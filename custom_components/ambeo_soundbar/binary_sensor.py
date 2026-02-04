"""Binary sensor platform for Ambeo Soundbar - God Tier Edition."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import AmbeoConfigEntry, Capability
from .entity import AmbeoBaseEntity


@dataclass(frozen=True, kw_only=True)
class AmbeoBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Binary sensor entity description for Ambeo Soundbar.
    
    Extends the standard BinarySensorEntityDescription with:
    - value_fn: Function to extract value from coordinator data
    - capability: Required capability for this entity
    """

    value_fn: Callable[[dict[str, Any]], bool | None]
    capability: Capability | None = None


# Entity descriptions for all binary sensors
BINARY_SENSOR_DESCRIPTIONS: tuple[AmbeoBinarySensorEntityDescription, ...] = (
    AmbeoBinarySensorEntityDescription(
        key="eco_mode",
        translation_key="eco_mode",
        device_class=BinarySensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("eco_mode"),
        capability=Capability.ECO_MODE,
    ),
)


class AmbeoBinarySensor(AmbeoBaseEntity, BinarySensorEntity):
    """Binary sensor entity for Ambeo Soundbar.
    
    Uses EntityDescription pattern for clean, maintainable code.
    """

    entity_description: AmbeoBinarySensorEntityDescription

    def __init__(
        self,
        config_entry: AmbeoConfigEntry,
        description: AmbeoBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor.
        
        Args:
            config_entry: The config entry for this entity
            description: Entity description containing configuration
        """
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            description.key,
        )
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.runtime_data.device.serial}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on.
        
        Uses the value_fn from entity_description to extract
        the current state from coordinator data.
        """
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return if entity is available.
        
        Entity is available if:
        - Coordinator has successfully updated
        - Data exists and contains valid value
        """
        if not super().available:
            return False
        if self.coordinator.data is None:
            return False
        # Check if the value exists (not just falsy)
        value = self.entity_description.value_fn(self.coordinator.data)
        return value is not None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AmbeoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities.
    
    Creates entities based on device capabilities and available data.
    Only creates entities for which the device has the required capability.
    """
    api = config_entry.runtime_data.api
    entities: list[BinarySensorEntity] = []

    for description in BINARY_SENSOR_DESCRIPTIONS:
        # Skip if capability is required but not available
        if description.capability and not api.has_capability(description.capability):
            continue

        entities.append(AmbeoBinarySensor(config_entry, description))

    async_add_entities(entities)
