"""Robust API client for Ambeo Soundbar - God Tier Edition.

Features:
- Automatic retry with exponential backoff
- Circuit breaker pattern for fault tolerance
- Rate limiting to prevent overwhelming the device
- Rich exception context for debugging
- Connection pooling via Home Assistant's aiohttp session
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, TypeVar

import aiohttp
from aiohttp import ClientTimeout

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from ..const import TIMEOUT as DEFAULT_TIMEOUT
from ..exceptions import (
    AmbeoCircuitBreakerError,
    AmbeoConnectionError,
    AmbeoError,
    AmbeoNotFoundError,
    AmbeoRateLimitError,
    AmbeoResponseError,
    AmbeoServerError,
    AmbeoTimeoutError,
    AmbeoValidationError,
)
from .models import ApiResponse, ConnectionState

_LOGGER = logging.getLogger(__name__)

T = TypeVar("T")

# Default configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 0.5  # seconds
DEFAULT_CIRCUIT_BREAKER_THRESHOLD = 5
DEFAULT_CIRCUIT_BREAKER_TIMEOUT = 120  # seconds
DEFAULT_RATE_LIMIT_CALLS = 10
DEFAULT_RATE_LIMIT_PERIOD = 1.0  # seconds


@dataclass
class CircuitBreaker:
    """Circuit breaker for fault tolerance."""

    failure_threshold: int = DEFAULT_CIRCUIT_BREAKER_THRESHOLD
    timeout_seconds: int = DEFAULT_CIRCUIT_BREAKER_TIMEOUT
    _failure_count: int = field(default=0, init=False)
    _last_failure_time: datetime | None = field(default=None, init=False)
    _state: ConnectionState = field(default=ConnectionState.CONNECTED, init=False)

    @property
    def is_open(self) -> bool:
        """Check if circuit breaker is open (blocking requests)."""
        if self._state == ConnectionState.ERROR:
            if self._last_failure_time:
                elapsed = (datetime.now() - self._last_failure_time).total_seconds()
                if elapsed >= self.timeout_seconds:
                    _LOGGER.debug("Circuit breaker timeout elapsed, closing circuit")
                    self._state = ConnectionState.CONNECTED
                    self._failure_count = 0
                    self._last_failure_time = None
                    return False
            return True
        return False

    @property
    def state(self) -> ConnectionState:
        """Get current circuit state."""
        if self.is_open:
            return ConnectionState.ERROR
        return self._state

    def record_success(self) -> None:
        """Record a successful request."""
        if self._failure_count > 0:
            _LOGGER.debug("Circuit breaker: resetting failure count after success")
            self._failure_count = 0
            self._state = ConnectionState.CONNECTED
            self._last_failure_time = None

    def record_failure(self) -> None:
        """Record a failed request."""
        self._failure_count += 1
        self._last_failure_time = datetime.now()

        if self._failure_count >= self.failure_threshold:
            self._state = ConnectionState.ERROR
            _LOGGER.warning(
                "Circuit breaker OPEN after %d consecutive failures. "
                "Blocking requests for %d seconds",
                self._failure_count,
                self.timeout_seconds,
            )

    def __str__(self) -> str:
        return (
            f"CircuitBreaker(state={self.state}, "
            f"failures={self._failure_count}/{self.failure_threshold})"
        )


@dataclass
class RateLimiter:
    """Token bucket rate limiter."""

    max_calls: int = DEFAULT_RATE_LIMIT_CALLS
    period_seconds: float = DEFAULT_RATE_LIMIT_PERIOD
    _timestamps: deque[float] = field(default_factory=deque, init=False)

    async def acquire(self) -> None:
        """Acquire permission to make a request, waiting if necessary."""
        now = time.monotonic()
        cutoff = now - self.period_seconds

        # Remove old timestamps
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

        # Check if we need to wait
        if len(self._timestamps) >= self.max_calls:
            # Calculate wait time
            oldest = self._timestamps[0]
            wait_time = (oldest + self.period_seconds) - now
            if wait_time > 0:
                _LOGGER.debug(
                    "Rate limit reached (%d/%d), waiting %.2fs",
                    len(self._timestamps),
                    self.max_calls,
                    wait_time,
                )
                await asyncio.sleep(wait_time)
                # Recalculate after wait
                now = time.monotonic()
                cutoff = now - self.period_seconds
                while self._timestamps and self._timestamps[0] < cutoff:
                    self._timestamps.popleft()

        self._timestamps.append(now)

    @property
    def current_count(self) -> int:
        """Get current number of requests in the window."""
        now = time.monotonic()
        cutoff = now - self.period_seconds
        return sum(1 for ts in self._timestamps if ts > cutoff)


class AmbeoApiClient:
    """Robust API client for Ambeo Soundbar.

    Features:
    - Automatic retry with exponential backoff
    - Circuit breaker for fault tolerance
    - Rate limiting
    - Rich error context
    - Request timing and metrics
    """

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        *,
        session: aiohttp.ClientSession | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        rate_limit_calls: int = DEFAULT_RATE_LIMIT_CALLS,
        rate_limit_period: float = DEFAULT_RATE_LIMIT_PERIOD,
        circuit_breaker_threshold: int = DEFAULT_CIRCUIT_BREAKER_THRESHOLD,
        circuit_breaker_timeout: int = DEFAULT_CIRCUIT_BREAKER_TIMEOUT,
    ) -> None:
        """Initialize the API client.

        Args:
            hass: Home Assistant instance
            host: Device IP address
            port: Device port
            session: Optional aiohttp session (uses HA's session if None)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial retry delay (doubles with each attempt)
            rate_limit_calls: Maximum calls per period
            rate_limit_period: Rate limiting period in seconds
            circuit_breaker_threshold: Failures before opening circuit
            circuit_breaker_timeout: Seconds to keep circuit open
        """
        self._hass = hass
        self._host = host
        self._port = port
        self._session = session
        self._timeout = ClientTimeout(total=timeout)
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._own_session = session is None

        # Resilience components
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            timeout_seconds=circuit_breaker_timeout,
        )
        self._rate_limiter = RateLimiter(
            max_calls=rate_limit_calls,
            period_seconds=rate_limit_period,
        )

        # Metrics
        self._request_count = 0
        self._failure_count = 0
        self._last_request_time: datetime | None = None
        self._avg_response_time = 0.0

    @property
    def base_url(self) -> str:
        """Get base API URL."""
        return f"http://{self._host}:{self._port}/api"

    @property
    def circuit_state(self) -> ConnectionState:
        """Get current circuit breaker state."""
        return self._circuit_breaker.state

    @property
    def metrics(self) -> dict[str, Any]:
        """Get client metrics."""
        return {
            "requests_total": self._request_count,
            "failures_total": self._failure_count,
            "circuit_state": self.circuit_state.value,
            "rate_limit_current": self._rate_limiter.current_count,
            "rate_limit_max": self._rate_limiter.max_calls,
            "avg_response_time_ms": round(self._avg_response_time * 1000, 2),
            "last_request": self._last_request_time.isoformat()
            if self._last_request_time
            else None,
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            from homeassistant.helpers.aiohttp_client import async_get_clientsession

            self._session = async_get_clientsession(self._hass)
            self._own_session = False
        return self._session

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for endpoint."""
        # Remove leading slash if present
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        retry: bool = True,
    ) -> ApiResponse:
        """Make an API request with full resilience.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            json_data: Optional JSON body
            retry: Whether to retry on failure

        Returns:
            ApiResponse with data and metadata

        Raises:
            AmbeoCircuitBreakerError: If circuit breaker is open
            AmbeoRateLimitError: If rate limit is exceeded
            AmbeoConnectionError: If connection fails after retries
            AmbeoResponseError: If response is invalid
        """
        # Check circuit breaker
        if self._circuit_breaker.is_open:
            raise AmbeoCircuitBreakerError(
                "Circuit breaker is open - too many consecutive failures",
                failure_count=self._circuit_breaker._failure_count,
            )

        # Acquire rate limit slot
        await self._rate_limiter.acquire()

        url = self._build_url(endpoint)
        retries = self._max_retries if retry else 1
        last_exception: Exception | None = None
        start_time = time.monotonic()

        for attempt in range(retries):
            self._last_request_time = datetime.now()
            self._request_count += 1

            try:
                session = await self._get_session()

                _LOGGER.debug(
                    "API Request: %s %s (attempt %d/%d)",
                    method.upper(),
                    url,
                    attempt + 1,
                    retries,
                )

                async with session.request(
                    method,
                    url,
                    params=params,
                    json=json_data,
                    timeout=self._timeout,
                ) as response:
                    result = await self._handle_response(response, url)

                    # Update metrics
                    duration = time.monotonic() - start_time
                    self._update_response_time(duration)
                    self._circuit_breaker.record_success()

                    return result

            except AmbeoError:
                # Don't retry Ambeo errors (they're already processed)
                raise

            except asyncio.TimeoutError as err:
                last_exception = AmbeoTimeoutError(
                    f"Request timeout after {self._timeout.total}s",
                    url=url,
                    timeout_seconds=self._timeout.total or 5.0,
                    retry_count=attempt,
                )
                _LOGGER.debug("Request timeout (attempt %d/%d)", attempt + 1, retries)

            except aiohttp.ClientError as err:
                last_exception = AmbeoConnectionError(
                    f"Connection error: {err}",
                    url=url,
                    retry_count=attempt,
                )
                _LOGGER.debug(
                    "Connection error (attempt %d/%d): %s",
                    attempt + 1,
                    retries,
                    err,
                )

            except Exception as err:
                last_exception = AmbeoError(
                    f"Unexpected error: {err}",
                    url=url,
                    retry_count=attempt,
                )
                _LOGGER.exception("Unexpected error during request")

            # Calculate retry delay with exponential backoff
            if attempt < retries - 1:
                delay = self._retry_delay * (2**attempt)
                _LOGGER.debug("Retrying in %.2f seconds...", delay)
                await asyncio.sleep(delay)

        # All retries exhausted
        self._failure_count += 1
        self._circuit_breaker.record_failure()

        if last_exception:
            raise last_exception
        raise AmbeoConnectionError("Request failed after all retries", url=url)

    async def _handle_response(
        self, response: aiohttp.ClientResponse, url: str
    ) -> ApiResponse:
        """Handle HTTP response and parse result."""
        start_time = time.monotonic()

        # Handle specific status codes
        if response.status == 204:  # No content
            return ApiResponse(
                success=True,
                status_code=204,
                request_duration=time.monotonic() - start_time,
            )

        if response.status == 401:
            raise AmbeoError(
                "Authentication required",
                url=url,
                status_code=401,
            )

        if response.status == 404:
            raise AmbeoNotFoundError(
                "Resource not found",
                url=url,
                path=url,
            )

        if response.status == 429:
            raise AmbeoRateLimitError(
                "Rate limit exceeded",
                url=url,
                retry_after=1.0,
            )

        if 500 <= response.status < 600:
            try:
                error_data = await response.json()
            except Exception:
                error_data = None

            raise AmbeoServerError(
                f"Server error {response.status}",
                url=url,
                status_code=response.status,
                response_data=error_data,
            )

        if response.status >= 400:
            try:
                error_data = await response.json()
                message = error_data.get("message", f"Error {response.status}")
            except Exception:
                message = f"Error {response.status}"

            raise AmbeoValidationError(
                message,
                url=url,
                response_data=error_data if "error_data" in dir() else None,
            )

        # Parse successful response
        try:
            if "application/json" in response.headers.get("Content-Type", ""):
                data = await response.json()
            else:
                # Some endpoints may return plain text
                text = await response.text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    data = {"text": text}

            return ApiResponse(
                success=True,
                data=data,
                status_code=response.status,
                request_duration=time.monotonic() - start_time,
            )

        except json.JSONDecodeError as err:
            raise AmbeoResponseError(
                f"Invalid JSON response: {err}",
                url=url,
                response_data=await response.text(),
            )

        except Exception as err:
            raise AmbeoResponseError(
                f"Failed to parse response: {err}",
                url=url,
            )

    def _update_response_time(self, duration: float) -> None:
        """Update average response time using exponential moving average."""
        alpha = 0.3  # Smoothing factor
        if self._avg_response_time == 0:
            self._avg_response_time = duration
        else:
            self._avg_response_time = (
                alpha * duration + (1 - alpha) * self._avg_response_time
            )

    # Convenience methods

    async def get(
        self, endpoint: str, *, params: dict[str, Any] | None = None, retry: bool = True
    ) -> ApiResponse:
        """Make GET request."""
        return await self.request("GET", endpoint, params=params, retry=retry)

    async def post(
        self,
        endpoint: str,
        *,
        json_data: dict[str, Any] | None = None,
        retry: bool = True,
    ) -> ApiResponse:
        """Make POST request."""
        return await self.request("POST", endpoint, json_data=json_data, retry=retry)

    async def close(self) -> None:
        """Close the client and cleanup resources."""
        _LOGGER.debug("Closing API client, metrics: %s", self.metrics)

        # Only close session if we own it (not HA's shared session)
        if self._own_session and self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> AmbeoApiClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
