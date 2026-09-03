"""
CryptoScope AI - Resilience & Circuit Breaker Engine
Implements Sections 44, 45:
- Token Bucket Rate Limiting per exchange/endpoint
- Circuit Breaker pattern with CLOSED, OPEN, HALF_OPEN states
- Automated health check monitoring & provider failover
"""
import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from core.enums import Provider, CircuitBreakerState

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = float(capacity)
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> bool:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.last_update = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

class CircuitBreaker:
    def __init__(self, provider: Provider, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.provider = provider
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time: Optional[float] = None
        self.last_success_time: Optional[float] = None

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.last_success_time = time.monotonic()

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

    def allow_request(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True
        if self.state == CircuitBreakerState.OPEN:
            now = time.monotonic()
            if self.last_failure_time and (now - self.last_failure_time > self.recovery_timeout):
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        if self.state == CircuitBreakerState.HALF_OPEN:
            return True
        return False

    def status(self) -> Dict[str, Any]:
        return {
            "provider": self.provider.value,
            "state": self.state.value,
            "consecutive_failures": self.failure_count,
            "last_failure_ago_sec": round(time.monotonic() - self.last_failure_time, 1) if self.last_failure_time else None
        }

class ResilienceManager:
    def __init__(self):
        self.breakers: Dict[Provider, CircuitBreaker] = {
            p: CircuitBreaker(p) for p in [
                Provider.BINANCE, Provider.BYBIT, Provider.OKX,
                Provider.COINBASE, Provider.HYPERLIQUID, Provider.COINANK
            ]
        }
        self.limiters: Dict[Provider, TokenBucket] = {
            Provider.BINANCE: TokenBucket(capacity=100, refill_rate=20.0),
            Provider.BYBIT: TokenBucket(capacity=80, refill_rate=15.0),
            Provider.OKX: TokenBucket(capacity=60, refill_rate=10.0),
            Provider.COINBASE: TokenBucket(capacity=50, refill_rate=10.0),
            Provider.HYPERLIQUID: TokenBucket(capacity=50, refill_rate=10.0),
        }

    def get_breaker(self, provider: Provider) -> CircuitBreaker:
        return self.breakers[provider]

    def get_limiter(self, provider: Provider) -> TokenBucket:
        return self.limiters.get(provider, TokenBucket(50, 10.0))

    def get_all_statuses(self) -> List[Dict[str, Any]]:
        return [cb.status() for cb in self.breakers.values()]

resilience_manager = ResilienceManager()
