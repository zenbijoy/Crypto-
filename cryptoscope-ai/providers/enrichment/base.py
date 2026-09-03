"""
CryptoScope AI - Base Enrichment Provider
Defines abstract contracts for external enrichment data providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class BaseEnrichmentProvider(ABC):
    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key
        self.is_configured = bool(api_key)

    @property
    def provider_name(self) -> str:
        return self.name

    def status(self) -> str:
        return "CONFIGURED" if self.is_configured else "NOT_CONFIGURED"

    def not_configured_response(self, reason: str = "API key not configured") -> Dict[str, Any]:
        return {
            "status": "NOT_CONFIGURED",
            "provider": self.name,
            "data": None,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def unavailable_response(self, error: str) -> Dict[str, Any]:
        return {
            "status": "DATA_UNAVAILABLE",
            "provider": self.name,
            "data": None,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
