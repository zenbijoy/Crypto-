"""
CryptoScope AI - Pydantic Request & Response Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str

class LoginRequest(BaseModel):
    email: str
    password: str

class DirectionProbabilities(BaseModel):
    p_up: float
    p_down: float
    p_sideways: float

class PriceQuantiles(BaseModel):
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float

class PredictionResponse(BaseModel):
    asset: str
    symbol: str
    timestamp: str
    horizon: str
    current_price: float
    expected_return: float
    direction: str
    direction_probabilities: DirectionProbabilities
    price_quantiles: PriceQuantiles
    expected_volatility: float
    confidence: int
    model_agreement: int
    regime: str
    regime_description: str
    data_quality: int
    risk_decision: str
    risk_level: str
    signal: str
    signal_reason: str
    explanations: Dict[str, List[str]]
    model_version: str
    disclaimer: str

class OrderRequest(BaseModel):
    symbol: str
    direction: str # LONG or SHORT
    size_usd: float
    leverage: int = 3
    stop_loss_pct: float = 1.5
    take_profit_pct: float = 2.5

class AlertCreateRequest(BaseModel):
    symbol: str
    horizon: str = "1h"
    min_confidence: int = 80
    min_model_agreement: int = 75
    signal_type: str = "LONG"
