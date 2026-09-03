"""
CryptoScope AI - DefiLlama Enrichment Adapter
Fetches real on-chain TVL & DeFi metrics from DefiLlama public API or returns DATA_UNAVAILABLE.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

from providers.enrichment.base import BaseEnrichmentProvider
from core.http_client import http_engine

logger = logging.getLogger("cryptoscope.enrichment.defillama")


class DefiLlamaProvider(BaseEnrichmentProvider):
    def __init__(self, base_url: str = "https://api.llama.fi"):
        super().__init__(name="DEFILLAMA")
        self.base_url = base_url

    async def get_defillama_metrics(self, asset: str) -> Dict[str, Any]:
        """Fetches chain TVL from DefiLlama /v2/chains or returns DATA_UNAVAILABLE."""
        chain_map = {"ETH": "Ethereum", "SOL": "Solana", "BTC": "Bitcoin"}
        chain_name = chain_map.get(asset.upper())
        if not chain_name:
            return {
                "status": "NOT_SUPPORTED",
                "chain": asset,
                "tvl_usd": None,
                "source": "DEFILLAMA"
            }

        url = f"{self.base_url}/v2/chains"
        try:
            data, _ = await http_engine.request("GET", url, max_retries=1)
            target = next((c for c in data if c.get("name", "").lower() == chain_name.lower()), None)
            if target:
                return {
                    "status": "AVAILABLE",
                    "chain": asset,
                    "tvl_usd": float(target.get("tvl", 0.0)),
                    "token_symbol": target.get("tokenSymbol"),
                    "source": "DEFILLAMA",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            return self.unavailable_response(f"Chain {chain_name} not found in DefiLlama")
        except Exception as exc:
            logger.warning("DefiLlama fetch failed: %s", exc)
            return self.unavailable_response(str(exc))
