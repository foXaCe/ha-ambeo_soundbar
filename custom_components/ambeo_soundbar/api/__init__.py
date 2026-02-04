"""Ambeo Soundbar API package - God Tier Edition.

This package provides a robust, resilient, and performant API client
for communicating with Sennheiser Ambeo Soundbar devices.

Example:
    from custom_components.ambeo_soundbar.api import AmbeoApiClient, ApiResponse
    from custom_components.ambeo_soundbar.api.models import DeviceInfo

    async with AmbeoApiClient(hass, "192.168.1.100", 80) as client:
        response = await client.get("getData?path=systemmanager:/deviceName")
        if response.success:
            print(response.data)
"""

from __future__ import annotations

# Core client
from .client import AmbeoApiClient

# Data models
from .models import (
    ApiResponse,
    AudioPreset,
    AudioSettings,
    BluetoothState,
    ConnectionState,
    DeviceInfo,
    InputSource,
    LightState,
    PlaybackInfo,
    PlaybackState,
    PowerState,
    SubwooferInfo,
    VolumeInfo,
)

# Factory for model-specific APIs
from .factory import AmbeoAPIFactory

# Base API implementations
from .impl.generic_api import AmbeoApi
from .impl.popcorn_api import AmbeoPopcornApi
from .impl.espresso_api import AmbeoEspressoApi

__all__ = [
    # Client
    "AmbeoApiClient",
    # Factory
    "AmbeoAPIFactory",
    # Base implementations
    "AmbeoApi",
    "AmbeoPopcornApi",
    "AmbeoEspressoApi",
    # Models
    "ApiResponse",
    "AudioPreset",
    "AudioSettings",
    "BluetoothState",
    "ConnectionState",
    "DeviceInfo",
    "InputSource",
    "LightState",
    "PlaybackInfo",
    "PlaybackState",
    "PowerState",
    "SubwooferInfo",
    "VolumeInfo",
]
