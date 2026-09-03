"""
CryptoScope AI - Genuine PatchTST-Style Forecasting Architecture
Implements:
- Patch Extraction across temporal sequence
- Linear Patch Embedding + 1D Learnable Positional Encoding
- PyTorch TransformerEncoder with Multi-Head Self-Attention & Causal Masking
- Residual connections, LayerNorm, Dropout
- Multi-task heads (Direction, Return, Volatility, Quantiles)
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, Optional
from ml.common.base_model import BaseTorchForecastModel


class PatchTSTNetwork(nn.Module):
    def __init__(
        self,
        input_dim: int,
        seq_len: int = 96,
        patch_len: int = 16,
        stride: int = 8,
        d_model: int = 64,
        n_heads: int = 4,
        n_layers: int = 2,
        ff_dim: int = 128,
        dropout: float = 0.1,
        num_quantiles: int = 5
    ):
        super().__init__()
        self.patch_len = patch_len
        self.stride = stride
        self.num_patches = (seq_len - patch_len) // stride + 1

        # Patch projection: maps flattened patch across all features to d_model
        patch_dim = patch_len * input_dim
        self.patch_proj = nn.Linear(patch_dim, d_model)
        self.pos_embedding = nn.Parameter(torch.randn(1, self.num_patches, d_model) * 0.02)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=ff_dim,
            dropout=dropout,
            activation="gelu",
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)

        self.shared_head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.LayerNorm(d_model),
            nn.GELU(),
            nn.Dropout(dropout)
        )

        self.direction_head = nn.Linear(d_model, 3)
        self.return_head = nn.Linear(d_model, 1)
        self.volatility_head = nn.Sequential(
            nn.Linear(d_model, 1),
            nn.Softplus()
        )
        self.quantile_head = nn.Linear(d_model, num_quantiles)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        # x shape: [batch_size, seq_len, input_dim]
        batch_size, seq_len, input_dim = x.shape

        # Extract patches
        patches = []
        for i in range(self.num_patches):
            start = i * self.stride
            end = start + self.patch_len
            patch = x[:, start:end, :].reshape(batch_size, -1)
            patches.append(patch)

        # [batch_size, num_patches, patch_dim]
        patch_tensor = torch.stack(patches, dim=1)
        embedded = self.patch_proj(patch_tensor) + self.pos_embedding

        # Generate causal mask so patch i only attends to patches <= i
        causal_mask = nn.Transformer.generate_square_subsequent_mask(self.num_patches).to(x.device)

        encoded = self.transformer_encoder(embedded, mask=causal_mask)
        last_patch_repr = encoded[:, -1, :]
        rep = self.shared_head(last_patch_repr)

        return {
            "direction_logits": self.direction_head(rep),
            "return": self.return_head(rep),
            "volatility": self.volatility_head(rep),
            "quantiles": self.quantile_head(rep)
        }


class PatchTSTForecastModel(BaseTorchForecastModel):
    def __init__(
        self,
        input_dim: int,
        seq_len: int = 96,
        patch_len: int = 16,
        stride: int = 8,
        d_model: int = 64,
        n_heads: int = 4,
        n_layers: int = 2,
        ff_dim: int = 128,
        dropout: float = 0.1,
        device: str = "cpu"
    ):
        super().__init__(device=device)
        self.input_dim = input_dim
        self.seq_len = seq_len
        self.patch_len = patch_len
        self.stride = stride
        self.d_model = d_model
        self.network = PatchTSTNetwork(
            input_dim=input_dim,
            seq_len=seq_len,
            patch_len=patch_len,
            stride=stride,
            d_model=d_model,
            n_heads=n_heads,
            n_layers=n_layers,
            ff_dim=ff_dim,
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
                "seq_len": self.seq_len,
                "patch_len": self.patch_len,
                "stride": self.stride,
                "d_model": self.d_model
            }
        }, filepath)

    def load(self, filepath: str) -> None:
        checkpoint = torch.load(filepath, map_location=self.device)
        self.network.load_state_dict(checkpoint["state_dict"])

    def metadata(self) -> Dict[str, Any]:
        return {
            "model_type": "PatchTSTForecastModel",
            "input_dim": self.input_dim,
            "seq_len": self.seq_len,
            "patch_len": self.patch_len,
            "stride": self.stride,
            "d_model": self.d_model
        }
