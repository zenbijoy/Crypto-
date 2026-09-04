"""
Comprehensive Test Suite for CryptoScope AI Production MLOps Pipeline.
Phases 1-100 Architectural Verification.
"""
import pytest
import asyncio
from datetime import datetime, timezone

from core.events import CanonicalEvent, EventType
from services.event_bus import event_bus
from services.dlq import dlq_manager
from services.data_quality_gate import data_quality_gate, GateDecision
from feature_store.online.store import online_feature_store
from feature_store.offline.store import offline_feature_store
from feature_store.validation.parity import feature_parity_validator
from services.model_serving.model_cache import model_cache
from services.model_serving.router import model_router
from services.model_serving.challenger import challenger_framework
from services.model_serving.canary import canary_router
from services.model_serving.promotion import promotion_manager, LifecycleStage
from services.model_serving.rollback import rollback_manager
from services.observability.kill_switch import kill_switch
from services.observability.prediction_journal import prediction_journal
from services.observability.ood_detector import ood_detector
from services.observability.drift_and_expert_monitor import ensemble_diagnostics
from services.admin.config_manager import config_manager


@pytest.mark.asyncio
async def test_event_bus_and_dlq():
    await event_bus.initialize()
    ev = CanonicalEvent.create(
        event_type=EventType.TRADE,
        provider="BINANCE",
        symbol="BTCUSDT",
        event_time=datetime.now(timezone.utc),
        payload={"price": 67500.0, "qty": 0.5, "side": "BUY"}
    )
    res = await event_bus.publish("market:trade", ev)
    assert res is not None and len(res) > 0

    # DLQ capture test
    dlq_rec = dlq_manager.capture_failure(
        stream_name="market:trade",
        consumer="TEST_STAGE",
        original_payload=ev.model_dump(),
        error=ValueError("Simulated test corruption")
    )
    assert dlq_rec.consumer == "TEST_STAGE"
    assert dlq_rec.status == "PENDING"


def test_data_quality_gate():
    # Healthy features
    healthy_feats = {
        "spread_bps": 1.8,
        "microprice": 67500.0,
        "order_imbalance": 1.45,
        "realized_volatility_5m": 0.002,
        "funding_rate": 0.0001
    }
    avail = {k: True for k in healthy_feats}
    fresh = {k: 1.5 for k in healthy_feats}

    decision, reason, meta = data_quality_gate.check(
        features=healthy_feats,
        availability_mask=avail,
        freshness_mask=fresh,
        clock_skew_seconds=0.05,
        provider_healthy=True
    )
    assert decision == GateDecision.ALLOW

    # Stale critical feature
    fresh["spread_bps"] = 35.0  # max threshold is 5.0s
    decision, reason, meta = data_quality_gate.check(
        features=healthy_feats,
        availability_mask=avail,
        freshness_mask=fresh,
        clock_skew_seconds=0.05,
        provider_healthy=True
    )
    assert decision == GateDecision.REJECT


@pytest.mark.asyncio
async def test_feature_store_and_parity():
    await online_feature_store.initialize()
    now = datetime.now(timezone.utc)
    feats = {
        "order_imbalance": 1.25,
        "spread_bps": 2.1,
        "depth_imbalance_10bps": 0.08,
        "rv_5m": 0.0018,
        "cvd_quote": 150000.0,
        "funding_rate": 0.0001
    }
    await online_feature_store.put_feature_vector("BTCUSDT", "15m", feats, now)
    vals, mask, freshness = await online_feature_store.get_feature_vector("BTCUSDT", "15m")
    assert mask["order_imbalance"] is True
    assert vals["order_imbalance"] == 1.25

    # Parity check
    parity = await feature_parity_validator.verify_parity(
        symbol="BTCUSDT",
        horizon="15m",
        best_bid=67499.0,
        best_ask=67500.0,
        bid_vol_10bps=50.0,
        ask_vol_10bps=40.0,
        prices=[67495.0, 67498.0, 67500.0],
        taker_buys=[10.0],
        taker_sells=[5.0],
        funding_rate=0.0001,
        mark_price=67500.0,
        index_price=67500.0
    )
    assert parity["parity_passed"] is True


