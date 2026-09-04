"""
Venue Clock Synchronization and Skew Guard.
Phase 50: Clock Synchronization.
"""
from __future__ import annotations
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("CryptoScope.ClockSync")


class ClockSynchronizer:
    """Monitors local system clock relative to venue server timestamps. Halts inference if skew > tolerance."""

    def __init__(self, max_allowed_skew_sec: float = 2.0):
        self.max_allowed_skew_sec = max_allowed_skew_sec
        # venue -> latest skew in seconds (local - remote)
        self._skew_measurements: Dict[str, float] = {}

    def record_server_timestamp(self, venue: str, venue_time_ms: int):
        """Compute clock skew given venue epoch millisecond timestamp."""
        local_time_ms = int(time.time() * 1000)
        skew_sec = (local_time_ms - venue_time_ms) / 1000.0
        self._skew_measurements[venue.upper()] = round(skew_sec, 3)

        if abs(skew_sec) > self.max_allowed_skew_sec:
            logger.error(
                f"[ClockSync] Critical clock skew with {venue}: "
                f"{skew_sec:.2f}s exceeds tolerance {self.max_allowed_skew_sec}s!"
            )

    def is_clock_synchronized(self) -> tuple[bool, float, Dict[str, float]]:
        if not self._skew_measurements:
            return True, 0.0, {}

        max_skew = max(abs(s) for s in self._skew_measurements.values())
        synchronized = max_skew <= self.max_allowed_skew_sec
        return synchronized, max_skew, dict(self._skew_measurements)


clock_synchronizer = ClockSynchronizer()
