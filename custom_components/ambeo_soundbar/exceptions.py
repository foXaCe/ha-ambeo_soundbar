"""Exceptions for Ambeo Soundbar integration."""

from homeassistant.exceptions import HomeAssistantError


class AmbeoError(HomeAssistantError):
    """Base exception for Ambeo integration."""


class AmbeoConnectionError(AmbeoError):
    """Connection failed."""


class AmbeoAuthError(AmbeoError):
    """Authentication failed."""


class AmbeoResponseError(AmbeoError):
    """Invalid response from device."""
