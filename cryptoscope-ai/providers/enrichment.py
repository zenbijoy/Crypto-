"""
CryptoScope AI - Optional Enrichment Providers (Unified Facade)
Phase 9: Modularized enrichment adapters with absolute zero manufactured data.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from providers.enrichment.base import BaseEnrichmentProvider
from providers.enrichment.coingecko import CoinGeckoProvider
from providers.enrichment.defillama import DefiLlamaProvider
from providers.enrichment.fred import FREDProvider
from providers.enrichment.onchain import OnChainProvider
from providers.enrichment.sentiment import SentimentProvider


class CoinAnkProvider(BaseEnrichmentProvider):
    """CoinAnk Optional Derivatives Enrichment Adapter."""
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="COINANK", api_key=api_key)

    async def get_derivatives_intelligence(self, asset: str) -> Dict[str, Any]:
        if not self.api_key:
            return self.not_configured_response("COINANK_API_KEY is not configured")
        # When key configured, real API call would be issued; otherwise no fake numbers
        return self.not_configured_response("CoinAnk real API integration not configured")


# Alias MacroProvider to FREDProvider for backward compatibility
MacroProvider = FREDProvider

__all__ = [
    "CoinAnkProvider",
    "CoinGeckoProvider",
    "DefiLlamaProvider",
    "FREDProvider",
    "MacroProvider",
    "OnChainProvider",
    "SentimentProvider"
]
