"""
CryptoScope AI - Multi-Task Loss Functions
Implements:
- Direction: CrossEntropyLoss
- Return: HuberLoss
- Volatility: HuberLoss (log-volatility)
- Quantiles: Pinball / Quantile Loss with Monotonicity Penalty
- Combined Multi-Task Loss with configurable lambda weights
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional


class PinballLoss(nn.Module):
    """Pinball / Quantile Loss for asymmetric quantile regression."""

    def __init__(self, quantiles: Optional[List[float]] = None):
        super().__init__()
        self.quantiles = quantiles or [0.10, 0.25, 0.50, 0.75, 0.90]

    def forward(self, pred_quantiles: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        pred_quantiles: [batch_size, num_quantiles]
        target: [batch_size] or [batch_size, 1]
        """
        if target.dim() == 1:
            target = target.unsqueeze(-1)
        
        losses = []
        for i, q in enumerate(self.quantiles):
            error = target - pred_quantiles[:, i:i+1]
            loss_q = torch.max((q - 1) * error, q * error)
            losses.append(loss_q.mean())
            
        pinball_loss = torch.stack(losses).mean()

        # Enforce monotonicity: P10 <= P25 <= P50 <= P75 <= P90
        # Penalize negative diffs between adjacent quantiles
        diffs = pred_quantiles[:, 1:] - pred_quantiles[:, :-1]
        crossing_penalty = torch.relu(-diffs).pow(2).mean() * 10.0

        return pinball_loss + crossing_penalty


class MultiTaskForecastLoss(nn.Module):
    """
    Combined loss:
    total_loss = lambda_dir * L_dir + lambda_ret * L_ret + lambda_vol * L_vol + lambda_q * L_quantiles
    """

    def __init__(
        self,
        lambda_direction: float = 1.0,
        lambda_return: float = 2.0,
        lambda_volatility: float = 1.0,
        lambda_quantile: float = 1.5,
        quantiles: Optional[List[float]] = None
    ):
        super().__init__()
        self.lambda_direction = lambda_direction
        self.lambda_return = lambda_return
        self.lambda_volatility = lambda_volatility
        self.lambda_quantile = lambda_quantile

        self.direction_criterion = nn.CrossEntropyLoss()
        self.return_criterion = nn.HuberLoss(delta=1.0)
        self.volatility_criterion = nn.HuberLoss(delta=1.0)
        self.quantile_criterion = PinballLoss(quantiles=quantiles)

    def forward(
        self,
        pred_direction: torch.Tensor,
        pred_return: torch.Tensor,
        pred_volatility: torch.Tensor,
        pred_quantiles: torch.Tensor,
        target_direction: torch.Tensor,
        target_return: torch.Tensor,
        target_volatility: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """Calculates multi-task loss and tracks components independently."""
        # Head A: Direction (3-class)
        loss_dir = self.direction_criterion(pred_direction, target_direction)

        # Head B: Return (Huber)
        if target_return.dim() == 1:
            target_return = target_return.unsqueeze(-1)
        loss_ret = self.return_criterion(pred_return, target_return)

        # Head C: Volatility (Huber on log-volatility)
        if target_volatility.dim() == 1:
            target_volatility = target_volatility.unsqueeze(-1)
        loss_vol = self.volatility_criterion(pred_volatility, target_volatility)

        # Head D: Quantiles (Pinball on return)
        loss_q = self.quantile_criterion(pred_quantiles, target_return)

        total_loss = (
            self.lambda_direction * loss_dir
            + self.lambda_return * loss_ret
            + self.lambda_volatility * loss_vol
            + self.lambda_quantile * loss_q
        )

        return {
            "total_loss": total_loss,
            "direction_loss": loss_dir,
            "return_loss": loss_ret,
            "volatility_loss": loss_vol,
            "quantile_loss": loss_q
        }
