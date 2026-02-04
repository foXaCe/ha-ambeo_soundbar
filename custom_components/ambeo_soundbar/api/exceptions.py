"""API Exceptions for Ambeo Soundbar - Re-exported from root.

All exceptions are defined in the root exceptions module for consistency.
This module provides convenient access when importing from the api package.
"""

from __future__ import annotations

from ..exceptions import (
    AmbeoAuthError,
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

__all__ = [
    "AmbeoError",
    "AmbeoConnectionError",
    "AmbeoAuthError",
    "AmbeoResponseError",
    "AmbeoRateLimitError",
    "AmbeoCircuitBreakerError",
    "AmbeoTimeoutError",
    "AmbeoNotFoundError",
    "AmbeoServerError",
    "AmbeoValidationError",
]
