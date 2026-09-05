"""
CryptoScope AI - Canonical Routers Export
"""
from apps.api.routers import (
    health,
    auth,
    users,
    markets,
    derivatives,
    orderbook,
    orderflow,
    liquidations,
    predictions,
    alerts,
    paper,
    providers,
)

__all__ = [
    "health",
    "auth",
    "users",
    "markets",
    "derivatives",
    "orderbook",
    "orderflow",
    "liquidations",
    "predictions",
    "alerts",
    "paper",
    "providers",
]
