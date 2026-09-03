"""
CryptoScope AI - Multi-Task Genuine Causal Temporal Convolutional Network (TCN)
Architecture:
- Causal 1D Dilated Convolutions (left-padding only: (kernel_size - 1) * dilation)
- Exponential Dilation Schedule: 1, 2, 4, 8, 16, 32
- Residual Connections with 1x1 Conv when channel dimensions mismatch
- Weight Normalization and Dropout
- Multi-Task Heads (Direction, Return, Volatility, Quantiles)
- Strict Causality Invariant: Output at step T does NOT consume step T+1.
"""
import torch
import torch.nn as nn
from torch.nn.utils.parametrizations import weight_norm
import numpy as np
from typing import Dict, Any, List, Optional
from ml.common.base_model import BaseTorchForecastModel


class CausalConv1dBlock(nn.Module):
    """Single Causal Dilated Residual Block."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        dilation: int,
        dropout: float = 0.2
    ):
        super().__init__()
        self.causal_padding = (kernel_size - 1) * dilation

        self.conv1 = weight_norm(nn.Conv1d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            dilation=dilation
        ))
        self.act1 = nn.GELU()
        self.drop1 = nn.Dropout(dropout)

        self.conv2 = weight_norm(nn.Conv1d(
            out_channels,
            out_channels,
            kernel_size=kernel_size,
            dilation=dilation
        ))
        self.act2 = nn.GELU()
        self.drop2 = nn.Dropout(dropout)

        self.downsample = nn.Conv1d(in_channels, out_channels, 1) if in_channels != out_channels else None
        self.final_act = nn.GELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: [batch, channels, seq_len]
        # Pad only on the left to strictly enforce temporal causality
        padded1 = nn.functional.pad(x, (self.causal_padding, 0))
        out = self.drop1(self.act1(self.conv1(padded1)))

        padded2 = nn.functional.pad(out, (self.causal_padding, 0))
        out = self.drop2(self.act2(self.conv2(padded2)))

        res = x if self.downsample is None else self.downsample(x)
        return self.final_act(out + res)


class TCNNetwork(nn.Module):
    def __init__(
        self,
        input_dim: int,
        num_channels: List[int] = [64, 64, 128, 128],
        kernel_size: int = 3,
        dropout: float = 0.2,
        num_quantiles: int = 5
    ):
        super().__init__()
        layers = []
        in_ch = input_dim
        for i, out_ch in enumerate(num_channels):
            dilation = 2 ** i
            layers.append(CausalConv1dBlock(
                in_channels=in_ch,
                out_channels=out_ch,
                kernel_size=kernel_size,
                dilation=dilation,
                dropout=dropout
            ))
            in_ch = out_ch

        self.network = nn.Sequential(*layers)
        final_ch = num_channels[-1]

        self.shared_head = nn.Sequential(
            nn.Linear(final_ch, final_ch),
            nn.LayerNorm(final_ch),
            nn.GELU(),
            nn.Dropout(dropout)
        )

        self.direction_head = nn.Linear(final_ch, 3)
        self.return_head = nn.Linear(final_ch, 1)
        self.volatility_head = nn.Sequential(
            nn.Linear(final_ch, 1),
            nn.Softplus()
        )
        self.quantile_head = nn.Linear(final_ch, num_quantiles)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        # Input x: [batch_size, seq_len, input_dim] -> transpose for Conv1d: [batch_size, input_dim, seq_len]
        x_transposed = x.transpose(1, 2)
        feats = self.network(x_transposed)

        # Causal output at step T is at index -1
        last_timestep = feats[:, :, -1]
        rep = self.shared_head(last_timestep)

        return {
            "direction_logits": self.direction_head(rep),
            "return": self.return_head(rep),
            "volatility": self.volatility_head(rep),
            "quantiles": self.quantile_head(rep)
        }


class TCNForecastModel(BaseTorchForecastModel):
    def __init__(
        self,
        input_dim: int,
        num_channels: List[int] = [64, 64, 128, 128],
        kernel_size: int = 3,
        dropout: float = 0.2,
        device: str = "cpu"
    ):
        super().__init__(device=device)
        self.input_dim = input_dim
        self.num_channels = num_channels
        self.kernel_size = kernel_size
        self.dropout = dropout
        self.network = TCNNetwork(
            input_dim=input_dim,
            num_channels=num_channels,
            kernel_size=kernel_size,
            dropout=dropout
        ).to(device)

    def fit(self, X: Any, y: Any, val_data: Optional[Any] = None, **kwargs) -> Any:
        pass

    def predict(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        self.network.eval()
        with torch.no_grad():
            t_X = torch.tensor(X, dtype=torch.float32, device=self.device)
            out = self.network(t_X)
            probs = torch.softmax(out["direction_logits"], dim=-1).cpu().numpy()
            dir_preds = np.argmax(probs, axis=-1)
            returns = out["return"].squeeze(-1).cpu().numpy()
            vols = out["volatility"].squeeze(-1).cpu().numpy()
            quantiles = out["quantiles"].cpu().numpy()
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
                "num_channels": self.num_channels,
                "kernel_size": self.kernel_size,
                "dropout": self.dropout
            }
        }, filepath)

    def load(self, filepath: str) -> None:
        checkpoint = torch.load(filepath, map_location=self.device)
        self.network.load_state_dict(checkpoint["state_dict"])

    def metadata(self) -> Dict[str, Any]:
        return {
            "model_type": "TCNForecastModel",
            "input_dim": self.input_dim,
            "num_channels": self.num_channels,
            "kernel_size": self.kernel_size,
            "dropout": self.dropout,
            "causal": True
        }