@pytest.mark.asyncio
async def test_model_serving_cache_and_swap():
    class MockModel:
        def predict_proba(self, X):
            return [[0.60, 0.20, 0.20]]

    # Register initial champion
    model_cache.register_model(
        asset="BTCUSDT",
        horizon="15m",
        version="CHAMP_V1",
        model_obj=MockModel(),
        metadata={"author": "quant"},
        is_champion=True
    )

    champ = model_cache.get_champion("BTCUSDT", "15m")
    assert champ is not None

    # Hot swap candidate
    success = await model_cache.atomic_swap_champion(
        asset="BTCUSDT",
        horizon="15m",
        new_version="TCN_V3_SWAP",
        candidate_model_obj=MockModel(),
        metadata={"author": "quant_team"}
    )
    assert success is True
    active = model_cache.get_champion("BTCUSDT", "15m")
    assert "TCN_V3_SWAP" in active.model_id


def test_promotion_policy_and_human_approval_gate():
    eval_res = promotion_manager.evaluate_candidate(
        metrics={"brier": 0.192, "mcc": 0.125, "ece": 0.045, "expectancy_bps": 4.2},
        shadow_days=4.5,
        sample_count=350
    )
    assert eval_res["eligible"] is True

    # Invariant: Automated promotion to PRODUCTION is strictly forbidden without Human Auditor ID
    with pytest.raises(PermissionError):
        promotion_manager.request_promotion(
            model_id="MOCK_MODEL_1",
            from_stage=LifecycleStage.PAPER,
            to_stage=LifecycleStage.PRODUCTION,
            evaluation=eval_res,
            approver="AUTO_SYSTEM_CRON"
        )

    # Valid human approval
    audit = promotion_manager.request_promotion(
        model_id="MOCK_MODEL_1",
        from_stage=LifecycleStage.PAPER,
        to_stage=LifecycleStage.PRODUCTION,
        evaluation=eval_res,
        approver="ChiefRiskOfficer_Elena",
        reason="Exceeds all benchmark gates for 4.5 shadow days"
    )
    assert audit["decision"] == "APPROVED"
    assert audit["approved_by"] == "ChiefRiskOfficer_Elena"


def test_prediction_journal_and_premature_resolution():
    entry = prediction_journal.log_prediction(
        prediction_id="pred_test_100",
        asset="BTCUSDT",
        horizon="15m",
        horizon_seconds=900,
        model_version="v2.0",
        feature_schema_version="v2.0",
        feature_snapshot_hash="abcd1234efgh5678",
        probabilities={"p_up": 0.65, "p_sideways": 0.15, "p_down": 0.20},
        forecast_return=0.0085,
        uncertainty_score=0.18,
        regime="TRENDING_BULL",
        signal="BUY",
        risk_decision="ALLOW",
        data_quality_status="FRESH"
    )
    assert entry.resolved is False

    # Invariant: Refuse premature label resolution before horizon expiration
    resolved = prediction_journal.resolve_label(
        prediction_id="pred_test_100",
        actual_return=0.0062,
        actual_high=67800.0,
        actual_low=67400.0,
        mfe=0.009,
        mae=0.001,
        current_time=datetime.now(timezone.utc)
    )
    assert resolved is False
    assert entry.resolved is False


def test_ood_and_killswitch():
    # OOD detection
    score, status, is_safe = ood_detector.calculate_ood_score([1.2, 67500.0, 0.05, 1.8, 250000.0, 0.0001])
    assert is_safe is True
    assert status == "NORMAL"

    # Extreme OOD event
    score_ood, status_ood, is_safe_ood = ood_detector.calculate_ood_score([99.0, 999999.0, 50.0, 80.0, 99999999.0, 0.5])
    assert is_safe_ood is False
    assert status_ood == "EXTREME_OOD"

    # Kill switch hierarchy
    allowed, _ = kill_switch.is_prediction_allowed("BTCUSDT", "15m")
    assert allowed is True

    kill_switch.set_global_prediction_kill(True, operator="SEC_ADMIN", reason="Emergency test")
    allowed_blocked, reason = kill_switch.is_prediction_allowed("BTCUSDT", "15m")
    assert allowed_blocked is False
    assert reason == "PREDICTIONS_DISABLED"

    # Reset
    kill_switch.set_global_prediction_kill(False, operator="SEC_ADMIN", reason="Test reset")
    allowed_restored, _ = kill_switch.is_prediction_allowed("BTCUSDT", "15m")
    assert allowed_restored is True
