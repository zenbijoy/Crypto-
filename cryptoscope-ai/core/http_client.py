"""
CryptoScope AI - Production Resilient Provider HTTP Engine
Implements Step 4 Specifications:
- Reusable async HTTP client with connection pooling
- Exponential backoff with full jitter
- Binance rate limit tracking (x-mbx-used-weight-1m header parsing)
- 429 & 418 IP ban defense and proactive throttle gating
- Bounded retries with circuit breaker pattern
- Request latency tracking and server time offset synchronization
- Structured error hierarchy: ProviderError, RateLimitError, ProviderUnavailableError
"""
import asyncio
import logging
import random
import time
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timezone
import httpx

from core.exceptions import (
    ProviderError,
    RateLimitError,
    ProviderUnavailableError,
    DataUnavailableError
)

logger = logging.getLogger("cryptoscope.http_client")


class CircuitBreakerState:
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Failing, fast-reject calls
    HALF_OPEN = "HALF_OPEN" # Testing recovery


class CircuitBreaker:
    """Circuit breaker for exchange HTTP endpoints."""
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time: float = 0.0

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning("Circuit breaker tripped to OPEN. Threshold: %d", self.failure_threshold)

    def allow_request(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True
        if self.state == CircuitBreakerState.OPEN:
            if time.monotonic() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker entered HALF_OPEN. Testing recovery.")
                return True
            return False
        # In HALF_OPEN, allow single test request
        return True


class ResilientHttpClient:
    """
    Singleton-capable resilient async HTTP client tailored for high-volume crypto exchanges.
    """
    def __init__(
        self,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        timeout_seconds: float = 10.0,
        connect_timeout_seconds: float = 5.0
    ):
        self.timeout = httpx.Timeout(timeout_seconds, connect=connect_timeout_seconds)
        self.limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=30.0
        )
        self._client: Optional[httpx.AsyncClient] = None
        self.circuit_breaker = CircuitBreaker()
        
        # Binance rate limit state
        self.used_weight_1m: int = 0
        self.weight_limit_1m: int = 1200 # Standard Binance USD-M 1-min weight limit
        self.last_weight_update: float = 0.0
        
        # Time synchronization offset (server_time_ms - local_time_ms)
        self.server_time_offset_ms: int = 0
        self.last_time_sync: float = 0.0

    async def get_client(self) -> httpx.AsyncClient:
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self._client is None or self._client.is_closed or getattr(self, "_client_loop", None) != current_loop:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=self.limits,
                headers={"User-Agent": "CryptoScopeAI/2.1 (Quantitative Platform)"}
            )
            self._client_loop = current_loop
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _update_rate_limit(self, headers: httpx.Headers):
        """Extracts and tracks rate limit headers from exchange responses."""
        for header_name in ["x-mbx-used-weight-1m", "x-mbx-used-weight"]:
            val = headers.get(header_name)
            if val and val.isdigit():
                self.used_weight_1m = int(val)
                self.last_weight_update = time.monotonic()
                if self.used_weight_1m > (self.weight_limit_1m * 0.90):
                    logger.warning(
                        "Binance 1m weight threshold near capacity: %d/%d",
                        self.used_weight_1m, self.weight_limit_1m
                    )
                break

    async def check_rate_limit_pause(self):
        """Proactively pauses if close to Binance 1200 weight limit to avoid 429/418."""
        if self.used_weight_1m >= (self.weight_limit_1m * 0.95):
            pause_time = 2.5
            logger.warning("Approaching IP ban limit (%d). Throttling for %.1fs", self.used_weight_1m, pause_time)
            await asyncio.sleep(pause_time)

    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
        base_backoff: float = 0.4
    ) -> Tuple[Any, float]:
        """
        Executes HTTP request with rate-limit guarding, retries, jitter, and latency recording.
        Returns (parsed_json_or_text, latency_ms).
        """
        if not self.circuit_breaker.allow_request():
            raise ProviderUnavailableError(f"Circuit breaker is OPEN for URL: {url}")

        await self.check_rate_limit_pause()
        client = await self.get_client()

        attempt = 0
        last_exception = None

        while attempt <= max_retries:
            start_time = time.monotonic()
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=headers
                )
                latency_ms = (time.monotonic() - start_time) * 1000.0
                self._update_rate_limit(response.headers)

                # Check for rate limit responses
                if response.status_code == 429 or response.status_code == 418:
                    retry_after = int(response.headers.get("Retry-After", "10"))
                    logger.error("Rate limited (HTTP %d). Retry-After: %ds", response.status_code, retry_after)
                    self.circuit_breaker.record_failure()
                    raise RateLimitError(
                        f"Exchange rate limit exceeded (HTTP {response.status_code}). Backing off {retry_after}s"
                    )

                if response.status_code >= 500:
                    response.raise_for_status()

                if response.status_code >= 400:
                    # Client errors (4xx other than 429) usually shouldn't retry
                    error_msg = f"HTTP {response.status_code}: {response.text[:300]}"
                    raise ProviderError(error_msg)

                self.circuit_breaker.record_success()
                return response.json(), latency_ms

            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                last_exception = exc
                attempt += 1
                if attempt > max_retries:
                    self.circuit_breaker.record_failure()
                    logger.error("HTTP request failed after %d attempts: %s %s (%s)", max_retries, method, url, str(exc))
                    raise ProviderError(f"Exchange request failed after {max_retries} attempts: {str(exc)}") from exc

                # Exponential backoff with full jitter: backoff = random(0, base * 2^attempt)
                backoff = random.uniform(0.1, base_backoff * (2 ** attempt))
                logger.warning("HTTP error (%s). Retrying %s %s in %.2fs (attempt %d/%d)",
                               str(exc), method, url, backoff, attempt, max_retries)
                await asyncio.sleep(backoff)

            except RateLimitError:
                raise

        raise ProviderError(f"HTTP request exhausted retries: {str(last_exception)}")

    async def sync_server_time(self, fapi_base_url: str = "https://fapi.binance.com") -> int:
        """
        Synchronizes local clock with Binance Futures server time.
        Updates self.server_time_offset_ms = server_time - local_time.
        """
        url = f"{fapi_base_url}/fapi/v1/time"
        data, _ = await self.request("GET", url, max_retries=2)
        server_time = int(data["serverTime"])
        local_time = int(time.time() * 1000)
        self.server_time_offset_ms = server_time - local_time
        self.last_time_sync = time.monotonic()
        logger.info("Synchronized Binance server time. Offset: %+d ms", self.server_time_offset_ms)
        return self.server_time_offset_ms


# Global singleton instance
http_engine = ResilientHttpClient()
