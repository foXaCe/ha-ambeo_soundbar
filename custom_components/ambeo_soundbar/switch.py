"""Switch platform for Ambeo Soundbar - God Tier Edition.

Implements switch entities using the EntityDescription pattern for
clean, maintainable code with proper device classes and capabilities.
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import AmbeoConfigEntry, Capability
from .entity import AmbeoBaseEntity
from .api.impl.generic_api import AmbeoApi


@dataclass(frozen=True, kw_only=True)
class AmbeoSwitchEntityDescription(SwitchEntityDescription):
    """Switch entity description for Ambeo Soundbar.
    
    Extends the standard SwitchEntityDescription with:
    - value_fn: Function to extract current state from coordinator data
    - turn_on_fn: Async function to turn the switch on
    - turn_off_fn: Async function to turn the switch off
    - capability: Required capability for this entity
    - check_exists_fn: Optional function to check if entity should be created
    """

    value_fn: Callable[[dict[str, Any]], bool | None]
    turn_on_fn: Callable[[AmbeoApi], Coroutine[Any, Any, None]]
    turn_off_fn: Callable[[AmbeoApi], Coroutine[Any, Any, None]]
    capability: Capability | None = None
    check_exists_fn: Callable[[AmbeoApi], Coroutine[Any, Any, bool]] | None = None


# Entity descriptions for all switch entities
SWITCH_DESCRIPTIONS: tuple[AmbeoSwitchEntityDescription, ...] = (
    AmbeoSwitchEntityDescription(
        key="night_mode",
        translation_key="night_mode",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:weather-night",
        value_fn=lambda data: data.get("night_mode"),
        turn_on_fn=lambda api: api.set_night_mode(True),
        turn_off_fn=lambda api: api.set_night_mode(False),
        capability=Capability.NIGHT_MODE,
    ),
    AmbeoSwitchEntityDescription(
        key="ambeo_mode",
        translation_key="ambeo_mode",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:surround-sound",
        value_fn=lambda data: data.get("ambeo_mode"),
        turn_on_fn=lambda api: api.set_ambeo_mode(True),
        turn_off_fn=lambda api: api.set_ambeo_mode(False),
        capability=Capability.AMBEO_MODE,
    ),
    AmbeoSwitchEntityDescription(
        key="sound_feedback",
        translation_key="sound_feedback",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:volume-high",
        value_fn=lambda data: data.get("sound_feedback"),
        turn_on_fn=lambda api: api.set_sound_feedback(True),
        turn_off_fn=lambda api: api.set_sound_feedback(False),
        capability=Capability.SOUND_FEEDBACK,
    ),
    AmbeoSwitchEntityDescription(
        key="voice_enhancement",
        translation_key="voice_enhancement",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:account-voice",
        value_fn=lambda data: data.get("voice_enhancement", {}).get("enabled")
        if isinstance(data.get("voice_enhancement"), dict)
        else data.get("voice_enhancement"),
        turn_on_fn=lambda api: api.set_voice_enhancement(True),
        turn_off_fn=lambda api: api.set_voice_enhancement(False),
        capability=Capability.VOICE_ENHANCEMENT_TOGGLE,
    ),
    AmbeoSwitchEntityDescription(
        key="bluetooth_pairing",
        translation_key="bluetooth_pairing",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:bluetooth",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("bluetooth_pairing"),
        turn_on_fn=lambda api: api.set_bluetooth_pairing_state(True),
        turn_off_fn=lambda api: api.set_bluetooth_pairing_state(False),
        capability=Capability.BLUETOOTH_PAIRING,
    ),
    AmbeoSwitchEntityDescription(
        key="subwoofer",
        translation_key="subwoofer",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:speaker",
        value_fn=lambda data: data.get("subwoofer", {}).get("status")
        if isinstance(data.get("subwoofer"), dict)
        else data.get("subwoofer"),
        turn_on_fn=lambda api: api.set_subwoofer_status(True),
        turn_off_fn=lambda api: api.set_subwoofer_status(False),
        capability=Capability.SUBWOOFER,
        check_exists_fn=lambda api: api.has_subwoofer(),
    ),
)


class AmbeoSwitch(AmbeoBaseEntity, SwitchEntity):
    """Switch entity for Ambeo Soundbar.
    
    Uses EntityDescription pattern for clean, maintainable code.
    All state changes automatically trigger coordinator refresh.
    """

    entity_description: AmbeoSwitchEntityDescription

    def __init__(
        self,
        config_entry: AmbeoConfigEntry,
        description: AmbeoSwitchEntityDescription,
    ) -> None:
        """Initialize the switch.
        
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
        self.api = config_entry.runtime_data.api

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on.
        
        Uses the value_fn from entity_description to extract
        the current state from coordinator data.
        """
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on.
        
        Calls the turn_on_fn from entity_description and
        refreshes coordinator data to update UI.
        """
        await self.entity_description.turn_on_fn(self.api)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off.
        
        Calls the turn_off_fn from entity_description and
        refreshes coordinator data to update UI.
        """
        await self.entity_description.turn_off_fn(self.api)
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AmbeoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities.
    
    Creates entities based on device capabilities. Each entity is
    only created if the device supports the required capability.
    For subwoofer, also checks if a subwoofer is actually connected.
    """
    api = config_entry.runtime_data.api
    entities: list[SwitchEntity] = []

    for description in SWITCH_DESCRIPTIONS:
        # Skip if capability is required but not available
        if description.capability and not api.has_capability(description.capability):
            continue

        # Check if entity should exist (e.g., subwoofer connected)
        if description.check_exists_fn is not None:
            try:
                if not await description.check_exists_fn(api):
                    continue
            except Exception:
                # If check fails, skip entity
                continue

        entities.append(AmbeoSwitch(config_entry, description))

    async_add_entities(entities)
