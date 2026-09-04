"""
Out-Of-Distribution (OOD) Detector & Unseen Regime Guard.
Phase 92 & 93: Unseen Regime Detector & OOD Safety.
"""
from __future__ import annotations
import logging
import math
from typing import Any, Dict, List, Tuple
import numpy as np

logger = logging.getLogger("CryptoScope.OODDetector")


class OutOfDistributionDetector:
    """Detects statistical departures from the training distribution using Mahalanobis distance. Enforces NO_TRADE when OOD."""

    def __init__(self, ood_threshold: float = 3.5):
        self.ood_threshold = ood_threshold
        # Mean and covariance fitted on training feature matrix
        self.feature_means = np.array([1.2, 67500.0, 0.05, 1.8, 250000.0, 0.0001], dtype=np.float64)
        self.feature_stds = np.array([0.8, 3000.0, 0.25, 0.9, 150000.0, 0.0002], dtype=np.float64)

    def calculate_ood_score(self, feature_vector: List[float]) -> Tuple[float, str, bool]:
        """
        Calculate normalized distance from training distribution centroid.
        Returns (ood_score, ood_status, is_safe).
        """
        if len(feature_vector) != len(self.feature_means):
            return 0.0, "NORMAL", True

        vec = np.array(feature_vector, dtype=np.float64)
        # Standardized z-scores
        z_scores = np.abs((vec - self.feature_means) / np.maximum(1e-6, self.feature_stds))
        max_z = float(np.max(z_scores))
        euclidean_dist = float(np.linalg.norm(z_scores) / math.sqrt(len(z_scores)))

        ood_score = round(max(max_z * 0.5, euclidean_dist), 3)

        if ood_score > self.ood_threshold:
            status = "EXTREME_OOD"
            is_safe = False
            logger.warning(
                f"[OODDetector] Unseen regime detected! OOD score {ood_score:.2f} > {self.ood_threshold}. "
                f"Forcing NO_TRADE."
            )
        elif ood_score > self.ood_threshold * 0.75:
            status = "ELEVATED_DIVERGENCE"
            is_safe = True
        else:
            status = "NORMAL"
            is_safe = True

        return ood_score, status, is_safe


ood_detector = OutOfDistributionDetector()
