"""Button platform for Ambeo Soundbar - God Tier Edition.

Implements button entities using the EntityDescription pattern for
clean, maintainable code with proper device classes.
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import AmbeoConfigEntry, Capability
from .entity import AmbeoBaseEntity
from .api.impl.generic_api import AmbeoApi


@dataclass(frozen=True, kw_only=True)
class AmbeoButtonEntityDescription(ButtonEntityDescription):
    """Button entity description for Ambeo Soundbar.

    Extends the standard ButtonEntityDescription with:
    - press_fn: Async function to execute when button is pressed
    - capability: Required capability for this entity
    """

    press_fn: Callable[[AmbeoApi], Coroutine[Any, Any, None]]
    capability: Capability | None = None


# Entity descriptions for all button entities
BUTTON_DESCRIPTIONS: tuple[AmbeoButtonEntityDescription, ...] = (
    AmbeoButtonEntityDescription(
        key="reboot",
        translation_key="reboot",
        device_class=ButtonDeviceClass.RESTART,
        icon="mdi:restart",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        press_fn=lambda api: api.reboot(),
    ),
    AmbeoButtonEntityDescription(
        key="reset_expert_settings",
        translation_key="reset_expert_settings",
        device_class=ButtonDeviceClass.RESTART,
        icon="mdi:restore",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        press_fn=lambda api: api.reset_expert_settings(),
        capability=Capability.RESET_EXPERT_SETTINGS,
    ),
)


class AmbeoButton(AmbeoBaseEntity, ButtonEntity):
    """Button entity for Ambeo Soundbar.

    Uses EntityDescription pattern for clean, maintainable code.
    """

    entity_description: AmbeoButtonEntityDescription

    def __init__(
        self,
        config_entry: AmbeoConfigEntry,
        description: AmbeoButtonEntityDescription,
    ) -> None:
        """Initialize the button.

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
        self._attr_unique_id = (
            f"{config_entry.runtime_data.device.serial}_{description.key}"
        )
        self.api = config_entry.runtime_data.api

    async def async_press(self) -> None:
        """Handle the button press.

        Calls the press_fn from entity_description to execute
        the appropriate action on the device.
        """
        await self.entity_description.press_fn(self.api)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AmbeoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities.

    Creates entities based on device capabilities. Each entity is
    only created if the device supports the required capability.
    """
    api = config_entry.runtime_data.api
    entities: list[ButtonEntity] = []

    for description in BUTTON_DESCRIPTIONS:
        # Skip if capability is required but not available
        if description.capability and not api.has_capability(description.capability):
            continue

        entities.append(AmbeoButton(config_entry, description))

    async_add_entities(entities)
