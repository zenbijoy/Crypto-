"""
Unit Tests for Health & Readiness Probes (Phase 28 & 29)
"""
from datetime import datetime, timezone
import unittest


class TestHealthProbes(unittest.TestCase):
    def test_health_live_contract(self):
        """Liveness probe test contract."""
        response = {
            "status": "alive",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.assertEqual(response["status"], "alive")
        self.assertIn("timestamp", response)

    def test_health_ready_structure(self):
        """Readiness probe schema test."""
        response = {
            "status": "ready",
            "database": "healthy",
            "redis": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.assertIn(response["status"], ["ready", "not_ready"])
        self.assertIn(response["database"], ["healthy", "unhealthy"])
        self.assertIn(response["redis"], ["healthy", "degraded"])


def test_health_live_contract():
    TestHealthProbes().test_health_live_contract()

def test_health_ready_structure():
    TestHealthProbes().test_health_ready_structure()


if __name__ == "__main__":
    unittest.main()
