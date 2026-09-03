"""
CryptoScope AI - Production Resilient Provider HTTP Engine
Enterprise async HTTP client for cryptocurrency exchange connectivity:
- Host/provider-isolated circuit breakers (preventing cross-provider cascading trip)
- Exponential backoff with bounded full jitter
- Exchange rate limit tracking (Binance x-mbx-used-weight-1m)
- 429 & 418 IP ban defense with Retry-After header compliance
- Non-retryable vs retryable error separation
- Structured telemetry, trace IDs, and monotonic latency tracking
- Clean lifecycle management for event loop changes and shutdown
"""
import asyncio
import logging
import random
import time
import uuid
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse
import httpx

from core.exceptions import (
    ProviderError,
    RateLimitError,
    ProviderUnavailableError,
    DataUnavailableError
)

logger = logging.getLogger("cryptoscope.http_client")


class CircuitBreakerState:
    CLOSED = "CLOSED"        # Normal healthy operation
    OPEN = "OPEN"            # Tripped, fast-failing calls
    HALF_OPEN = "HALF_OPEN"  # Testing single probe requests


class CircuitBreaker:
    """Per-host circuit breaker to prevent cascading failures."""
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
            logger.warning("Circuit breaker tripped to OPEN (consecutive failures: %d)", self.failure_count)

    def allow_request(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True
        if self.state == CircuitBreakerState.OPEN:
            if time.monotonic() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker entered HALF_OPEN. Testing recovery.")
                return True
            return False
        # HALF_OPEN allows probe requests
        return True


class ResilientHttpClient:
    """
    Singleton resilient async HTTP client with host-specific circuit breakers,
    adaptive rate-limit gating, connection pooling, and lifecycle handling.
    """
    def __init__(
        self,
        max_connections: int = 150,
        max_keepalive_connections: int = 40,
        timeout_seconds: float = 12.0,
        connect_timeout_seconds: float = 5.0
    ):
        self.timeout = httpx.Timeout(timeout_seconds, connect=connect_timeout_seconds)
        self.limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=30.0
        )
        self._client: Optional[httpx.AsyncClient] = None
        self._client_loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Per-host circuit breakers
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Binance rate limit tracking (1-min weight)
        self.used_weight_1m: int = 0
        self.weight_limit_1m: int = 1200
        self.last_weight_update: float = 0.0
        
        # Server time offset synchronization
        self.server_time_offset_ms: int = 0
        self.last_time_sync: float = 0.0
        
        # Request metrics
        self.total_requests: int = 0
        self.total_errors: int = 0

    def _get_host(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc or "default"

    def get_circuit_breaker(self, url: str) -> CircuitBreaker:
        host = self._get_host(url)
        if host not in self._circuit_breakers:
            self._circuit_breakers[host] = CircuitBreaker()
        return self._circuit_breakers[host]

    async def get_client(self) -> httpx.AsyncClient:
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self._client is None or self._client.is_closed or self._client_loop != current_loop:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=self.limits,
                headers={"User-Agent": "CryptoScopeAI/2.1 (Truthful Quantitative Platform)"}
            )
            self._client_loop = current_loop
        return self._client

    async def close(self):
        """Clean shutdown hook for connection pools."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            self._client_loop = None
            logger.info("ResilientHttpClient connection pool cleanly closed.")

    def _update_rate_limit(self, headers: httpx.Headers):
        for header_name in ["x-mbx-used-weight-1m", "x-mbx-used-weight"]:
            val = headers.get(header_name)
            if val and val.isdigit():
                self.used_weight_1m = int(val)
                self.last_weight_update = time.monotonic()
                if self.used_weight_1m > (self.weight_limit_1m * 0.90):
                    logger.warning(
                        "Binance weight near capacity: %d/%d (90%%+)",
                        self.used_weight_1m, self.weight_limit_1m
                    )
                break

    async def check_rate_limit_pause(self):
        """Proactively delays requests when approaching 95% of Binance weight limit."""
        if self.used_weight_1m >= (self.weight_limit_1m * 0.95):
            pause = 2.0
            logger.warning("Approaching exchange rate limit ceiling (%d). Gating for %.1fs", self.used_weight_1m, pause)
            await asyncio.sleep(pause)

    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
        base_backoff: float = 0.3,
        request_id: Optional[str] = None
    ) -> Tuple[Any, float]:
        """
        Executes HTTP request with host-isolated circuit breakers, rate-limit gating,
        bounded exponential backoff, monotonic latency measurement, and Retry-After handling.
        """
        cb = self.get_circuit_breaker(url)
        if not cb.allow_request():
            host = self._get_host(url)
            raise ProviderUnavailableError(f"Circuit breaker is OPEN for host: {host}")

        await self.check_rate_limit_pause()
        client = await self.get_client()

        req_id = request_id or str(uuid.uuid4())[:8]
        req_headers = dict(headers or {})
        req_headers["X-Request-ID"] = req_id

        attempt = 0
        last_exception = None

        while attempt <= max_retries:
            start_mono = time.monotonic()
            self.total_requests += 1
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=req_headers
                )
                latency_ms = (time.monotonic() - start_mono) * 1000.0
                self._update_rate_limit(response.headers)

                # Rate Limit handling (429 / 418)
                if response.status_code in (429, 418):
                    retry_after_str = response.headers.get("Retry-After", "5")
                    try:
                        retry_after = int(retry_after_str)
                    except ValueError:
                        retry_after = 5
                    logger.error("[%s] Exchange rate limit HTTP %d. Retry-After: %ds", req_id, response.status_code, retry_after)
                    cb.record_failure()
                    self.total_errors += 1
                    raise RateLimitError(
                        f"Exchange rate limit exceeded (HTTP {response.status_code}). Backing off {retry_after}s",
                        retry_after_seconds=retry_after
                    )

                # 5xx Server Errors (Retryable)
                if response.status_code >= 500:
                    response.raise_for_status()

                # 4xx Client Errors (Non-retryable unless rate limit)
                if response.status_code >= 400:
                    self.total_errors += 1
                    error_msg = f"HTTP {response.status_code}: {response.text[:300]}"
                    raise ProviderError(error_msg)

                cb.record_success()
                return response.json(), latency_ms

            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                self.total_errors += 1
                last_exception = exc
                attempt += 1
                if attempt > max_retries:
                    cb.record_failure()
                    logger.error("[%s] Request exhausted retries (%d): %s %s (%s)", req_id, max_retries, method, url, str(exc))
                    raise ProviderError(f"Exchange request failed after {max_retries} attempts: {str(exc)}") from exc

                # Bounded exponential backoff with full jitter: backoff in [0.1, min(10.0, base * 2^attempt)]
                backoff_cap = min(10.0, base_backoff * (2 ** attempt))
                backoff = random.uniform(0.1, backoff_cap)
                logger.warning("[%s] HTTP retry %d/%d after %.2fs due to: %s", req_id, attempt, max_retries, backoff, str(exc))
                await asyncio.sleep(backoff)

            except RateLimitError:
                raise

        raise ProviderError(f"HTTP request exhausted retries: {str(last_exception)}")

    async def sync_server_time(self, fapi_base_url: str = "https://fapi.binance.com") -> int:
        """Synchronizes local clock with Binance Futures server time."""
        url = f"{fapi_base_url}/fapi/v1/time"
        data, _ = await self.request("GET", url, max_retries=2)
        server_time = int(data["serverTime"])
        local_time = int(time.time() * 1000)
        self.server_time_offset_ms = server_time - local_time
        self.last_time_sync = time.monotonic()
        logger.info("Synchronized Binance server time. Offset: %+d ms", self.server_time_offset_ms)
        return self.server_time_offset_ms


http_engine = ResilientHttpClient()
