"""Test Ambeo Soundbar coordinator."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.ambeo_soundbar.coordinator import AmbeoDataUpdateCoordinator
from custom_components.ambeo_soundbar.exceptions import AmbeoAuthError, AmbeoConnectionError


@pytest.mark.asyncio
async def test_coordinator_update_success(
    hass: HomeAssistant, mock_config_entry, mock_api
) -> None:
    """Test successful coordinator update."""
    coordinator = AmbeoDataUpdateCoordinator(hass, mock_config_entry, mock_api)

    data = await coordinator._async_update_data()

    assert data is not None
    assert data["volume"] == 50
    assert data["mute"] is False


@pytest.mark.asyncio
async def test_coordinator_auth_error(
    hass: HomeAssistant, mock_config_entry, mock_api
) -> None:
    """Test coordinator auth error handling."""
    mock_api.get_volume = AsyncMock(side_effect=AmbeoAuthError("Auth failed"))
    coordinator = AmbeoDataUpdateCoordinator(hass, mock_config_entry, mock_api)

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_connection_error(
    hass: HomeAssistant, mock_config_entry, mock_api
) -> None:
    """Test coordinator connection error handling."""
    mock_api.get_volume = AsyncMock(side_effect=AmbeoConnectionError("Connection failed"))
    coordinator = AmbeoDataUpdateCoordinator(hass, mock_config_entry, mock_api)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
