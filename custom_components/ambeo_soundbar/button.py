"""Button platform for Ambeo Soundbar."""

from __future__ import annotations

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory

from .const import AmbeoConfigEntry, Capability
from .entity import AmbeoBaseButton


class AmbeoReboot(AmbeoBaseButton):
    """Button to reboot the Ambeo device."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_device_class = ButtonDeviceClass.RESTART

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the reboot button."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "reboot",
        )
        self._attr_translation_key = "reboot"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.api.reboot()


class ResetExpertSettings(AmbeoBaseButton):
    """Button to reset expert audio settings."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_device_class = ButtonDeviceClass.RESTART

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the reset expert settings button."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "reset_expert_settings",
        )
        self._attr_translation_key = "reset_expert_settings"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.api.reset_expert_settings()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AmbeoConfigEntry,
    async_add_entities,
) -> None:
    """Set up button entities."""
    api = config_entry.runtime_data.api
    entities: list[ButtonEntity] = [AmbeoReboot(config_entry)]

    if api.has_capability(Capability.RESET_EXPERT_SETTINGS):
        entities.append(ResetExpertSettings(config_entry))

    async_add_entities(entities)
