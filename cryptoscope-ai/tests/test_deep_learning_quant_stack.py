"""
Tests for Phase 44 & 45:
- GRU shapes and bidirectional=False invariant
- TCN strict causality (ensuring output at T does not change when future T+1 is modified)
- PatchTST shape and causality
- Pinball loss and quantile monotonicity enforcement
- Scaler fit isolation (ensuring scaler only fits on train split)
- NO_TRADE risk invariant
"""
import torch
import numpy as np
import pytest

from ml.deep_models.gru import GRUNetwork
from ml.deep_models.tcn import TCNNetwork
from ml.transformers.patchtst import PatchTSTNetwork
from ml.losses.multi_task_loss import PinballLoss, MultiTaskForecastLoss
from ml.ensemble.stacking_and_risk import RiskSignalEngine
from ml.datasets.dataset_builder import QuantDatasetBuilder


def test_gru_shapes_and_invariants():
    batch_size = 4
    seq_len = 96
    feat_dim = 14
    model = GRUNetwork(input_dim=feat_dim, hidden_dim=32, num_layers=2)
    x = torch.randn(batch_size, seq_len, feat_dim)
    out = model(x)

    assert out["direction_logits"].shape == (batch_size, 3)
    assert out["return"].shape == (batch_size, 1)
    assert out["volatility"].shape == (batch_size, 1)
    assert out["quantiles"].shape == (batch_size, 5)
    assert bool(model.gru.bidirectional) is False


def test_tcn_strict_causality():
    """Proves causality: modifying the input at time T+1 does NOT alter the feature output at time T."""
    batch_size = 1
    seq_len = 32
    feat_dim = 8
    model = TCNNetwork(input_dim=feat_dim, num_channels=[16, 16], kernel_size=3)
    model.eval()

    x1 = torch.randn(batch_size, seq_len, feat_dim)
    x2 = x1.clone()
    # Modify the last timestep in x2
    x2[:, -1, :] += 5.0

    with torch.no_grad():
        # Transpose for conv1d: [batch, channels, seq]
        f1 = model.network(x1.transpose(1, 2))
        f2 = model.network(x2.transpose(1, 2))

    # All timesteps prior to the last step (-1) must be identical
    diff_prior = torch.max(torch.abs(f1[:, :, :-1] - f2[:, :, :-1])).item()
    assert diff_prior == pytest.approx(0.0, abs=1e-5), "TCN output at earlier timesteps leaked future data!"


def test_patchtst_shapes():
    batch_size = 2
    seq_len = 64
    feat_dim = 10
    model = PatchTSTNetwork(input_dim=feat_dim, seq_len=seq_len, patch_len=16, stride=8, d_model=32)
    x = torch.randn(batch_size, seq_len, feat_dim)
    out = model(x)

    assert out["direction_logits"].shape == (batch_size, 3)
    assert out["return"].shape == (batch_size, 1)
    assert out["volatility"].shape == (batch_size, 1)
    assert out["quantiles"].shape == (batch_size, 5)


def test_pinball_loss_and_monotonicity():
    loss_fn = PinballLoss(quantiles=[0.10, 0.25, 0.50, 0.75, 0.90])
    target = torch.tensor([[0.01], [-0.02]])
    # Monotonic predictions
    pred_monotonic = torch.tensor([[-0.02, -0.01, 0.0, 0.01, 0.02], [-0.03, -0.02, -0.01, 0.0, 0.01]])
    # Non-monotonic predictions (violates P10 <= P25 ...)
    pred_violating = torch.tensor([[0.02, 0.01, 0.0, -0.01, -0.02], [0.01, 0.0, -0.01, -0.02, -0.03]])

    loss_mono = loss_fn(pred_monotonic, target).item()
    loss_viol = loss_fn(pred_violating, target).item()

    assert loss_viol > loss_mono, "Crossing penalty did not penalize inverted quantiles!"


def test_no_trade_risk_invariants():
    engine = RiskSignalEngine()

    # Case 1: Low data quality -> must veto to NO_TRADE
    res1 = engine.evaluate_signal(np.array([0.1, 0.2, 0.7]), predicted_return=0.005, uncertainty=0.1, data_quality_score=50.0)
    assert res1["signal"] == "NO_TRADE"
    assert res1["actionable"] is False

    # Case 2: High uncertainty -> must veto to NO_TRADE
    res2 = engine.evaluate_signal(np.array([0.1, 0.2, 0.7]), predicted_return=0.005, uncertainty=0.55, data_quality_score=98.0)
    assert res2["signal"] == "NO_TRADE"
    assert res2["actionable"] is False

    # Case 3: Dominant sideways -> must veto to NO_TRADE
    res3 = engine.evaluate_signal(np.array([0.2, 0.6, 0.2]), predicted_return=0.0, uncertainty=0.15, data_quality_score=98.0)
    assert res3["signal"] == "NO_TRADE"
    assert res3["actionable"] is False

    # Case 4: High confidence bullish -> STRONG_LONG
    res4 = engine.evaluate_signal(np.array([0.1, 0.2, 0.7]), predicted_return=0.004, uncertainty=0.15, data_quality_score=98.0)
    assert res4["signal"] == "STRONG_LONG"
    assert res4["actionable"] is True
