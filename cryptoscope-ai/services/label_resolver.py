"""
CryptoScope AI - Delayed Label Resolver & Calibration Engine
Resolves true future ground truth for past predictions once holding periods elapse.
Computes MFE (Max Favorable Excursion), MAE (Max Adverse Excursion), and calibration errors.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np


class GroundTruthLabel(BaseModel):
    prediction_id: str
    symbol: str
    horizon: str
    entry_time: datetime
    resolution_time: datetime
    
    predicted_direction: str
    realized_direction: str
    realized_return_pct: float
    mfe_pct: float  # Maximum Favorable Excursion
    mae_pct: float  # Maximum Adverse Excursion
    realized_volatility_pct: float
    
    is_correct: bool
    brier_score: float  # squared error of directional probability


class LabelResolver:
    @staticmethod
    def resolve(
        prediction_id: str,
        symbol: str,
        horizon: str,
        entry_time: datetime,
        predicted_dir: str,
        predicted_probs: Dict[str, float],
        entry_price: float,
        price_trajectory: List[float]  # prices observed during the holding horizon
    ) -> GroundTruthLabel:
        if not price_trajectory or entry_price <= 0:
            now = datetime.now(timezone.utc)
            return GroundTruthLabel(
                prediction_id=prediction_id,
                symbol=symbol,
                horizon=horizon,
                entry_time=entry_time,
                resolution_time=now,
                predicted_direction=predicted_dir,
                realized_direction="FLAT",
                realized_return_pct=0.0,
                mfe_pct=0.0,
                mae_pct=0.0,
                realized_volatility_pct=0.0,
                is_correct=False,
                brier_score=1.0
            )

        final_px = price_trajectory[-1]
        ret_pct = ((final_px - entry_price) / entry_price) * 100.0

        # Trajectory excursions
        p_arr = np.array(price_trajectory)
        max_px = np.max(p_arr)
        min_px = np.min(p_arr)

        if predicted_dir == "UP":
            mfe = ((max_px - entry_price) / entry_price) * 100.0
            mae = ((min_px - entry_price) / entry_price) * 100.0
        else:
            mfe = ((entry_price - min_px) / entry_price) * 100.0
            mae = ((entry_price - max_px) / entry_price) * 100.0

        # Realized direction (with 0.15% deadband)
        if ret_pct > 0.15:
            realized_dir = "UP"
        elif ret_pct < -0.15:
            realized_dir = "DOWN"
        else:
            realized_dir = "FLAT"

        is_corr = (predicted_dir == realized_dir)

        # Brier score
        actual_onehot = {"DOWN": 0.0, "FLAT": 0.0, "UP": 0.0}
        actual_onehot[realized_dir] = 1.0
        brier = float(sum((predicted_probs.get(k, 0.33) - actual_onehot[k]) ** 2 for k in actual_onehot))

        # Realized volatility
        diffs = np.diff(p_arr) / p_arr[:-1]
        realized_vol = float(np.std(diffs) * np.sqrt(35040) * 100.0) if len(diffs) > 1 else 0.0

        return GroundTruthLabel(
            prediction_id=prediction_id,
            symbol=symbol,
            horizon=horizon,
            entry_time=entry_time,
            resolution_time=datetime.now(timezone.utc),
            predicted_direction=predicted_dir,
            realized_direction=realized_dir,
            realized_return_pct=round(ret_pct, 4),
            mfe_pct=round(mfe, 4),
            mae_pct=round(mae, 4),
            realized_volatility_pct=round(realized_vol, 2),
            is_correct=is_corr,
            brier_score=round(brier, 4)
        )
