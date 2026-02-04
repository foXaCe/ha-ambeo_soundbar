"""Select platform for Ambeo Soundbar."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant

from .const import AmbeoConfigEntry
from .entity import AmbeoBaseEntity
from .util import find_id_by_title, find_title_by_id


class AmbeoAudioPreset(AmbeoBaseEntity, SelectEntity):
    """Select entity for audio presets (sound modes)."""

    def __init__(
        self,
        config_entry: AmbeoConfigEntry,
        presets: list[dict],
    ) -> None:
        """Initialize the audio preset select."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "audio_preset",
        )
        self._attr_translation_key = "audio_preset"
        self.api = config_entry.runtime_data.api
        self._presets = presets

    @property
    def current_option(self) -> str | None:
        """Return the current preset."""
        if self.coordinator.data is None:
            return None
        preset_id = self.coordinator.data.get("preset")
        return find_title_by_id(preset_id, self._presets)

    @property
    def options(self) -> list[str]:
        """Return the list of available presets."""
        titles = [preset["title"] for preset in self._presets if "title" in preset]
        return sorted(titles)

    async def async_select_option(self, option: str) -> None:
        """Change the selected preset."""
        preset_id = find_id_by_title(option, self._presets)
        if preset_id is not None:
            await self.api.set_preset(preset_id)
            await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AmbeoConfigEntry,
    async_add_entities,
) -> None:
    """Set up select entities."""
    api = config_entry.runtime_data.api

    presets = await api.get_all_presets()

    entities: list[SelectEntity] = []
    if presets:
        entities.append(AmbeoAudioPreset(config_entry, presets))

    async_add_entities(entities)
