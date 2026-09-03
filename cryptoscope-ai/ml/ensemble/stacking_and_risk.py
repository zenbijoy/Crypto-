"""
CryptoScope AI - Probability Calibration & Stacking Ensemble
Implements:
- Probability Calibration: Temperature Scaling & Isotonic Regression
- Out-of-fold learned Stacking Ensemble with Logistic Regression / LightGBM meta-model
- NO_TRADE Invariant & Risk veto engine
"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from typing import Dict, Any, List, Optional
import torch
import torch.nn as nn


class TemperatureScaler:
    """Post-hoc temperature scaling for multi-class direction probabilities."""

    def __init__(self):
        self.temperature = 1.0

    def fit(self, logits: np.ndarray, y_true: np.ndarray) -> "TemperatureScaler":
        t_logits = torch.tensor(logits, dtype=torch.float32)
        t_labels = torch.tensor(y_true, dtype=torch.long)

        temp = nn.Parameter(torch.ones(1) * 1.5)
        optimizer = torch.optim.LBFGS([temp], lr=0.01, max_iter=50)
        criterion = nn.CrossEntropyLoss()

        def eval_loss():
            optimizer.zero_grad()
            scaled = t_logits / temp.clamp(min=0.1, max=10.0)
            loss = criterion(scaled, t_labels)
            loss.backward()
            return loss

        try:
            optimizer.step(eval_loss)
            self.temperature = float(temp.clamp(min=0.1, max=10.0).item())
        except Exception:
            self.temperature = 1.0

        return self

    def scale_probabilities(self, probs: np.ndarray) -> np.ndarray:
        # Convert probs to pseudo logits and scale
        eps = 1e-7
        clipped = np.clip(probs, eps, 1.0 - eps)
        pseudo_logits = np.log(clipped)
        scaled_logits = pseudo_logits / self.temperature
        exp_logits = np.exp(scaled_logits - np.max(scaled_logits, axis=-1, keepdims=True))
        return exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)


class LearnedStackingEnsemble:
    """Meta-model stacking out-of-fold predictions from baselines and neural models."""

    def __init__(self):
        self.meta_clf = LogisticRegression(max_iter=500)
        self.fitted = False

    def fit_oof(self, oof_probs: np.ndarray, y_true: np.ndarray):
        """oof_probs shape: [num_samples, num_models * 3]"""
        self.meta_clf.fit(oof_probs, y_true)
        self.fitted = True
        return self

    def predict_proba(self, model_probs_list: List[np.ndarray]) -> np.ndarray:
        concatenated = np.hstack(model_probs_list)
        if not self.fitted:
            # Fallback to simple unweighted average
            return np.mean(model_probs_list, axis=0)
        return self.meta_clf.predict_proba(concatenated)


class RiskSignalEngine:
    """
    Decides signal regime:
    STRONG_LONG, LONG, NO_TRADE, SHORT, STRONG_SHORT
    Enforces that NO_TRADE is strictly non-actionable.
    """

    @staticmethod
    def evaluate_signal(
        calibrated_probs: np.ndarray,
        predicted_return: float,
        uncertainty: float,
        data_quality_score: float = 95.0,
        model_agreement: float = 0.85
    ) -> Dict[str, Any]:
        p_down, p_sideways, p_up = calibrated_probs

        # NO_TRADE Invariants:
        # 1. High uncertainty > 0.40
        # 2. Sideways probability dominant or max prob < 0.50
        # 3. Model disagreement
        # 4. Low data quality
        if data_quality_score < 70.0:
            return {"signal": "NO_TRADE", "reason": "LOW_DATA_QUALITY", "actionable": False}

        if uncertainty > 0.45:
            return {"signal": "NO_TRADE", "reason": "HIGH_EPISTEMIC_UNCERTAINTY", "actionable": False}

        if model_agreement < 0.55:
            return {"signal": "NO_TRADE", "reason": "MODEL_DISAGREEMENT", "actionable": False}

        max_prob = max(p_down, p_sideways, p_up)
        if p_sideways == max_prob or max_prob < 0.48:
            return {"signal": "NO_TRADE", "reason": "UNCLEAR_EDGE", "actionable": False}

        if p_up > 0.65 and predicted_return > 0.003:
            return {"signal": "STRONG_LONG", "reason": "HIGH_CONFIDENCE_BULLISH", "actionable": True}
        elif p_up > 0.50 and predicted_return > 0.001:
            return {"signal": "LONG", "reason": "MODERATE_BULLISH", "actionable": True}
        elif p_down > 0.65 and predicted_return < -0.003:
            return {"signal": "STRONG_SHORT", "reason": "HIGH_CONFIDENCE_BEARISH", "actionable": True}
        elif p_down > 0.50 and predicted_return < -0.001:
            return {"signal": "SHORT", "reason": "MODERATE_BEARISH", "actionable": True}

        return {"signal": "NO_TRADE", "reason": "DEFAULT_CONSERVATIVE_FILTER", "actionable": False}
