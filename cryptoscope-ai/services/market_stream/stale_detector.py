"""
CryptoScope AI - Market Stream Stale Detector
Monitors stream message freshness and detects stale or hung connections.
"""
import time
from typing import Dict, Optional


class StaleDetector:
    """Tracks per-stream event timestamps and identifies dead feeds."""
    def __init__(self, stale_threshold_seconds: float = 10.0):
        self.stale_threshold_seconds = stale_threshold_seconds
        self._last_event_mono: Dict[str, float] = {}

    def record_event(self, stream_id: str):
        self._last_event_mono[stream_id] = time.monotonic()

    def is_stale(self, stream_id: str) -> bool:
        last = self._last_event_mono.get(stream_id)
        if last is None:
            return True
        return (time.monotonic() - last) > self.stale_threshold_seconds

    def get_freshness_ms(self, stream_id: str) -> Optional[float]:
        last = self._last_event_mono.get(stream_id)
        if last is None:
            return None
        return (time.monotonic() - last) * 1000.0

    def clear(self):
        self._last_event_mono.clear()
