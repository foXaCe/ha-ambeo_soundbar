"""Data models for Ambeo Soundbar API responses."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Self


class PowerState(StrEnum):
    """Device power states."""

    ON = "on"
    STANDBY = "standby"
    UNKNOWN = "unknown"


class PlaybackState(StrEnum):
    """Media playback states."""

    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    UNKNOWN = "unknown"


class ConnectionState(StrEnum):
    """API connection states."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass(slots=True, frozen=True)
class DeviceInfo:
    """Device information model."""

    serial: str
    name: str
    model: str
    firmware: str
    manufacturer: str = "Sennheiser"

    @classmethod
    def from_api_response(
        cls,
        serial: str,
        name: str,
        model: str,
        firmware: str,
    ) -> Self:
        """Create from API response values."""
        return cls(
            serial=serial,
            name=name,
            model=model,
            firmware=firmware,
        )


@dataclass(slots=True, frozen=True)
class VolumeInfo:
    """Volume information model."""

    level: int
    muted: bool
    min_value: int = 0
    max_value: int = 100
    step: float = 0.01

    @property
    def percent(self) -> float:
        """Get volume as percentage (0.0-1.0)."""
        if self.max_value == self.min_value:
            return 0.0
        return (self.level - self.min_value) / (self.max_value - self.min_value)

    @classmethod
    def from_api_response(
        cls,
        level: int | None,
        muted: bool | None,
        min_value: int = 0,
        max_value: int = 100,
        step: float = 0.01,
    ) -> Self | None:
        """Create from API response values."""
        if level is None:
            return None
        return cls(
            level=level,
            muted=muted if muted is not None else False,
            min_value=min_value,
            max_value=max_value,
            step=step,
        )


@dataclass(slots=True, frozen=True)
class LightState:
    """LED/Logo light state model."""

    state: bool
    brightness: int | None = None
    min_brightness: int = 0
    max_brightness: int = 100

    @property
    def brightness_percent(self) -> float | None:
        """Get brightness as percentage."""
        if self.brightness is None:
            return None
        return self.brightness / self.max_brightness

    @classmethod
    def from_api_response(
        cls,
        state: bool | None,
        brightness: int | None = None,
        min_brightness: int = 0,
        max_brightness: int = 100,
    ) -> Self | None:
        """Create from API response values."""
        if state is None:
            return None
        return cls(
            state=state,
            brightness=brightness,
            min_brightness=min_brightness,
            max_brightness=max_brightness,
        )


@dataclass(slots=True, frozen=True)
class AudioSettings:
    """Audio settings model."""

    night_mode: bool | None = None
    ambeo_mode: bool | None = None
    voice_enhancement: bool | None = None
    sound_feedback: bool | None = None
    eco_mode: bool | None = None

    @classmethod
    def from_api_response(
        cls,
        night_mode: bool | None = None,
        ambeo_mode: bool | None = None,
        voice_enhancement: bool | None = None,
        sound_feedback: bool | None = None,
        eco_mode: bool | None = None,
    ) -> Self:
        """Create from API response values."""
        return cls(
            night_mode=night_mode,
            ambeo_mode=ambeo_mode,
            voice_enhancement=voice_enhancement,
            sound_feedback=sound_feedback,
            eco_mode=eco_mode,
        )


@dataclass(slots=True, frozen=True)
class SubwooferInfo:
    """Subwoofer information model."""

    present: bool
    enabled: bool | None = None
    volume: int | None = None
    min_volume: int = -10
    max_volume: int = 10

    @classmethod
    def from_api_response(
        cls,
        present: bool,
        enabled: bool | None = None,
        volume: int | None = None,
        min_volume: int = -10,
        max_volume: int = 10,
    ) -> Self:
        """Create from API response values."""
        return cls(
            present=present,
            enabled=enabled,
            volume=volume,
            min_volume=min_volume,
            max_volume=max_volume,
        )


@dataclass(slots=True, frozen=True)
class InputSource:
    """Input source model."""

    id: str
    title: str
    selected: bool = False

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> Self:
        """Create from API response dict."""
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            selected=data.get("selected", False),
        )


@dataclass(slots=True, frozen=True)
class AudioPreset:
    """Audio preset model."""

    id: str
    title: str
    selected: bool = False

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> Self:
        """Create from API response dict."""
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            selected=data.get("selected", False),
        )


@dataclass(slots=True, frozen=True)
class PlaybackInfo:
    """Media playback information model."""

    state: PlaybackState
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    art_url: str | None = None
    duration: int | None = None
    position: int | None = None

    @classmethod
    def from_api_response(cls, data: dict[str, Any] | None) -> Self | None:
        """Create from API response dict."""
        if data is None:
            return None

        state = PlaybackState.UNKNOWN
        if data.get("isPlaying"):
            state = PlaybackState.PLAYING
        elif data.get("isPaused"):
            state = PlaybackState.PAUSED
        elif data.get("isStopped"):
            state = PlaybackState.STOPPED

        return cls(
            state=state,
            title=data.get("title"),
            artist=data.get("artist"),
            album=data.get("album"),
            art_url=data.get("artUrl"),
            duration=data.get("duration"),
            position=data.get("position"),
        )


@dataclass(slots=True, frozen=True)
class BluetoothState:
    """Bluetooth pairing state model."""

    pairable: bool
    connected_devices: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_api_response(
        cls,
        pairable: bool | None,
        devices: list[dict[str, Any]] | None = None,
    ) -> Self | None:
        """Create from API response values."""
        if pairable is None:
            return None
        return cls(
            pairable=pairable,
            connected_devices=devices or [],
        )


@dataclass(slots=True)
class ApiResponse:
    """Generic API response wrapper with metadata."""

    success: bool
    data: Any = None
    error: str | None = None
    status_code: int | None = None
    request_duration: float = 0.0
    cached: bool = False

    @property
    def failed(self) -> bool:
        """Check if request failed."""
        return not self.success
