"""
CryptoScope AI - Base Forecast Model Interfaces
Provides standard interfaces for all quantitative & deep learning forecasting models.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import numpy as np


class BaseForecastModel(ABC):
    """Common interface for all ML/DL forecasting models in CryptoScope AI."""

    @abstractmethod
    def fit(self, X: Any, y: Any, val_data: Optional[Tuple[Any, Any]] = None, **kwargs) -> Any:
        """Fit model strictly on training data."""
        pass

    @abstractmethod
    def predict(self, X: Any) -> Dict[str, np.ndarray]:
        """
        Generate multi-task predictions:
        Returns dictionary with:
          - 'direction': class index (0: DOWN, 1: SIDEWAYS, 2: UP)
          - 'return': predicted future log return
          - 'volatility': predicted future realized volatility
          - 'quantiles': predicted return quantiles [P10, P25, P50, P75, P90]
        """
        pass

    @abstractmethod
    def predict_proba(self, X: Any) -> np.ndarray:
        """Return calibrated class probabilities for direction [P(DOWN), P(SIDEWAYS), P(UP)]."""
        pass

    @abstractmethod
    def save(self, filepath: str) -> None:
        """Persist model weights and metadata."""
        pass

    @abstractmethod
    def load(self, filepath: str) -> None:
        """Load model weights and metadata."""
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Return model metadata, config, architecture, and feature schema."""
        pass

    def validate_input_schema(self, X: Any, expected_features: List[str]) -> bool:
        """Verify that input feature columns match expected schema."""
        if hasattr(X, "columns"):
            cols = list(X.columns)
            missing = [f for f in expected_features if f not in cols]
            if missing:
                raise ValueError(f"Input schema missing required features: {missing}")
        return True


class BaseTorchForecastModel(BaseForecastModel):
    """Base interface specialized for PyTorch neural models."""

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.network = None

    def to_device(self, device: str):
        self.device = device
        if self.network is not None:
            self.network.to(device)
        return self
