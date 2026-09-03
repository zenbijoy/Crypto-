"""
CryptoScope AI - Leakage-Free Incremental Scaler
Implements Section 26 & 27:
Global scalers must NOT be fitted using future data.
Fit scalers strictly on historical training windows only.
"""
from typing import List
import statistics
import math

class LeakageFreeScaler:
    def __init__(self):
        self.mean: float = 0.0
        self.std: float = 1.0
        self.is_fitted: bool = False

    def fit(self, historical_values: List[float]):
        """Fits mean and std using only historical window observations (T_available <= T_now)"""
        if not historical_values:
            self.mean = 0.0
            self.std = 1.0
            self.is_fitted = True
            return
        self.mean = float(statistics.mean(historical_values))
        if len(historical_values) > 1:
            stdev = statistics.stdev(historical_values)
            self.std = float(max(1e-8, stdev))
        else:
            self.std = 1.0
        self.is_fitted = True

    def transform(self, values: List[float]) -> List[float]:
        if not self.is_fitted:
            raise RuntimeError("Scaler must be fitted on historical data before transforming.")
        return [(v - self.mean) / self.std for v in values]

    def fit_transform(self, historical_values: List[float]) -> List[float]:
        self.fit(historical_values)
        return self.transform(historical_values)
