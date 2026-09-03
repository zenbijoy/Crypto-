"""
Unit Tests for Deep Learning & Multi-Expert Ensemble Architecture
Verifies:
1. Multi-horizon log-return & triple barrier labeling
2. Layer 1-5 Specialists & Layer 6 Meta-Ensemble
3. Probability Calibration (ECE, Brier Score, Platt Scaling)
4. Layer 8 Abstention Engine (NO_SIGNAL policy)
5. Drift Detector (PSI) & Champion/Challenger Model Registry
"""
import unittest
from ml.labeling.triple_barrier import triple_barrier_labeler
from ml.models.tabular_expert import tabular_expert
from ml.models.orderflow_tcn import orderflow_tcn_expert
from ml.models.temporal_tft import temporal_transformer_expert
from ml.models.derivatives_expert import derivatives_expert
from ml.models.context_expert import context_expert
from ml.models.meta_ensemble import meta_ensemble_engine
from ml.calibration.calibrator import probability_calibrator
from services.abstention import abstention_engine
from services.drift_detector import drift_detector
from services.model_registry import model_registry
from services.feature_engine import feature_engine

class TestDeepLearningArchitecture(unittest.TestCase):
    def test_triple_barrier_labeling(self):
        prices = [100.0, 101.5, 102.8, 103.5, 104.2, 103.8, 102.5, 101.0, 99.5, 98.0, 97.2, 98.5, 100.0, 102.0, 105.0]
        vols = [0.015] * len(prices)
        
        labels = triple_barrier_labeler.generate_triple_barrier_labels(prices, vols, horizon_steps=5)
        self.assertGreater(len(labels), 0)
        for sample in labels:
            self.assertIn(sample["label"], [1, 0, -1])
            self.assertIn(sample["barrier_hit"], ["UPPER", "LOWER", "TIME_EXPIRY"])

    def test_specialist_models_and_meta_ensemble(self):
        sample_candles = [
            {"close": 67000.0 + i * 5.0, "high": 67050.0 + i * 5.0, "low": 66950.0 + i * 5.0, "volume_base": 100.0}
            for i in range(30)
        ]
        f_vec = feature_engine.compute_all_features("BTC", sample_candles)
        
        p_tab = tabular_expert.predict(f_vec)
        p_flow = orderflow_tcn_expert.predict(f_vec)
        p_temp = temporal_transformer_expert.predict(f_vec, horizon="1h")
        p_deriv = derivatives_expert.predict(f_vec)
        p_ctx = context_expert.predict(f_vec)

        for res in [p_tab, p_flow, p_temp, p_deriv, p_ctx]:
            probs = res["probabilities"]
            self.assertAlmostEqual(probs["up"] + probs["neutral"] + probs["down"], 1.0, places=2)

        # Test Meta Ensemble
        ensemble = meta_ensemble_engine.predict_ensemble(f_vec, horizon="1h")
        self.assertIn("ensemble_probabilities", ensemble)
        self.assertGreaterEqual(ensemble["model_agreement"], 0.0)
        self.assertLessEqual(ensemble["model_agreement"], 1.0)
        self.assertIn("price_quantiles", ensemble)
        q = ensemble["price_quantiles"]
        self.assertTrue(q["p10"] <= q["p25"] <= q["p50"] <= q["p75"] <= q["p90"])

    def test_probability_calibrator(self):
        raw = {"up": 0.85, "neutral": 0.10, "down": 0.05}
        calibrated = probability_calibrator.calibrate_probabilities(raw)
        self.assertAlmostEqual(calibrated["up"] + calibrated["neutral"] + calibrated["down"], 1.0, places=2)
        # Scaled probability is smoothed to prevent extreme overconfidence
        self.assertLess(calibrated["up"], 0.85)

        # Test ECE & Brier score
        preds = [0.8, 0.7, 0.2, 0.1]
        actuals = [1, 1, 0, 0]
        brier = probability_calibrator.compute_brier_score(preds, actuals)
        self.assertLess(brier, 0.15)
        ece = probability_calibrator.compute_ece(preds, actuals)
        self.assertLessEqual(ece, 0.25)

    def test_abstention_engine_rules(self):
        # High confidence, high agreement, good data quality -> ALLOW
        good_eval = abstention_engine.evaluate_signal(
            calibrated_probs={"up": 0.78, "neutral": 0.12, "down": 0.10},
            model_agreement=0.88,
            data_quality_score=98
        )
        self.assertFalse(good_eval["abstention_active"])
        self.assertTrue(good_eval["actionable"])
        self.assertEqual(good_eval["signal"], "STRONG LONG")

        # Low confidence -> ABSTAIN
        low_conf_eval = abstention_engine.evaluate_signal(
            calibrated_probs={"up": 0.40, "neutral": 0.35, "down": 0.25},
            model_agreement=0.88,
            data_quality_score=98
        )
        self.assertTrue(low_conf_eval["abstention_active"])
        self.assertEqual(low_conf_eval["signal"], "NEUTRAL / NO-TRADE")

        # Poor data quality -> ABSTAIN & REJECT
        bad_data_eval = abstention_engine.evaluate_signal(
            calibrated_probs={"up": 0.78, "neutral": 0.12, "down": 0.10},
            model_agreement=0.88,
            data_quality_score=70
        )
        self.assertTrue(bad_data_eval["abstention_active"])
        self.assertEqual(bad_data_eval["risk_decision"], "REJECT")

    def test_drift_detector_and_model_registry(self):
        # Baseline vs live features
        baseline = [10.0, 10.5, 11.0, 10.2, 9.8, 10.1, 10.4]
        live_healthy = [10.1, 10.4, 10.9, 10.3, 9.9, 10.0, 10.5]
        drift_res = drift_detector.evaluate_feature_drift(baseline, live_healthy)
        self.assertEqual(drift_res["status"], "HEALTHY")

        # Model Registry
        models = model_registry.list_models()
        self.assertGreaterEqual(len(models), 3)
        champ = model_registry.get_champion()
        self.assertIsNotNone(champ)
        self.assertEqual(champ["status"], "CHAMPION")

if __name__ == "__main__":
    unittest.main()
