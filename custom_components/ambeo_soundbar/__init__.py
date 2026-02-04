import logging
from pathlib import Path

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.service import async_register_admin_service
import voluptuous as vol

from .api.factory import AmbeoAPIFactory
from .const import CONFIG_HOST, DEFAULT_PORT, DOMAIN, MANUFACTURER, Capability
from .coordinator import AmbeoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Service schemas
SERVICE_SET_EXPERT_AUDIO_LEVELS_SCHEMA = vol.Schema(
    {
        vol.Optional("voice_enhancement_level"): vol.All(
            vol.Coerce(int), vol.Range(min=-6, max=6)
        ),
        vol.Optional("center_speaker_level"): vol.All(
            vol.Coerce(int), vol.Range(min=-6, max=6)
        ),
        vol.Optional("side_firing_level"): vol.All(
            vol.Coerce(int), vol.Range(min=-6, max=6)
        ),
        vol.Optional("up_firing_level"): vol.All(
            vol.Coerce(int), vol.Range(min=-6, max=6)
        ),
    }
)

SERVICE_SET_EQ_PRESET_SCHEMA = vol.Schema(
    {
        vol.Required("preset"): cv.string,
    }
)

PRESET_MAP = {
    "Neutral": 0,
    "Movies": 1,
    "Sport": 2,
    "News": 3,
    "Music": 4,
}


class AmbeoDevice:
    def __init__(self, serial, name, manufacturer, model, version, host, port):
        self._serial = serial
        self.name = name
        self.manufacturer = manufacturer
        self.model = model
        self.version = version
        self.host = host
        self.port = port

    @property
    def serial(self):
        return self._serial


async def _async_entry_updated(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle entry updates."""
    host = config_entry.options.get(CONFIG_HOST)
    hass.data[DOMAIN][config_entry.entry_id]["api"].set_endpoint(host)
    await hass.config_entries.async_reload(config_entry.entry_id)
    _LOGGER.info("Successfully updated configuration entries")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug("Starting configuration of ambeo entry")
    entry.async_on_unload(entry.add_update_listener(_async_entry_updated))

    host = entry.options.get(CONFIG_HOST, entry.data.get(CONFIG_HOST))
    session = async_create_clientsession(hass)

    try:
        ambeo_api = await AmbeoAPIFactory.create_api(host, DEFAULT_PORT, session, hass)
        serial = await ambeo_api.get_serial()
        model = await ambeo_api.get_model()
        name = await ambeo_api.get_name()
        version = await ambeo_api.get_version()
    except (aiohttp.ClientError, OSError, TimeoutError) as ex:
        # Device is offline or unreachable - log at info level only
        _LOGGER.info("AMBEO Soundbar at %s is currently unavailable", host)
        raise ConfigEntryNotReady(
            f"AMBEO Soundbar at {host} is unavailable. Please check the device is powered on and connected to the network."
        ) from ex

    device = AmbeoDevice(serial, name, MANUFACTURER, model, version, host, DEFAULT_PORT)

    # Initialize data update coordinator for adaptive polling
    coordinator = AmbeoDataUpdateCoordinator(hass, ambeo_api, entry.entry_id)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": ambeo_api,
        "device": device,
        "coordinator": coordinator,
    }
    _LOGGER.debug("Data initialized with adaptive polling coordinator")

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, serial)},
        name=name,
        manufacturer=MANUFACTURER,
        model=model,
        sw_version=version,
        configuration_url=f"http://{host}",
    )

    # Register services (only once for the domain)
    if not hass.services.has_service(DOMAIN, "set_expert_audio_levels"):
        await _async_setup_services(hass)

    await hass.config_entries.async_forward_entry_setups(
        entry,
        [
            "media_player",
            "switch",
            "light",
            "button",
            "number",
            "binary_sensor",
            "select",
        ],
    )

    return True


async def _async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Ambeo Soundbar integration."""

    async def handle_set_expert_audio_levels(call: ServiceCall) -> None:
        """Handle the set_expert_audio_levels service call."""
        # Get the first entry's API (services work on all devices)
        for _entry_id, data in hass.data[DOMAIN].items():
            api = data["api"]

            # Check capabilities
            if call.data.get("voice_enhancement_level") is not None:
                if api.has_capability(Capability.VOICE_ENHANCEMENT_LEVEL):
                    await api.set_voice_enhancement_level(
                        call.data["voice_enhancement_level"]
                    )
                else:
                    _LOGGER.warning(
                        "Voice enhancement level not supported on this device"
                    )

            if call.data.get("center_speaker_level") is not None:
                if api.has_capability(Capability.CENTER_SPEAKER_LEVEL):
                    await api.set_center_speaker_level(
                        call.data["center_speaker_level"]
                    )
                else:
                    _LOGGER.warning("Center speaker level not supported on this device")

            if call.data.get("side_firing_level") is not None:
                if api.has_capability(Capability.SIDE_FIRING_LEVEL):
                    await api.set_side_firing_level(call.data["side_firing_level"])
                else:
                    _LOGGER.warning("Side firing level not supported on this device")

            if call.data.get("up_firing_level") is not None:
                if api.has_capability(Capability.UP_FIRING_LEVEL):
                    await api.set_up_firing_level(call.data["up_firing_level"])
                else:
                    _LOGGER.warning("Up firing level not supported on this device")

    async def handle_reset_expert_settings(_call: ServiceCall) -> None:
        """Handle the reset_expert_settings service call."""
        for _entry_id, data in hass.data[DOMAIN].items():
            api = data["api"]
            if api.has_capability(Capability.RESET_EXPERT_SETTINGS):
                await api.reset_expert_settings()
                _LOGGER.info("Expert settings reset to defaults")
            else:
                _LOGGER.warning("Reset expert settings not supported on this device")

    async def handle_set_eq_preset(call: ServiceCall) -> None:
        """Handle the set_eq_preset service call."""
        preset_name = call.data.get("preset")
        preset_id = PRESET_MAP.get(preset_name)

        if preset_id is None:
            _LOGGER.error("Unknown preset: %s", preset_name)
            return

        for _entry_id, data in hass.data[DOMAIN].items():
            api = data["api"]
            await api.set_preset(preset_id)
            _LOGGER.info("EQ preset set to: %s", preset_name)

    # Register services
    hass.services.async_register(
        DOMAIN,
        "set_expert_audio_levels",
        handle_set_expert_audio_levels,
        schema=SERVICE_SET_EXPERT_AUDIO_LEVELS_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "reset_expert_settings",
        handle_reset_expert_settings,
    )

    hass.services.async_register(
        DOMAIN,
        "set_eq_preset",
        handle_set_eq_preset,
        schema=SERVICE_SET_EQ_PRESET_SCHEMA,
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle integration unload"""
    # Unload configuration
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        [
            "media_player",
            "switch",
            "light",
            "button",
            "number",
            "binary_sensor",
            "select",
        ],
    )
    if unload_ok and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)

        # If this was the last entry, unregister services
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "set_expert_audio_levels")
            hass.services.async_remove(DOMAIN, "reset_expert_settings")
            hass.services.async_remove(DOMAIN, "set_eq_preset")

    return unload_ok
