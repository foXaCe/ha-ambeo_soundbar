"""Exceptions for Ambeo Soundbar integration - God Tier Edition."""

from __future__ import annotations

from typing import Any

from homeassistant.exceptions import HomeAssistantError


class AmbeoError(HomeAssistantError):
    """Base exception for Ambeo integration with rich context."""

    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
        status_code: int | None = None,
        response_data: Any = None,
        retry_count: int = 0,
    ) -> None:
        super().__init__(message)
        self.url = url
        self.status_code = status_code
        self.response_data = response_data
        self.retry_count = retry_count

    def __str__(self) -> str:
        parts = [self.args[0]]
        if self.url:
            parts.append(f"URL: {self.url}")
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.retry_count > 0:
            parts.append(f"Retries: {self.retry_count}")
        return " | ".join(parts)


class AmbeoConnectionError(AmbeoError):
    """Connection failed - device unreachable or network error."""

    def __init__(
        self,
        message: str = "Connection failed",
        *,
        url: str | None = None,
        retry_count: int = 0,
        is_timeout: bool = False,
    ) -> None:
        super().__init__(
            f"{'Timeout: ' if is_timeout else ''}{message}",
            url=url,
            retry_count=retry_count,
        )
        self.is_timeout = is_timeout


class AmbeoAuthError(AmbeoError):
    """Authentication failed - invalid credentials or token expired."""

    def __init__(
        self,
        message: str = "Authentication failed",
        *,
        url: str | None = None,
    ) -> None:
        super().__init__(message, url=url, status_code=401)


class AmbeoResponseError(AmbeoError):
    """Invalid response from device - malformed JSON or unexpected format."""

    def __init__(
        self,
        message: str = "Invalid response",
        *,
        url: str | None = None,
        response_data: Any = None,
        expected_format: str | None = None,
    ) -> None:
        super().__init__(message, url=url, response_data=response_data)
        self.expected_format = expected_format


class AmbeoRateLimitError(AmbeoError):
    """Rate limit exceeded - too many requests."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after: float = 1.0,
        url: str | None = None,
    ) -> None:
        super().__init__(message, url=url, status_code=429)
        self.retry_after = retry_after


class AmbeoCircuitBreakerError(AmbeoError):
    """Circuit breaker is open - too many consecutive failures."""

    def __init__(
        self,
        message: str = "Circuit breaker open",
        *,
        failure_count: int = 5,
        open_until: str | None = None,
    ) -> None:
        super().__init__(message)
        self.failure_count = failure_count
        self.open_until = open_until


class AmbeoTimeoutError(AmbeoConnectionError):
    """Request timeout - device didn't respond in time."""

    def __init__(
        self,
        message: str = "Request timeout",
        *,
        url: str | None = None,
        timeout_seconds: float = 5.0,
        retry_count: int = 0,
    ) -> None:
        super().__init__(
            message,
            url=url,
            retry_count=retry_count,
            is_timeout=True,
        )
        self.timeout_seconds = timeout_seconds


class AmbeoNotFoundError(AmbeoError):
    """Resource not found - endpoint or data path doesn't exist."""

    def __init__(
        self,
        message: str = "Resource not found",
        *,
        url: str | None = None,
        path: str | None = None,
    ) -> None:
        super().__init__(message, url=url, status_code=404)
        self.path = path


class AmbeoServerError(AmbeoError):
    """Server error - device returned 5xx status."""

    def __init__(
        self,
        message: str = "Server error",
        *,
        url: str | None = None,
        status_code: int = 500,
        response_data: Any = None,
    ) -> None:
        super().__init__(
            message,
            url=url,
            status_code=status_code,
            response_data=response_data,
        )


class AmbeoValidationError(AmbeoError):
    """Validation error - invalid parameter or value."""

    def __init__(
        self,
        message: str = "Validation error",
        *,
        parameter: str | None = None,
        value: Any = None,
        allowed_values: list[Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=400)
        self.parameter = parameter
        self.value = value
        self.allowed_values = allowed_values or []
