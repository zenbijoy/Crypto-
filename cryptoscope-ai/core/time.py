"""
CryptoScope AI - Time & Point-In-Time Integrity
Enforces strict anti-leakage temporal rules:
Prediction at time T may only access available_time <= T.
"""
from datetime import datetime, timezone
from typing import Union

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def to_iso(dt: Union[datetime, None]) -> str:
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def assert_point_in_time(available_time: datetime, current_timestamp: datetime):
    """Enforces strict anti-leakage constraint: available_time must be <= current_timestamp"""
    if available_time > current_timestamp:
        raise ValueError(
            f"DATA LEAKAGE VIOLATION: observation available at {available_time} "
            f"is accessed during evaluation timestamp {current_timestamp}"
        )
