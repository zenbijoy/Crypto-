"""
CryptoScope AI - Multi-Task PyTorch GRU Baseline
Architecture:
Input Projection -> Multi-layer Causal GRU (bidirectional=False) -> Dropout -> Pooling/Last State -> Shared Representation -> Multi-Task Heads:
  - Head A: 3-class Direction logits [batch_size, 3]
  - Head B: Future Return regression [batch_size, 1]
  - Head C: Future Volatility regression [batch_size, 1]
  - Head D: Future Return Quantiles [P10, P25, P50, P75, P90]
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, Optional
from ml.common.base_model import BaseTorchForecastModel


class GRUNetwork(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2,
        num_quantiles: int = 5
    ):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        self.activation = nn.GELU()

        # Bidirectional strictly FALSE to prevent lookahead in time-series
        self.gru = nn.GRU(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
            bidirectional=False
        )

        self.shared_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout)
        )

        # Multi-task heads
        self.direction_head = nn.Linear(hidden_dim, 3)  # [DOWN, SIDEWAYS, UP]
        self.return_head = nn.Linear(hidden_dim, 1)
        self.volatility_head = nn.Sequential(
            nn.Linear(hidden_dim, 1),
            nn.Softplus()  # Volatility must strictly be positive
        )
        self.quantile_head = nn.Linear(hidden_dim, num_quantiles)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        # x shape: [batch_size, seq_len, input_dim]
        projected = self.activation(self.input_proj(x))
        out, h_n = self.gru(projected)

        # Use last timestep representation (causal)
        last_step = out[:, -1, :]
        rep = self.shared_head(last_step)

        direction_logits = self.direction_head(rep)
        pred_return = self.return_head(rep)
        pred_volatility = self.volatility_head(rep)
        pred_quantiles = self.quantile_head(rep)

        return {
            "direction_logits": direction_logits,
            "return": pred_return,
            "volatility": pred_volatility,
            "quantiles": pred_quantiles
        }


class GRUForecastModel(BaseTorchForecastModel):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2,
        device: str = "cpu"
    ):
        super().__init__(device=device)
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout
        self.network = GRUNetwork(
            input_dim=input_dim,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            dropout=dropout
        ).to(device)

    def fit(self, X: Any, y: Any, val_data: Optional[Any] = None, **kwargs) -> Any:
        pass

    def predict(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        self.network.eval()
        with torch.no_grad():
            t_X = torch.tensor(X, dtype=torch.float32, device=self.device)
            out = self.network(t_X)
            logits = out["direction_logits"].cpu().numpy()
            probs = torch.softmax(out["direction_logits"], dim=-1).cpu().numpy()
            dir_preds = np.argmax(probs, axis=-1)
            returns = out["return"].squeeze(-1).cpu().numpy()
            vols = out["volatility"].squeeze(-1).cpu().numpy()
            quantiles = out["quantiles"].cpu().numpy()

            # Enforce monotonic quantile consistency: P10 <= P25 <= P50 <= P75 <= P90
            quantiles_sorted = np.sort(quantiles, axis=-1)

        return {
            "direction": dir_preds,
            "probabilities": probs,
            "return": returns,
            "volatility": vols,
            "quantiles": quantiles_sorted
        }

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.predict(X)["probabilities"]

    def save(self, filepath: str) -> None:
        torch.save({
            "state_dict": self.network.state_dict(),
            "config": {
                "input_dim": self.input_dim,
                "hidden_dim": self.hidden_dim,
                "num_layers": self.num_layers,
                "dropout": self.dropout
            }
        }, filepath)

    def load(self, filepath: str) -> None:
        checkpoint = torch.load(filepath, map_location=self.device)
        self.network.load_state_dict(checkpoint["state_dict"])

    def metadata(self) -> Dict[str, Any]:
        return {
            "model_type": "GRUForecastModel",
            "input_dim": self.input_dim,
            "hidden_dim": self.hidden_dim,
            "num_layers": self.num_layers,
            "dropout": self.dropout,
            "bidirectional": False
        }
