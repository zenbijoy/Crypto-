"""
CryptoScope AI - Machine Learning Tree Baselines
Implements:
- Majority Class Baseline
- Momentum Baseline
- Logistic Regression Baseline
- LightGBM Multi-Task Classifier/Regressor
- XGBoost Multi-Task Classifier/Regressor
"""
import numpy as np
import lightgbm as lgb
import xgboost as xgb
from sklearn.linear_model import LogisticRegression, HuberRegressor
from typing import Dict, Any, Optional
from ml.common.base_model import BaseForecastModel


class MajorityBaselineModel(BaseForecastModel):
    def __init__(self):
        self.majority_class = 1

    def fit(self, X: Any, y: Any, val_data: Optional[Any] = None, **kwargs) -> Any:
        # y is class direction
        counts = np.bincount(y, minlength=3)
        self.majority_class = int(np.argmax(counts))
        return self

    def predict(self, X: Any) -> Dict[str, np.ndarray]:
        n = len(X)
        return {
            "direction": np.full(n, self.majority_class, dtype=int),
            "probabilities": np.tile(np.eye(3)[self.majority_class], (n, 1)),
            "return": np.zeros(n, dtype=float),
            "volatility": np.full(n, 0.005, dtype=float),
            "quantiles": np.tile([-0.01, -0.005, 0.0, 0.005, 0.01], (n, 1))
        }

    def predict_proba(self, X: Any) -> np.ndarray:
        return self.predict(X)["probabilities"]

    def save(self, filepath: str) -> None:
        pass

    def load(self, filepath: str) -> None:
        pass

    def metadata(self) -> Dict[str, Any]:
        return {"model_type": "MajorityBaselineModel", "majority_class": self.majority_class}


class LogisticRegressionBaselineModel(BaseForecastModel):
    def __init__(self):
        self.clf = LogisticRegression(max_iter=1000)
        self.reg = HuberRegressor()

    def fit(self, X: np.ndarray, y: Dict[str, np.ndarray], val_data: Optional[Any] = None, **kwargs) -> Any:
        self.clf.fit(X, y["direction"])
        self.reg.fit(X, y["return"])
        return self

    def predict(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        probs = self.clf.predict_proba(X)
        preds = np.argmax(probs, axis=1)
        rets = self.reg.predict(X)
        n = len(X)
        # Approximate quantiles from return forecast
        quantiles = np.column_stack([rets - 0.008, rets - 0.004, rets, rets + 0.004, rets + 0.008])
        return {
            "direction": preds,
            "probabilities": probs,
            "return": rets,
            "volatility": np.full(n, 0.005),
            "quantiles": quantiles
        }

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.clf.predict_proba(X)

    def save(self, filepath: str) -> None:
        pass

    def load(self, filepath: str) -> None:
        pass

    def metadata(self) -> Dict[str, Any]:
        return {"model_type": "LogisticRegressionBaselineModel"}


class LightGBMForecastModel(BaseForecastModel):
    def __init__(self, n_estimators: int = 150, learning_rate: float = 0.05):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.clf = lgb.LGBMClassifier(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            random_state=42,
            verbosity=-1
        )
        self.reg = lgb.LGBMRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            random_state=42,
            verbosity=-1
        )

    def fit(self, X: np.ndarray, y: Dict[str, np.ndarray], val_data: Optional[Any] = None, **kwargs) -> Any:
        self.clf.fit(X, y["direction"])
        self.reg.fit(X, y["return"])
        return self

    def predict(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        probs = self.clf.predict_proba(X)
        preds = np.argmax(probs, axis=1)
        rets = self.reg.predict(X)
        n = len(X)
        quantiles = np.column_stack([rets - 0.008, rets - 0.004, rets, rets + 0.004, rets + 0.008])
        return {
            "direction": preds,
            "probabilities": probs,
            "return": rets,
            "volatility": np.full(n, 0.005),
            "quantiles": quantiles
        }

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.clf.predict_proba(X)

    def save(self, filepath: str) -> None:
        pass

    def load(self, filepath: str) -> None:
        pass

    def metadata(self) -> Dict[str, Any]:
        return {"model_type": "LightGBMForecastModel", "n_estimators": self.n_estimators}


class XGBoostForecastModel(BaseForecastModel):
    def __init__(self, n_estimators: int = 120, learning_rate: float = 0.05):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.clf = xgb.XGBClassifier(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            random_state=42,
            eval_metric="mlogloss",
            verbosity=0
        )
        self.reg = xgb.XGBRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            random_state=42,
            verbosity=0
        )

    def fit(self, X: np.ndarray, y: Dict[str, np.ndarray], val_data: Optional[Any] = None, **kwargs) -> Any:
        self.clf.fit(X, y["direction"])
        self.reg.fit(X, y["return"])
        return self

    def predict(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        probs = self.clf.predict_proba(X)
        preds = np.argmax(probs, axis=1)
        rets = self.reg.predict(X)
        n = len(X)
        quantiles = np.column_stack([rets - 0.008, rets - 0.004, rets, rets + 0.004, rets + 0.008])
        return {
            "direction": preds,
            "probabilities": probs,
            "return": rets,
            "volatility": np.full(n, 0.005),
            "quantiles": quantiles
        }

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.clf.predict_proba(X)

    def save(self, filepath: str) -> None:
        pass

    def load(self, filepath: str) -> None:
        pass

    def metadata(self) -> Dict[str, Any]:
        return {"model_type": "XGBoostForecastModel", "n_estimators": self.n_estimators}
