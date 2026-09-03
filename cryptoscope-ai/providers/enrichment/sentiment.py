"""
CryptoScope AI - Sentiment & Fear/Greed Adapter
Queries official Alternative.me Crypto Fear & Greed public API or returns DATA_UNAVAILABLE.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

from providers.enrichment.base import BaseEnrichmentProvider
from core.http_client import http_engine

logger = logging.getLogger("cryptoscope.enrichment.sentiment")


class SentimentProvider(BaseEnrichmentProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="SENTIMENT", api_key=api_key)
        self.fng_url = "https://api.alternative.me/fng/?limit=1"

    async def get_sentiment(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """Fetches real Crypto Fear & Greed index from Alternative.me."""
        try:
            data, _ = await http_engine.request("GET", self.fng_url, max_retries=1)
            items = data.get("data", [])
            if items:
                fng_val = int(items[0].get("value", 50))
                classification = items[0].get("value_classification", "Neutral")
                ts = int(items[0].get("timestamp", int(datetime.now(timezone.utc).timestamp())))
                return {
                    "status": "AVAILABLE",
                    "fear_and_greed_score": fng_val,
                    "classification": classification,
                    "source": "ALTERNATIVE_ME_API",
                    "timestamp": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
                }
            return self.unavailable_response("Empty response from Alternative.me Fear & Greed API")
        except Exception as exc:
            logger.warning("Sentiment query failed: %s", exc)
            return self.unavailable_response(str(exc))
