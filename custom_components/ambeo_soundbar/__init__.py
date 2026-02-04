"""Ambeo Soundbar integration for Home Assistant."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import (
    DEFAULT_PORT,
    DOMAIN,
    MANUFACTURER,
    AmbeoConfigEntry,
    AmbeoDevice,
    AmbeoRuntimeData,
)
from .coordinator import AmbeoDataUpdateCoordinator
from .api.factory import AmbeoAPIFactory

if TYPE_CHECKING:
    from .api.impl.generic_api import AmbeoApi as AmbeoApi

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.MEDIA_PLAYER,
    Platform.SWITCH,
    Platform.LIGHT,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.BINARY_SENSOR,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: AmbeoConfigEntry) -> bool:
    """Set up Ambeo Soundbar from a config entry."""
    _LOGGER.debug("Setting up Ambeo Soundbar entry: %s", entry.entry_id)

    host = entry.options.get("host") or entry.data.get("host")
    session = async_create_clientsession(hass)

    try:
        ambeo_api = await AmbeoAPIFactory.create_api(host, DEFAULT_PORT, session, hass)

        # Fetch device info
        serial = await ambeo_api.get_serial()
        model = await ambeo_api.get_model()
        name = await ambeo_api.get_name()
        version = await ambeo_api.get_version()

    except aiohttp.ClientError as ex:
        raise ConfigEntryNotReady(f"Could not connect to {host}: {ex}") from ex
    except Exception as ex:
        raise ConfigEntryNotReady(f"Unexpected error: {ex}") from ex

    # Create device object
    device = AmbeoDevice(
        serial=serial,
        name=name,
        manufacturer=MANUFACTURER,
        model=model,
        version=version,
        host=host,
        port=DEFAULT_PORT,
    )

    # Create coordinator and do first refresh
    coordinator = AmbeoDataUpdateCoordinator(hass, entry, ambeo_api)

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        raise
    except Exception as ex:
        raise ConfigEntryNotReady(f"Failed to fetch initial data: {ex}") from ex

    # Store runtime data
    entry.runtime_data = AmbeoRuntimeData(
        coordinator=coordinator,
        api=ambeo_api,
        device=device,
    )

    # Register device in device registry
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, serial)},
        name=name,
        manufacturer=MANUFACTURER,
        model=model,
        sw_version=version,
    )

    # Forward to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Add update listener for options
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    _LOGGER.info("Ambeo Soundbar %s setup complete", name)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: AmbeoConfigEntry) -> bool:
    """Unload Ambeo Soundbar config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_reload_entry(hass: HomeAssistant, entry: AmbeoConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
