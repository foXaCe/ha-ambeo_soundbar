"""Binary sensor platform for Ambeo Soundbar."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant

from .const import AmbeoConfigEntry, Capability
from .entity import AmbeoBaseEntity


class EcoModeSensor(AmbeoBaseEntity, BinarySensorEntity):
    """Binary sensor for Eco Mode status."""

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the Eco Mode sensor."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "eco_mode",
        )
        self._attr_translation_key = "eco_mode"

    @property
    def is_on(self) -> bool | None:
        """Return true if Eco Mode is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("eco_mode")

    @property
    def available(self) -> bool:
        """Return if the sensor is available."""
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.get("eco_mode") is not None
        )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AmbeoConfigEntry,
    async_add_entities,
) -> None:
    """Set up binary sensor entities."""
    api = config_entry.runtime_data.api
    entities: list[BinarySensorEntity] = []

    if api.has_capability(Capability.ECO_MODE):
        entities.append(EcoModeSensor(config_entry))

    async_add_entities(entities)
