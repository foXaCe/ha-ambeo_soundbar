"""Switch platform for Ambeo Soundbar."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant


from .const import AmbeoConfigEntry, Capability
from .entity import AmbeoBaseSwitch


class SubWooferStatus(AmbeoBaseSwitch):
    """Switch for subwoofer status."""

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the subwoofer switch."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "subwoofer",
        )
        self._attr_translation_key = "subwoofer"
        self.api = config_entry.runtime_data.api

    @property
    def is_on(self) -> bool | None:
        """Return true if subwoofer is on."""
        if self.coordinator.data is None:
            return None
        subwoofer_data = self.coordinator.data.get("subwoofer")
        if subwoofer_data:
            return subwoofer_data.get("status")
        return None

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the subwoofer on."""
        await self.api.set_subwoofer_status(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the subwoofer off."""
        await self.api.set_subwoofer_status(False)
        await self.coordinator.async_request_refresh()


class VoiceEnhancementMode(AmbeoBaseSwitch):
    """Switch for voice enhancement mode."""

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the voice enhancement switch."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "voice_enhancement",
        )
        self._attr_translation_key = "voice_enhancement"
        self.api = config_entry.runtime_data.api

    @property
    def is_on(self) -> bool | None:
        """Return true if voice enhancement is on."""
        if self.coordinator.data is None:
            return None
        voice_data = self.coordinator.data.get("voice_enhancement")
        if voice_data:
            return voice_data.get("enabled")
        return None

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the voice enhancement feature on."""
        await self.api.set_voice_enhancement(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the voice enhancement feature off."""
        await self.api.set_voice_enhancement(False)
        await self.coordinator.async_request_refresh()


class SoundFeedback(AmbeoBaseSwitch):
    """Switch for sound feedback."""

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the sound feedback switch."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "sound_feedback",
        )
        self._attr_translation_key = "sound_feedback"
        self.api = config_entry.runtime_data.api

    @property
    def is_on(self) -> bool | None:
        """Return true if sound feedback is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("sound_feedback")

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the sound feedback feature on."""
        await self.api.set_sound_feedback(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the sound feedback feature off."""
        await self.api.set_sound_feedback(False)
        await self.coordinator.async_request_refresh()


class AmbeoMode(AmbeoBaseSwitch):
    """Switch for Ambeo mode."""

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the Ambeo mode switch."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "ambeo_mode",
        )
        self._attr_translation_key = "ambeo_mode"
        self.api = config_entry.runtime_data.api

    @property
    def is_on(self) -> bool | None:
        """Return true if Ambeo mode is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("ambeo_mode")

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the Ambeo mode feature on."""
        await self.api.set_ambeo_mode(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the Ambeo mode feature off."""
        await self.api.set_ambeo_mode(False)
        await self.coordinator.async_request_refresh()


class NightMode(AmbeoBaseSwitch):
    """Switch for night mode."""

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the night mode switch."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "night_mode",
        )
        self._attr_translation_key = "night_mode"
        self.api = config_entry.runtime_data.api

    @property
    def is_on(self) -> bool | None:
        """Return true if night mode is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("night_mode")

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the night mode feature on."""
        await self.api.set_night_mode(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the night mode feature off."""
        await self.api.set_night_mode(False)
        await self.coordinator.async_request_refresh()


class AmbeoBluetoothPairing(AmbeoBaseSwitch):
    """Switch for Bluetooth pairing."""

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the Bluetooth pairing switch."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "bluetooth_pairing",
        )
        self._attr_translation_key = "bluetooth_pairing"
        self.api = config_entry.runtime_data.api

    @property
    def is_on(self) -> bool | None:
        """Return true if Bluetooth pairing is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("bluetooth_pairing")

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the Bluetooth pairing feature on."""
        await self.api.set_bluetooth_pairing_state(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the Bluetooth pairing feature off."""
        await self.api.set_bluetooth_pairing_state(False)
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AmbeoConfigEntry,
    async_add_entities,
) -> None:
    """Set up switch entities."""
    api = config_entry.runtime_data.api
    entities: list[SwitchEntity] = [
        NightMode(config_entry),
        AmbeoMode(config_entry),
        SoundFeedback(config_entry),
    ]

    if api.has_capability(Capability.VOICE_ENHANCEMENT_TOGGLE):
        entities.append(VoiceEnhancementMode(config_entry))

    if api.has_capability(Capability.BLUETOOTH_PAIRING):
        entities.append(AmbeoBluetoothPairing(config_entry))

    if api.has_capability(Capability.SUBWOOFER) and await api.has_subwoofer():
        entities.append(SubWooferStatus(config_entry))

    async_add_entities(entities)
