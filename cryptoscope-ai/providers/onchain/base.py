"""
CryptoScope AI - On-Chain Base Provider Framework
Defines normalized schemas and status contracts for on-chain metrics across BTC, ETH, and SOL.
Statuses: REAL, NOT_CONFIGURED, UNAVAILABLE. Zero synthetic data.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class OnChainMetricSnapshot(BaseModel):
    chain: str  # "BTC", "ETH", "SOL"
    provider: str
    status: str  # "REAL", "NOT_CONFIGURED", "UNAVAILABLE"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Generic chain activity metrics
    block_height: Optional[int] = None
    tps: Optional[float] = None
    fee_rate_standard: Optional[float] = None  # sat/vB for BTC, Gwei for ETH, lamports for SOL
    fee_rate_priority: Optional[float] = None
    unconfirmed_transactions: Optional[int] = None
    
    # Specific metrics
    metrics: Dict[str, Any] = Field(default_factory=dict)
    attribution_url: Optional[str] = None


class BaseOnChainProvider(ABC):
    def __init__(self, chain: str, provider_name: str):
        self.chain = chain
        self.provider_name = provider_name

    @abstractmethod
    async def get_metrics(self) -> OnChainMetricSnapshot:
        pass
