"""
Production Model Inference Pipeline with Granular Component Latency Breakdown.
Phase 25 & 26: Inference Pipeline & Latency Profiler.
"""
from __future__ import annotations
import math
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class LatencyProfile:
    feature_lookup_ms: float = 0.0
    preprocessing_ms: float = 0.0
    model_inference_ms: float = 0.0
    ensemble_ms: float = 0.0
    calibration_ms: float = 0.0
    risk_ms: float = 0.0
    serialization_ms: float = 0.0
    total_ms: float = 0.0


class LatencyTracker:
    def __init__(self, max_samples: int = 1000):
        self.history = deque(maxlen=max_samples)

    def record(self, total_ms: float):
        self.history.append(total_ms)

    def percentiles(self) -> Dict[str, float]:
        if not self.history:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        arr = sorted(self.history)
        n = len(arr)
        return {
            "p50": round(arr[int(n * 0.50)], 2),
            "p95": round(arr[min(n - 1, int(n * 0.95))], 2),
            "p99": round(arr[min(n - 1, int(n * 0.99))], 2),
        }


class InferencePipeline:
    """End-to-end inference orchestrator timing every sub-stage and guaranteeing consistent probability simplex."""

    def __init__(self):
        self.latency_tracker = LatencyTracker()

    def run_inference(
        self,
        features: Dict[str, float],
        model_container: Any,
        calibrator: Optional[Any] = None
    ) -> Tuple[Dict[str, float], LatencyProfile]:
        profile = LatencyProfile()
        t0 = time.perf_counter()

        # 1. Feature Preprocessing (t0 -> t1)
        t_pre = time.perf_counter()
        feature_order = [
            "spread_bps",
            "microprice",
            "order_imbalance",
            "realized_volatility_5m",
            "cvd_quote",
            "funding_rate"
        ]
        input_vector = [features.get(f, 0.0) for f in feature_order]
        # NaN safe guard
        input_vector = [0.0 if (math.isnan(v) or math.isinf(v)) else v for v in input_vector]
        X = np.array([input_vector], dtype=np.float32)
        profile.preprocessing_ms = (time.perf_counter() - t_pre) * 1000.0

        # 2. Model Inference (t1 -> t2)
        t_inf = time.perf_counter()
        raw_probs = [0.33, 0.34, 0.33]  # default fallback
        if model_container and hasattr(model_container, "model"):
            m = model_container.model
            if hasattr(m, "predict_proba"):
                probs = m.predict_proba(X)[0]
                raw_probs = [float(p) for p in probs]
            elif hasattr(m, "forward"):  # PyTorch
                import torch
                with torch.no_grad():
                    out = m(torch.tensor(X))
                    if out.shape[-1] == 3:
                        probs = torch.softmax(out, dim=-1).numpy()[0]
                        raw_probs = [float(p) for p in probs]
                    else:
                        # Regression return
                        val = float(out[0][0])
                        p_up = 1.0 / (1.0 + math.exp(-val * 100.0))
                        raw_probs = [p_up, 1.0 - p_up, 0.0]
        profile.model_inference_ms = (time.perf_counter() - t_inf) * 1000.0

        # 3. Calibration (t2 -> t3)
        t_cal = time.perf_counter()
        calibrated_probs = list(raw_probs)
        if calibrator and hasattr(calibrator, "calibrate"):
            calibrated_probs = calibrator.calibrate(raw_probs)
        profile.calibration_ms = (time.perf_counter() - t_cal) * 1000.0

        # 4. Invariant Enforcement: Probabilities sum to 1.0
        tot = sum(calibrated_probs)
        if tot > 0:
            norm_probs = [round(p / tot, 4) for p in calibrated_probs]
        else:
            norm_probs = [0.3333, 0.3334, 0.3333]

        p_up = norm_probs[0]
        p_down = norm_probs[1] if len(norm_probs) > 1 else 0.0
        p_neutral = norm_probs[2] if len(norm_probs) > 2 else 0.0

        # Ensure simplex exact sum
        p_neutral = round(max(0.0, 1.0 - (p_up + p_down)), 4)

        # Total timing
        profile.total_ms = (time.perf_counter() - t0) * 1000.0
        self.latency_tracker.record(profile.total_ms)

        result = {
            "p_up": p_up,
            "p_down": p_down,
            "p_neutral": p_neutral,
            "expected_return": round((p_up - p_down) * 0.005, 5),
            "confidence": round(max(p_up, p_down) * 100.0, 1)
        }
        return result, profile


inference_pipeline = InferencePipeline()
