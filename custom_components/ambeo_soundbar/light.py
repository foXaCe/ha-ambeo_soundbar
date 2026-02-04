"""Light platform for Ambeo Soundbar."""

from __future__ import annotations

import math
from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS
from homeassistant.core import HomeAssistant
from homeassistant.util.color import brightness_to_value, value_to_brightness

from .const import (
    BRIGHTNESS_SCALE,
    BRIGHTNESS_SCALE_AMBEO_MAX_DISPLAY,
    BRIGHTNESS_SCALE_AMBEO_MAX_LOGO,
    DEFAULT_BRIGHTNESS,
    DEFAULT_BRIGHTNESS_AMBEO_MAX,
    AmbeoConfigEntry,
    Capability,
)
from .entity import AmbeoBaseLight


class LEDBar(AmbeoBaseLight):
    """Light entity for LED Bar."""

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the LED Bar light."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "led_bar",
            BRIGHTNESS_SCALE,
        )
        self._attr_translation_key = "led_bar"
        self.api = config_entry.runtime_data.api

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        if self.coordinator.data is None:
            return None
        brightness_val = self.coordinator.data.get("led_bar_brightness")
        if brightness_val is None:
            return None
        return super().brightness if hasattr(super(), "brightness") else brightness_val

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        if self.coordinator.data is None:
            return None
        brightness_val = self.coordinator.data.get("led_bar_brightness")
        return brightness_val is not None and brightness_val > 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = math.floor(
                brightness_to_value(BRIGHTNESS_SCALE, kwargs[ATTR_BRIGHTNESS])
            )
        else:
            brightness = DEFAULT_BRIGHTNESS
        await self.api.set_led_bar_brightness(brightness)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.api.set_led_bar_brightness(0)
        await self.coordinator.async_request_refresh()


class CodecLED(AmbeoBaseLight):
    """Light entity for Codec LED."""

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the Codec LED light."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "codec_led",
            BRIGHTNESS_SCALE,
        )
        self._attr_translation_key = "codec_led"
        self.api = config_entry.runtime_data.api

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        if self.coordinator.data is None:
            return None
        brightness_val = self.coordinator.data.get("codec_led_brightness")
        return brightness_val is not None and brightness_val > 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = math.floor(
                brightness_to_value(BRIGHTNESS_SCALE, kwargs[ATTR_BRIGHTNESS])
            )
        else:
            brightness = DEFAULT_BRIGHTNESS
        await self.api.set_codec_led_brightness(brightness)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.api.set_codec_led_brightness(0)
        await self.coordinator.async_request_refresh()


class AmbeoMaxLogo(AmbeoBaseLight):
    """Light entity for Ambeo Max Logo."""

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the Ambeo Max Logo light."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "ambeo_max_logo",
            BRIGHTNESS_SCALE_AMBEO_MAX_LOGO,
        )
        self._attr_translation_key = "ambeo_max_logo"
        self.api = config_entry.runtime_data.api

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        if self.coordinator.data is None:
            return None
        logo_data = self.coordinator.data.get("logo_state")
        if logo_data:
            return logo_data.get("state") and logo_data.get("brightness", 0) > 0
        return None

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        if self.coordinator.data is None:
            return None
        logo_data = self.coordinator.data.get("logo_state")
        if logo_data:
            brightness_val = logo_data.get("brightness")
            if brightness_val is not None:
                return value_to_brightness(BRIGHTNESS_SCALE_AMBEO_MAX_LOGO, brightness_val)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = math.floor(
                brightness_to_value(
                    BRIGHTNESS_SCALE_AMBEO_MAX_LOGO, kwargs[ATTR_BRIGHTNESS]
                )
            )
        else:
            brightness = DEFAULT_BRIGHTNESS_AMBEO_MAX
        await self.api.set_logo_brightness(brightness)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.api.set_logo_brightness(0)
        await self.coordinator.async_request_refresh()


class AmbeoMaxDisplay(AmbeoBaseLight):
    """Light entity for Ambeo Max Display."""

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the Ambeo Max Display light."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "ambeo_max_display",
            BRIGHTNESS_SCALE_AMBEO_MAX_DISPLAY,
        )
        self._attr_translation_key = "ambeo_max_display"
        self.api = config_entry.runtime_data.api

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        if self.coordinator.data is None:
            return None
        brightness_val = self.coordinator.data.get("display_brightness")
        return brightness_val is not None and brightness_val > 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = math.floor(
                brightness_to_value(
                    BRIGHTNESS_SCALE_AMBEO_MAX_DISPLAY, kwargs[ATTR_BRIGHTNESS]
                )
            )
        else:
            brightness = DEFAULT_BRIGHTNESS_AMBEO_MAX
        await self.api.set_display_brightness(brightness)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.api.set_display_brightness(0)
        await self.coordinator.async_request_refresh()


class AmbeoLogo(AmbeoBaseLight):
    """Light entity for Ambeo Logo."""

    def __init__(self, config_entry: AmbeoConfigEntry) -> None:
        """Initialize the Ambeo Logo light."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "ambeo_logo",
            BRIGHTNESS_SCALE,
        )
        self._attr_translation_key = "ambeo_logo"
        self.api = config_entry.runtime_data.api

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        if self.coordinator.data is None:
            return None
        logo_data = self.coordinator.data.get("logo_state")
        if logo_data:
            return logo_data.get("state") and logo_data.get("brightness", 0) > 0
        return None

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        if self.coordinator.data is None:
            return None
        logo_data = self.coordinator.data.get("logo_state")
        if logo_data:
            brightness_val = logo_data.get("brightness")
            if brightness_val is not None:
                return value_to_brightness(self._brightness_scale, brightness_val)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = math.floor(
                brightness_to_value(BRIGHTNESS_SCALE, kwargs[ATTR_BRIGHTNESS])
            )
        else:
            brightness = DEFAULT_BRIGHTNESS
        await self.api.change_logo_state(True)
        await self.api.set_logo_brightness(brightness)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.api.change_logo_state(False)
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AmbeoConfigEntry,
    async_add_entities,
) -> None:
    """Set up light entities."""
    api = config_entry.runtime_data.api
    entities = []

    if api.has_capability(Capability.AMBEO_LOGO):
        entities.append(AmbeoLogo(config_entry))

    if api.has_capability(Capability.LED_BAR):
        entities.append(LEDBar(config_entry))

    if api.has_capability(Capability.CODEC_LED):
        entities.append(CodecLED(config_entry))

    if api.has_capability(Capability.MAX_LOGO):
        entities.append(AmbeoMaxLogo(config_entry))

    if api.has_capability(Capability.MAX_DISPLAY):
        entities.append(AmbeoMaxDisplay(config_entry))

    async_add_entities(entities)
