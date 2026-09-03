"""
CryptoScope AI - On-Chain Telemetry Adapter
Retrieves verified on-chain metrics or returns NOT_CONFIGURED.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

from providers.enrichment.base import BaseEnrichmentProvider

logger = logging.getLogger("cryptoscope.enrichment.onchain")


class OnChainProvider(BaseEnrichmentProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="ONCHAIN", api_key=api_key)

    async def get_onchain_metrics(self, asset: str) -> Dict[str, Any]:
        """
        Retrieves on-chain metrics (MVRV, SOPR, Active Addresses).
        Returns NOT_CONFIGURED if specialized on-chain provider API key is not supplied.
        """
        if not self.api_key:
            return self.not_configured_response("On-chain provider API key (CoinMetrics/Glassnode) is not configured")

        return self.not_configured_response("On-chain enterprise feed adapter not configured")
