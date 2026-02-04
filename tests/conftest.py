"""Fixtures for Ambeo Soundbar tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ambeo_soundbar.const import (
    DOMAIN,
    AmbeoDevice,
    AmbeoRuntimeData,
)
from custom_components.ambeo_soundbar.coordinator import AmbeoDataUpdateCoordinator


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "192.168.1.100"},
        options={},
        unique_id="test_serial_123",
        title="Test Ambeo",
    )


@pytest.fixture
def mock_device() -> AmbeoDevice:
    """Return a mock device."""
    return AmbeoDevice(
        serial="test_serial_123",
        name="Test Ambeo",
        manufacturer="Sennheiser",
        model="AMBEO Soundbar Max",
        version="1.0.0",
        host="192.168.1.100",
        port=80,
    )


@pytest.fixture
def mock_api() -> Generator[MagicMock, None, None]:
    """Return a mock API."""
    api = MagicMock()
    api.get_serial = AsyncMock(return_value="test_serial_123")
    api.get_model = AsyncMock(return_value="AMBEO Soundbar Max")
    api.get_name = AsyncMock(return_value="Test Ambeo")
    api.get_version = AsyncMock(return_value="1.0.0")
    api.get_volume = AsyncMock(return_value=50)
    api.is_mute = AsyncMock(return_value=False)
    api.get_state = AsyncMock(return_value="online")
    api.get_current_source = AsyncMock(return_value="hdmi")
    api.get_ambeo_mode = AsyncMock(return_value=True)
    api.get_night_mode = AsyncMock(return_value=False)
    api.get_sound_feedback = AsyncMock(return_value=True)
    api.get_logo_brightness = AsyncMock(return_value=50)
    api.get_led_bar_brightness = AsyncMock(return_value=50)
    api.get_subwoofer_status = AsyncMock(return_value=True)
    api.get_subwoofer_volume = AsyncMock(return_value=0)
    api.get_voice_enhancement = AsyncMock(return_value=False)
    api.get_codec_led_brightness = AsyncMock(return_value=50)
    api.get_display_brightness = AsyncMock(return_value=50)
    api.has_capability = MagicMock(return_value=False)
    api.capabilities = []
    api.support_debounce_mode = MagicMock(return_value=False)
    api.get_volume_step = MagicMock(return_value=0.01)
    api.get_subwoofer_min_value = MagicMock(return_value=-10)
    api.get_subwoofer_max_value = MagicMock(return_value=10)
    api.get_all_sources = AsyncMock(return_value=[
        {"id": "hdmi", "title": "HDMI"},
        {"id": "bluetooth", "title": "Bluetooth"},
    ])
    api.get_all_presets = AsyncMock(return_value=[
        {"id": "movie", "title": "Movie"},
        {"id": "music", "title": "Music"},
    ])
    api.has_subwoofer = AsyncMock(return_value=False)
    yield api


@pytest.fixture
def mock_coordinator(
    hass, mock_config_entry, mock_api, mock_device
) -> AmbeoDataUpdateCoordinator:
    """Return a mock coordinator."""
    # Setup runtime_data manually for testing
    coordinator = AmbeoDataUpdateCoordinator(hass, mock_config_entry, mock_api)
    
    # Mock data
    coordinator.data = {
        "volume": 50,
        "mute": False,
        "power_state": "online",
        "source": "hdmi",
        "ambeo_mode": True,
        "night_mode": False,
        "sound_feedback": True,
        "logo_brightness": 50,
        "led_bar_brightness": 50,
        "subwoofer": {"status": True, "volume": 0},
        "voice_enhancement": {"enabled": False, "level": None},
        "codec_led_brightness": 50,
        "display_brightness": 50,
    }
    
    return coordinator


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations."""
    return enable_custom_integrations
