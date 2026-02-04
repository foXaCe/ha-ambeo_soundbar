"""Base entity class for Ambeo Soundbar."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, AmbeoDevice
from .coordinator import AmbeoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class AmbeoBaseEntity(CoordinatorEntity[AmbeoDataUpdateCoordinator]):
    """Base class for Ambeo entities."""

    _attr_has_entity_name = True
    __slots__ = ("_device",)

    def __init__(
        self,
        coordinator: AmbeoDataUpdateCoordinator,
        device: AmbeoDevice,
        unique_id_suffix: str,
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = (
            f"{device.serial}_{unique_id_suffix.lower().replace(' ', '_')}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.serial)},
            name=device.name,
            manufacturer=device.manufacturer,
            model=device.model,
            sw_version=device.version,
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class AmbeoBaseLight(AmbeoBaseEntity, LightEntity):
    """Base class for Ambeo light entities."""

    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS
    __slots__ = ("_brightness_scale",)

    def __init__(
        self,
        coordinator: AmbeoDataUpdateCoordinator,
        device: AmbeoDevice,
        unique_id_suffix: str,
        brightness_scale: tuple[int, int],
    ) -> None:
        """Initialize the light entity."""
        super().__init__(coordinator, device, unique_id_suffix)
        self._brightness_scale = brightness_scale

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return None

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        return None


class AmbeoBaseSwitch(AmbeoBaseEntity, SwitchEntity):
    """Base class for Ambeo switch entities."""

    __slots__ = ()

    def __init__(
        self,
        coordinator: AmbeoDataUpdateCoordinator,
        device: AmbeoDevice,
        unique_id_suffix: str,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator, device, unique_id_suffix)

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return None


class AmbeoBaseNumber(AmbeoBaseEntity, NumberEntity):
    """Base class for Ambeo number entities."""

    __slots__ = ()

    def __init__(
        self,
        coordinator: AmbeoDataUpdateCoordinator,
        device: AmbeoDevice,
        unique_id_suffix: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, device, unique_id_suffix)

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return None


class AmbeoBaseButton(AmbeoBaseEntity, ButtonEntity):
    """Base class for Ambeo button entities."""

    __slots__ = ()

    def __init__(
        self,
        coordinator: AmbeoDataUpdateCoordinator,
        device: AmbeoDevice,
        unique_id_suffix: str,
    ) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator, device, unique_id_suffix)

    async def async_press(self) -> None:
        """Handle the button press."""
        raise NotImplementedError
