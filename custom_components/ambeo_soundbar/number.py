"""Number platform for Ambeo Soundbar."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.const import UnitOfSoundPressure
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory

from .const import AmbeoConfigEntry, Capability
from .entity import AmbeoBaseNumber


class SubWooferVolume(AmbeoBaseNumber):
    """Number entity for subwoofer volume."""

    _attr_native_step = 1
    _attr_device_class = NumberDeviceClass.SOUND_PRESSURE
    _attr_native_unit_of_measurement = UnitOfSoundPressure.DECIBEL

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the subwoofer volume."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "subwoofer_volume",
        )
        self._attr_translation_key = "subwoofer_volume"
        self.api = config_entry.runtime_data.api

    @property
    def native_min_value(self) -> float:
        """Return the min value."""
        return self.api.get_subwoofer_min_value()

    @property
    def native_max_value(self) -> float:
        """Return the max value."""
        return self.api.get_subwoofer_max_value()

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data is None:
            return None
        subwoofer_data = self.coordinator.data.get("subwoofer")
        if subwoofer_data:
            return subwoofer_data.get("volume")
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the volume of the subwoofer."""
        await self.api.set_subwoofer_volume(value)
        await self.coordinator.async_request_refresh()


class VoiceEnhancementLevel(AmbeoBaseNumber):
    """Number entity for voice enhancement level."""

    _attr_native_step = 1
    _attr_native_min_value = 0
    _attr_native_max_value = 3
    _attr_native_unit_of_measurement = "Level"

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the voice enhancement level."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "voice_enhancement_level",
        )
        self._attr_translation_key = "voice_enhancement_level"
        self.api = config_entry.runtime_data.api

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data is None:
            return None
        voice_data = self.coordinator.data.get("voice_enhancement")
        if voice_data:
            return voice_data.get("level")
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the voice enhancement level."""
        await self.api.set_voice_enhancement_level(int(value))
        await self.coordinator.async_request_refresh()


class CenterSpeakerLevel(AmbeoBaseNumber):
    """Number entity for center speaker level."""

    _attr_native_step = 1
    _attr_native_min_value = -12
    _attr_native_max_value = 12
    _attr_device_class = NumberDeviceClass.SOUND_PRESSURE
    _attr_native_unit_of_measurement = UnitOfSoundPressure.DECIBEL
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the center speaker level."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "center_speaker_level",
        )
        self._attr_translation_key = "center_speaker_level"
        self.api = config_entry.runtime_data.api

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        # Data from coordinator if available, otherwise direct API call
        return None  # Will be fetched on first update

    async def async_set_native_value(self, value: float) -> None:
        """Update the center speaker level."""
        await self.api.set_center_speaker_level(int(value))
        self._attr_native_value = int(value)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update the current center speaker level."""
        try:
            level = await self.api.get_center_speaker_level()
            self._attr_native_value = level
        except Exception:
            self._attr_native_value = None


class SideFiringLevel(AmbeoBaseNumber):
    """Number entity for side firing speakers level."""

    _attr_native_step = 1
    _attr_native_min_value = -12
    _attr_native_max_value = 12
    _attr_device_class = NumberDeviceClass.SOUND_PRESSURE
    _attr_native_unit_of_measurement = UnitOfSoundPressure.DECIBEL
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the side firing speakers level."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "side_firing_level",
        )
        self._attr_translation_key = "side_firing_level"
        self.api = config_entry.runtime_data.api

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the side firing speakers level."""
        await self.api.set_side_firing_level(int(value))
        self._attr_native_value = int(value)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update the current side firing speakers level."""
        try:
            level = await self.api.get_side_firing_level()
            self._attr_native_value = level
        except Exception:
            self._attr_native_value = None


class UpFiringLevel(AmbeoBaseNumber):
    """Number entity for up firing speakers level."""

    _attr_native_step = 1
    _attr_native_min_value = -12
    _attr_native_max_value = 12
    _attr_device_class = NumberDeviceClass.SOUND_PRESSURE
    _attr_native_unit_of_measurement = UnitOfSoundPressure.DECIBEL
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the up firing speakers level."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "up_firing_level",
        )
        self._attr_translation_key = "up_firing_level"
        self.api = config_entry.runtime_data.api

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the up firing speakers level."""
        await self.api.set_up_firing_level(int(value))
        self._attr_native_value = int(value)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update the current up firing speakers level."""
        try:
            level = await self.api.get_up_firing_level()
            self._attr_native_value = level
        except Exception:
            self._attr_native_value = None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AmbeoConfigEntry,
    async_add_entities,
) -> None:
    """Set up number entities."""
    api = config_entry.runtime_data.api
    entities: list[NumberEntity] = []

    if api.has_capability(Capability.SUBWOOFER) and await api.has_subwoofer():
        entities.append(SubWooferVolume(config_entry))

    if api.has_capability(Capability.VOICE_ENHANCEMENT_LEVEL):
        entities.append(VoiceEnhancementLevel(config_entry))

    if api.has_capability(Capability.CENTER_SPEAKER_LEVEL):
        entities.append(CenterSpeakerLevel(config_entry))

    if api.has_capability(Capability.SIDE_FIRING_LEVEL):
        entities.append(SideFiringLevel(config_entry))

    if api.has_capability(Capability.UP_FIRING_LEVEL):
        entities.append(UpFiringLevel(config_entry))

    async_add_entities(entities, update_before_add=True)
