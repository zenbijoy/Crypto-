"""
Canonical Event Model and Deterministic Envelope for CryptoScope AI.
Phase 2: Production Event Model.
"""
from __future__ import annotations
import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class EventType(str, Enum):
    TRADE = "market:trade"
    CANDLE = "market:candle"
    ORDERBOOK = "market:orderbook"
    BOOK_TICKER = "market:book_ticker"
    FUNDING = "market:funding"
    OPEN_INTEREST = "market:oi"
    LIQUIDATION = "market:liquidation"
    FEATURE_REALTIME = "features:realtime"
    PREDICTION = "predictions"
    SIGNAL = "signals"
    PAPER_ORDER = "paper:orders"
    SYSTEM_EVENT = "system:events"
    DEAD_LETTER = "system:dlq"


class QualityState(str, Enum):
    CLEAN = "CLEAN"
    SUSPECT = "SUSPECT"
    DEGRADED = "DEGRADED"
    INVALID = "INVALID"


def generate_event_id(
    provider: str,
    symbol: str,
    event_type: str,
    event_time: datetime,
    sequence_id: Optional[int] = None,
    unique_payload_key: Optional[str] = None
) -> str:
    """Generate a deterministic SHA256 event ID based on event invariants."""
    ts_str = event_time.isoformat()
    seq_str = str(sequence_id) if sequence_id is not None else ""
    key_str = unique_payload_key or ""
    raw = f"{provider}:{symbol}:{event_type}:{ts_str}:{seq_str}:{key_str}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


class CanonicalEvent(BaseModel):
    """Canonical Event Envelope guaranteeing complete lineage, provenance, and quality state."""
    event_id: str = Field(description="Deterministic or UUID event identifier")
    event_type: EventType = Field(description="Canonical event type")
    provider: str = Field(description="Source exchange or internal generator (e.g. BINANCE, BYBIT, FEATURE_STORE)")
    symbol: str = Field(description="Canonical symbol e.g. BTC/USDT/PERP or BTCUSDT")
    market: str = Field(default="PERPETUAL", description="Market classification e.g. PERPETUAL, SPOT")
    event_time: datetime = Field(description="Timestamp from the venue when event occurred in UTC")
    available_time: datetime = Field(description="Timestamp when event became visible to the platform")
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Local ingestion timestamp")
    sequence_id: Optional[int] = Field(default=None, description="Venue sequence number or monotonic offset")
    schema_version: str = Field(default="v2.0", description="Semantic schema version of payload")
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:16], description="Distributed trace identifier")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific normalized dictionary")
    quality_state: QualityState = Field(default=QualityState.CLEAN, description="Assessed quality status")

    @classmethod
    def create(
        cls,
        event_type: EventType,
        provider: str,
        symbol: str,
        event_time: datetime,
        payload: Dict[str, Any],
        sequence_id: Optional[int] = None,
        market: str = "PERPETUAL",
        available_time: Optional[datetime] = None,
        schema_version: str = "v2.0",
        trace_id: Optional[str] = None,
        quality_state: QualityState = QualityState.CLEAN,
        unique_payload_key: Optional[str] = None
    ) -> CanonicalEvent:
        now = datetime.now(timezone.utc)
        avail = available_time or now
        event_id = generate_event_id(provider, symbol, event_type.value, event_time, sequence_id, unique_payload_key)
        return cls(
            event_id=event_id,
            event_type=event_type,
            provider=provider.upper(),
            symbol=symbol,
            market=market.upper(),
            event_time=event_time,
            available_time=avail,
            ingested_at=now,
            sequence_id=sequence_id,
            schema_version=schema_version,
            trace_id=trace_id or str(uuid.uuid4())[:16],
            payload=payload,
            quality_state=quality_state
        )

    def to_dict(self) -> Dict[str, Any]:
        d = self.model_dump()
        d["event_time"] = self.event_time.isoformat()
        d["available_time"] = self.available_time.isoformat()
        d["ingested_at"] = self.ingested_at.isoformat()
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CanonicalEvent:
        data_copy = dict(data)
        if isinstance(data_copy.get("event_time"), str):
            data_copy["event_time"] = datetime.fromisoformat(data_copy["event_time"])
        if isinstance(data_copy.get("available_time"), str):
            data_copy["available_time"] = datetime.fromisoformat(data_copy["available_time"])
        if isinstance(data_copy.get("ingested_at"), str):
            data_copy["ingested_at"] = datetime.fromisoformat(data_copy["ingested_at"])
        return cls(**data_copy)
