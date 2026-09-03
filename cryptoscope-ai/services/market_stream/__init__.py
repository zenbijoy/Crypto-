"""
CryptoScope AI - Market Stream Package
Upstream exchange stream ingestion, subscription handling, and feed supervision.
"""
from services.market_stream.binance_ws import binance_ws_client
from services.market_stream.subscriptions import stream_registry, StreamType
from services.market_stream.stale_detector import StaleDetector
from services.market_stream.supervisor import stream_supervisor

__all__ = [
    "binance_ws_client",
    "stream_registry",
    "StreamType",
    "StaleDetector",
    "stream_supervisor"
]
