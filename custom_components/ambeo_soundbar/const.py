"""Constants for the Ambeo Soundbar integration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from .coordinator import AmbeoDataUpdateCoordinator
    from .api.impl.generic_api import AmbeoApi

DOMAIN = "ambeo_soundbar"
VERSION = "1.1.0"
MANUFACTURER = "Sennheiser"
DEFAULT_PORT = 80
TIMEOUT = 5

# Config keys
CONFIG_HOST = "host"
CONFIG_DEBOUNCE_COOLDOWN = "debounce_cooldown"
CONFIG_DEBOUNCE_COOLDOWN_DEFAULT = 0
CONFIG_HOST_DEFAULT = "ambeo.local"

# Brightness settings
BRIGHTNESS_SCALE = (0, 100)
DEFAULT_BRIGHTNESS = 50

# Model identifiers
MAX_SOUNDBAR = "AMBEO Soundbar Max"
PLUS_SOUNDBAR = "AMBEO Soundbar Plus"
MINI_SOUNDBAR = "AMBEO Soundbar Mini"

# Model-specific settings
BRIGHTNESS_SCALE_AMBEO_MAX_DISPLAY = (1, 126)
BRIGHTNESS_SCALE_AMBEO_MAX_LOGO = (1, 118)
DEFAULT_BRIGHTNESS_AMBEO_MAX = 128
EXCLUDE_SOURCES_MAX = ["aes"]
AMBEO_MAX_VOLUME_STEP = 0.02
AMBEO_POPCORN_VOLUME_STEP = 0.01

# API model mapping
POPCORN_API_MODELS = [PLUS_SOUNDBAR, MINI_SOUNDBAR]
ESPRESSO_API_MODELS = [MAX_SOUNDBAR]

# Typed ConfigEntry for runtime_data
type AmbeoConfigEntry = ConfigEntry[AmbeoRuntimeData]


@dataclass(slots=True)
class AmbeoRuntimeData:
    """Runtime data stored on the config entry."""

    coordinator: AmbeoDataUpdateCoordinator
    api: AmbeoApi
    device: AmbeoDevice


@dataclass(slots=True)
class AmbeoDevice:
    """Represents an Ambeo device."""

    serial: str
    name: str
    manufacturer: str
    model: str
    version: str
    host: str
    port: int


class Capability(StrEnum):
    """Device capabilities."""

    AMBEO_LOGO = "AmbeoLogo"
    LED_BAR = "LEDBar"
    CODEC_LED = "CodecLED"
    VOICE_ENHANCEMENT_TOGGLE = "VoiceEnhancementMode"
    VOICE_ENHANCEMENT_LEVEL = "VoiceEnhancementLevel"
    CENTER_SPEAKER_LEVEL = "CenterSpeakerLevel"
    SIDE_FIRING_LEVEL = "SideFiringLevel"
    UP_FIRING_LEVEL = "UpFiringLevel"
    RESET_EXPERT_SETTINGS = "ResetExpertSettings"
    BLUETOOTH_PAIRING = "AmbeoBluetoothPairing"
    SUBWOOFER = "SubWoofer"
    STANDBY = "standby"
    ECO_MODE = "EcoMode"
    MAX_LOGO = "AmbeoMaxLogo"
    MAX_DISPLAY = "AmbeoMaxDisplay"
    AMBEO_MODE = "AmbeoMode"
    NIGHT_MODE = "NightMode"
    SOUND_FEEDBACK = "SoundFeedback"
