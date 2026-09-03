"""
CryptoScope AI - CoinGecko Enrichment Adapter
Fetches real asset metadata & global market state from CoinGecko API or returns DATA_UNAVAILABLE.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

from providers.enrichment.base import BaseEnrichmentProvider
from core.http_client import http_engine

logger = logging.getLogger("cryptoscope.enrichment.coingecko")


class CoinGeckoProvider(BaseEnrichmentProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="COINGECKO", api_key=api_key)
        self.base_url = "https://pro-api.coingecko.com/api/v3" if api_key else "https://api.coingecko.com/api/v3"

    async def get_asset_metadata(self, asset: str) -> Dict[str, Any]:
        """Fetches asset details from CoinGecko or returns DATA_UNAVAILABLE."""
        asset_map = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "DOGE": "dogecoin"}
        cg_id = asset_map.get(asset.upper())
        if not cg_id:
            return self.unavailable_response(f"Asset {asset} mapping not supported")

        url = f"{self.base_url}/coins/{cg_id}"
        headers = {"x-cg-pro-api-key": self.api_key} if self.api_key else {}
        params = {"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"}

        try:
            data, _ = await http_engine.request("GET", url, params=params, headers=headers, max_retries=1)
            md = data.get("market_data", {})
            return {
                "status": "AVAILABLE",
                "name": data.get("name"),
                "rank": data.get("market_cap_rank"),
                "market_cap_usd": md.get("market_cap", {}).get("usd"),
                "circulating_supply": md.get("circulating_supply"),
                "categories": data.get("categories", []),
                "source": "COINGECKO",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as exc:
            logger.warning("CoinGecko metadata fetch failed: %s", exc)
            return self.unavailable_response(str(exc))

    async def get_global_market_state(self) -> Dict[str, Any]:
        """Fetches global crypto stats from /global."""
        url = f"{self.base_url}/global"
        headers = {"x-cg-pro-api-key": self.api_key} if self.api_key else {}
        try:
            data, _ = await http_engine.request("GET", url, headers=headers, max_retries=1)
            d = data.get("data", {})
            return {
                "status": "AVAILABLE",
                "total_market_cap_usd": d.get("total_market_cap", {}).get("usd"),
                "total_24h_volume_usd": d.get("total_volume", {}).get("usd"),
                "btc_dominance_pct": d.get("market_cap_percentage", {}).get("btc"),
                "eth_dominance_pct": d.get("market_cap_percentage", {}).get("eth"),
                "sol_dominance_pct": d.get("market_cap_percentage", {}).get("sol"),
                "doge_dominance_pct": d.get("market_cap_percentage", {}).get("doge"),
                "source": "COINGECKO",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as exc:
            logger.warning("CoinGecko global fetch failed: %s", exc)
            return self.unavailable_response(str(exc))
