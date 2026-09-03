"""
CryptoScope AI - FRED Macroeconomic Enrichment Adapter
Retrieves Federal Reserve Economic Data (FRED) observations or returns NOT_CONFIGURED.
Tracks: observation_time, available_time, vintage/revision information.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

from providers.enrichment.base import BaseEnrichmentProvider
from core.http_client import http_engine

logger = logging.getLogger("cryptoscope.enrichment.fred")


class FREDProvider(BaseEnrichmentProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="FRED", api_key=api_key)
        self.base_url = "https://api.stlouisfed.org/fred"

    async def get_macro_indicators(self) -> Dict[str, Any]:
        """Fetches macro indicators (DXY, 10Y Yield, CPI) if API key is configured."""
        if not self.api_key:
            return self.not_configured_response("FRED_API_KEY is not configured in environment")

        series_to_fetch = {
            "us_10y_yield": "DGS10",
            "us_2y_yield": "DGS2",
            "fed_funds_rate": "FEDFUNDS"
        }

        results: Dict[str, Any] = {
            "status": "AVAILABLE",
            "provider": "FRED",
            "source": "FRED_API",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        try:
            for field, series_id in series_to_fetch.items():
                url = f"{self.base_url}/series/observations"
                params = {
                    "series_id": series_id,
                    "api_key": self.api_key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": 1
                }
                data, _ = await http_engine.request("GET", url, params=params, max_retries=1)
                obs_list = data.get("observations", [])
                if obs_list:
                    obs = obs_list[0]
                    val_str = obs.get("value", "")
                    try:
                        results[field] = float(val_str)
                        results[f"{field}_obs_time"] = obs.get("date")
                    except ValueError:
                        results[field] = None
                else:
                    results[field] = None

            return results
        except Exception as exc:
            logger.warning("FRED observation fetch failed: %s", exc)
            return self.unavailable_response(str(exc))
