"""
CryptoScope AI - Market Stream Supervisor
Oversees stream freshness, orderbook sequence synchronization, and feed health monitoring.
"""
import asyncio
import logging
from typing import Dict, Any, Optional

from services.market_stream.binance_ws import binance_ws_client
from services.market_stream.stale_detector import StaleDetector

logger = logging.getLogger("cryptoscope.market_stream.supervisor")


class MarketStreamSupervisor:
    """Coordinates upstream market ingestion streams and monitors feed health."""
    def __init__(self):
        self.client = binance_ws_client
        self._monitor_task: Optional[asyncio.Task] = None

    async def start(self):
        await self.client.start()
        self._monitor_task = asyncio.create_task(self._health_monitor_loop())
        logger.info("MarketStreamSupervisor started.")

    async def stop(self):
        if self._monitor_task:
            self._monitor_task.cancel()
        await self.client.stop()
        logger.info("MarketStreamSupervisor stopped.")

    async def _health_monitor_loop(self):
        while True:
            await asyncio.sleep(10.0)
            if self.client.is_connected:
                # Log periodic status
                logger.debug(
                    "Market streams healthy. Total messages: %d, errors: %d",
                    self.client.total_messages_received, self.client.error_count
                )

    def get_health(self) -> Dict[str, Any]:
        return {
            "is_connected": self.client.is_connected,
            "last_connected_at": self.client.last_connected_at.isoformat() if self.client.last_connected_at else None,
            "total_messages": self.client.total_messages_received,
            "error_count": self.client.error_count,
            "provider": "BINANCE_USDM_WS"
        }

stream_supervisor = MarketStreamSupervisor()
