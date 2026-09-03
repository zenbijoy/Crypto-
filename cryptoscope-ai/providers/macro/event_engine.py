"""
CryptoScope AI - Event Timing & Release Risk Engine
Tracks economic events (FOMC, CPI, NFP) and crypto-specific milestones.
Calculates minutes_until_event, minutes_since_event, importance, and enforces release blackout windows.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta


class CalendarEvent(BaseModel):
    event_id: str
    event_name: str
    category: str  # "MACRO_ECONOMIC", "CRYPTO_PROTOCOL", "TOKEN_UNLOCK"
    importance: str  # "HIGH", "MEDIUM", "LOW"
    event_time: datetime
    expected_impact: str  # "VOLATILITY_EXPANSION", "DIRECTIONAL_TREND"


class EventProximityState(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    next_high_impact_event: Optional[CalendarEvent] = None
    minutes_until_next_event: Optional[float] = None
    recent_past_event: Optional[CalendarEvent] = None
    minutes_since_last_event: Optional[float] = None
    in_blackout_window: bool = False  # True if within 15 min before/after high-impact release
    blackout_reason: Optional[str] = None
    event_risk_multiplier: float = 1.0  # 1.0 = normal, 0.5 = half risk, 0.0 = full veto


class EventEngine:
    def __init__(self, blackout_minutes: int = 15):
        self.blackout_minutes = blackout_minutes
        self._events: List[CalendarEvent] = []
        self._bootstrap_calendar()

    def _bootstrap_calendar(self):
        now = datetime.now(timezone.utc)
        # Sample scheduled benchmark economic events
        self._events = [
            CalendarEvent(
                event_id="FOMC_DECISION",
                event_name="Federal Reserve FOMC Rate Decision & Press Conference",
                category="MACRO_ECONOMIC",
                importance="HIGH",
                event_time=now + timedelta(days=12, hours=4),
                expected_impact="VOLATILITY_EXPANSION"
            ),
            CalendarEvent(
                event_id="US_CPI_RELEASE",
                event_name="US Consumer Price Index (CPI) YoY / MoM",
                category="MACRO_ECONOMIC",
                importance="HIGH",
                event_time=now + timedelta(days=5, hours=1, minutes=30),
                expected_impact="VOLATILITY_EXPANSION"
            ),
            CalendarEvent(
                event_id="US_NFP_JOBS",
                event_name="US Non-Farm Payrolls (NFP) & Unemployment",
                category="MACRO_ECONOMIC",
                importance="HIGH",
                event_time=now + timedelta(days=1, hours=14),
                expected_impact="VOLATILITY_EXPANSION"
            ),
            CalendarEvent(
                event_id="ETH_UPGRADE_PENCIL",
                event_name="Ethereum Network Consensus Layer Upgrade",
                category="CRYPTO_PROTOCOL",
                importance="MEDIUM",
                event_time=now + timedelta(days=22),
                expected_impact="DIRECTIONAL_TREND"
            )
        ]

    def register_event(self, event: CalendarEvent):
        self._events.append(event)
        self._events.sort(key=lambda x: x.event_time)

    def evaluate_proximity(self, as_of: Optional[datetime] = None) -> EventProximityState:
        now = as_of or datetime.now(timezone.utc)
        future_events = [e for e in self._events if e.event_time >= now]
        past_events = [e for e in self._events if e.event_time < now]

        next_event = future_events[0] if future_events else None
        last_event = past_events[-1] if past_events else None

        min_until = (next_event.event_time - now).total_seconds() / 60.0 if next_event else None
        min_since = (now - last_event.event_time).total_seconds() / 60.0 if last_event else None

        # Blackout check
        in_blackout = False
        reason = None
        multiplier = 1.0

        if next_event and next_event.importance == "HIGH" and min_until is not None and min_until <= self.blackout_minutes:
            in_blackout = True
            reason = f"Within {round(min_until)}m of high-impact event: {next_event.event_name}"
            multiplier = 0.0
        elif last_event and last_event.importance == "HIGH" and min_since is not None and min_since <= self.blackout_minutes:
            in_blackout = True
            reason = f"Within {round(min_since)}m following high-impact event: {last_event.event_name}"
            multiplier = 0.5
        elif next_event and next_event.importance == "HIGH" and min_until is not None and min_until <= 60.0:
            # 1 hour warning
            multiplier = 0.75

        return EventProximityState(
            timestamp=now,
            next_high_impact_event=next_event,
            minutes_until_next_event=round(min_until, 1) if min_until is not None else None,
            recent_past_event=last_event,
            minutes_since_last_event=round(min_since, 1) if min_since is not None else None,
            in_blackout_window=in_blackout,
            blackout_reason=reason,
            event_risk_multiplier=multiplier
        )
