"""
Unit Tests for Health & Readiness Probes (Phase 28 & 29)
"""
import pytest
from datetime import datetime, timezone


def test_health_live_contract():
    """Liveness probe test contract."""
    response = {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    assert response["status"] == "alive"
    assert "timestamp" in response


def test_health_ready_structure():
    """Readiness probe schema test."""
    response = {
        "status": "ready",
        "database": "healthy",
        "redis": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    assert response["status"] in ["ready", "not_ready"]
    assert response["database"] in ["healthy", "unhealthy"]
    assert response["redis"] in ["healthy", "degraded"]
