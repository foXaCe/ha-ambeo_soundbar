"""Test light platform for Ambeo Soundbar."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.light import ATTR_BRIGHTNESS
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ambeo_soundbar.const import DOMAIN


@pytest.mark.asyncio
async def test_led_bar_light(hass: HomeAssistant, snapshot) -> None:
    """Test LED Bar light entity."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"host": "192.168.1.100"},
        unique_id="test_serial_123",
    )
    entry.add_to_hass(hass)

    # Setup the integration
    with patch(
        "custom_components.ambeo_soundbar.AmbeoAPIFactory.create_api"
    ) as mock_api_factory:
        mock_api = MagicMock()
        mock_api.get_serial = AsyncMock(return_value="test_serial_123")
        mock_api.get_model = AsyncMock(return_value="AMBEO Soundbar Plus")
        mock_api.get_name = AsyncMock(return_value="Test Ambeo")
        mock_api.get_version = AsyncMock(return_value="1.0.0")
        mock_api.has_capability = MagicMock(return_value=True)
        mock_api.get_led_bar_brightness = AsyncMock(return_value=50)
        mock_api.set_led_bar_brightness = AsyncMock()
        mock_api_factory.return_value = mock_api

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Check entity state
    state = hass.states.get("light.test_ambeo_led_bar")
    assert state == snapshot


@pytest.mark.asyncio
async def test_light_turn_on(hass: HomeAssistant) -> None:
    """Test turning on light."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"host": "192.168.1.100"},
        unique_id="test_serial_123",
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.ambeo_soundbar.AmbeoAPIFactory.create_api"
    ) as mock_api_factory:
        mock_api = MagicMock()
        mock_api.get_serial = AsyncMock(return_value="test_serial_123")
        mock_api.get_model = AsyncMock(return_value="AMBEO Soundbar Plus")
        mock_api.get_name = AsyncMock(return_value="Test Ambeo")
        mock_api.get_version = AsyncMock(return_value="1.0.0")
        mock_api.has_capability = MagicMock(return_value=True)
        mock_api.get_led_bar_brightness = AsyncMock(return_value=50)
        mock_api.set_led_bar_brightness = AsyncMock()
        mock_api_factory.return_value = mock_api

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Turn on light
        await hass.services.async_call(
            "light",
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: "light.test_ambeo_led_bar", ATTR_BRIGHTNESS: 128},
            blocking=True,
        )
        await hass.async_block_till_done()

        mock_api.set_led_bar_brightness.assert_called_once()
