"""Select entities for Ambeo Soundbar."""

import logging
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AmbeoBaseEntity

if TYPE_CHECKING:
    from .api.impl.generic_api import AmbeoApi

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ambeo select entities."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    device = data["device"]
    api = data["api"]

    # Fetch available presets from the API
    presets = await api.get_all_presets()

    if presets:
        async_add_entities([AmbeoPresetSelect(device, api, presets)])


class AmbeoPresetSelect(AmbeoBaseEntity, SelectEntity):
    """Representation of an Ambeo preset selector."""

    def __init__(self, device, api: "AmbeoApi", presets):
        """Initialize the preset selector."""
        super().__init__(device, api, "Audio Preset", "audio_preset")
        self._presets = presets
        self._attr_options = [preset["title"] for preset in presets]
        self._current_preset = None
        self._attr_icon = "mdi:equalizer"

    @property
    def current_option(self) -> str | None:
        """Return the current selected preset."""
        if self._current_preset is not None:
            for preset in self._presets:
                if preset["id"] == self._current_preset:
                    return preset["title"]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected preset."""
        for preset in self._presets:
            if preset["title"] == option:
                await self.api.set_preset(preset["id"])
                self._current_preset = preset["id"]
                self.async_write_ha_state()
                _LOGGER.debug("Preset changed to: %s", option)
                return

        _LOGGER.warning("Unknown preset selected: %s", option)

    async def async_update(self):
        """Update the current preset from the API."""
        try:
            self._current_preset = await self.api.get_current_preset()
        except Exception:
            _LOGGER.exception("Failed to update preset")
