"""Test Ambeo Soundbar setup."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from custom_components.ambeo_soundbar.const import DOMAIN


@pytest.mark.asyncio
async def test_setup_entry_success(
    hass: HomeAssistant, mock_config_entry, mock_api
) -> None:
    """Test successful setup of config entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.ambeo_soundbar.AmbeoAPIFactory.create_api",
        AsyncMock(return_value=mock_api),
    ), patch(
        "custom_components.ambeo_soundbar.AmbeoDataUpdateCoordinator._async_update_data",
        AsyncMock(return_value={}),
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state.value == "loaded"

    # Verify device registry
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(
        identifiers={(DOMAIN, "test_serial_123")}
    )
    assert device is not None
    assert device.name == "Test Ambeo"
    assert device.manufacturer == "Sennheiser"


@pytest.mark.asyncio
async def test_unload_entry(hass: HomeAssistant, mock_config_entry, mock_api) -> None:
    """Test unloading config entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.ambeo_soundbar.AmbeoAPIFactory.create_api",
        AsyncMock(return_value=mock_api),
    ), patch(
        "custom_components.ambeo_soundbar.AmbeoDataUpdateCoordinator._async_update_data",
        AsyncMock(return_value={}),
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state.value == "loaded"

    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state.value == "not_loaded"
