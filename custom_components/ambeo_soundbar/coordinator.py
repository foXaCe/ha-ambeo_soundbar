"""DataUpdateCoordinator for Ambeo Soundbar."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, AmbeoConfigEntry, Capability
from .exceptions import AmbeoAuthError, AmbeoConnectionError

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)


class AmbeoDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage data fetching from Ambeo device."""

    config_entry: AmbeoConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: AmbeoConfigEntry,
        api,
    ) -> None:
        """Initialize the coordinator."""
        self.config_entry = entry
        self.api = api

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            request_refresh_debouncer=Debouncer(
                hass,
                _LOGGER,
                cooldown=entry.data.get("debounce_cooldown", 0) or 1.5,
                immediate=False,
            ),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        try:
            data: dict[str, Any] = {}

            # Fetch all relevant data in parallel
            results = await asyncio.gather(
                self._fetch_volume(),
                self._fetch_mute(),
                self._fetch_power_state(),
                self._fetch_source(),
                self._fetch_preset(),
                self._fetch_ambeo_mode(),
                self._fetch_night_mode(),
                self._fetch_sound_feedback(),
                self._fetch_bluetooth_pairing(),
                self._fetch_logo_brightness(),
                self._fetch_led_bar_brightness(),
                self._fetch_subwoofer(),
                self._fetch_voice_enhancement(),
                self._fetch_codec_led_brightness(),
                self._fetch_display_brightness(),
                self._fetch_eco_mode(),
                return_exceptions=True,
            )

            keys = [
                "volume",
                "mute",
                "power_state",
                "source",
                "preset",
                "ambeo_mode",
                "night_mode",
                "sound_feedback",
                "bluetooth_pairing",
                "logo_state",
                "led_bar_brightness",
                "subwoofer",
                "voice_enhancement",
                "codec_led_brightness",
                "display_brightness",
                "eco_mode",
            ]

            for key, result in zip(keys, results, strict=False):
                if isinstance(result, Exception):
                    if isinstance(result, AmbeoAuthError):
                        raise ConfigEntryAuthFailed from result
                    _LOGGER.warning("Failed to fetch %s: %s", key, result)
                    data[key] = None
                else:
                    data[key] = result

            return data

        except AmbeoAuthError as err:
            raise ConfigEntryAuthFailed from err
        except AmbeoConnectionError as err:
            raise UpdateFailed(str(err)) from err
        except Exception as err:
            _LOGGER.exception("Unexpected error updating data")
            raise UpdateFailed(str(err)) from err

    async def _fetch_volume(self) -> int | None:
        """Fetch volume level."""
        return await self.api.get_volume()

    async def _fetch_mute(self) -> bool | None:
        """Fetch mute state."""
        return await self.api.is_mute()

    async def _fetch_power_state(self) -> str | None:
        """Fetch power state."""
        return await self.api.get_state()

    async def _fetch_source(self) -> str | None:
        """Fetch current source."""
        return await self.api.get_current_source()

    async def _fetch_preset(self) -> str | None:
        """Fetch current preset."""
        return await self.api.get_current_preset()

    async def _fetch_ambeo_mode(self) -> bool | None:
        """Fetch Ambeo mode state."""
        if self.api.has_capability(Capability.AMBEO_MODE):
            return await self.api.get_ambeo_mode()
        return None

    async def _fetch_night_mode(self) -> bool | None:
        """Fetch night mode state."""
        if self.api.has_capability(Capability.NIGHT_MODE):
            return await self.api.get_night_mode()
        return None

    async def _fetch_sound_feedback(self) -> bool | None:
        """Fetch sound feedback state."""
        if self.api.has_capability(Capability.SOUND_FEEDBACK):
            return await self.api.get_sound_feedback()
        return None

    async def _fetch_bluetooth_pairing(self) -> bool | None:
        """Fetch Bluetooth pairing state."""
        if self.api.has_capability(Capability.BLUETOOTH_PAIRING):
            return await self.api.get_bluetooth_pairing_state()
        return None

    async def _fetch_logo_brightness(self) -> dict[str, Any] | None:
        """Fetch logo brightness and state."""
        if self.api.has_capability(Capability.AMBEO_LOGO):
            return {
                "brightness": await self.api.get_logo_brightness(),
                "state": await self.api.get_logo_state(),
            }
        return None

    async def _fetch_led_bar_brightness(self) -> int | None:
        """Fetch LED bar brightness."""
        if self.api.has_capability(Capability.LED_BAR):
            return await self.api.get_led_bar_brightness()
        return None

    async def _fetch_subwoofer(self) -> dict[str, Any] | None:
        """Fetch subwoofer data."""
        if self.api.has_capability(Capability.SUBWOOFER):
            return {
                "status": await self.api.get_subwoofer_status(),
                "volume": await self.api.get_subwoofer_volume(),
            }
        return None

    async def _fetch_voice_enhancement(self) -> dict[str, Any] | None:
        """Fetch voice enhancement data."""
        if self.api.has_capability(Capability.VOICE_ENHANCEMENT_TOGGLE):
            return {
                "enabled": await self.api.get_voice_enhancement(),
                "level": await self.api.get_voice_enhancement_level()
                if self.api.has_capability(Capability.VOICE_ENHANCEMENT_LEVEL)
                else None,
            }
        return None

    async def _fetch_codec_led_brightness(self) -> int | None:
        """Fetch codec LED brightness."""
        if self.api.has_capability(Capability.CODEC_LED):
            return await self.api.get_codec_led_brightness()
        return None

    async def _fetch_display_brightness(self) -> int | None:
        """Fetch display brightness."""
        if self.api.has_capability(Capability.MAX_DISPLAY):
            return await self.api.get_display_brightness()
        return None

    async def _fetch_eco_mode(self) -> bool | None:
        """Fetch eco mode state."""
        if self.api.has_capability(Capability.ECO_MODE):
            return await self.api.get_eco_mode()
        return None
