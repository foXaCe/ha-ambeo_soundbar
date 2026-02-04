"""Data update coordinator for Ambeo Soundbar with adaptive polling."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Polling intervals
POLLING_INTERVAL_PLAYING = timedelta(seconds=5)  # Fast when playing
POLLING_INTERVAL_IDLE = timedelta(seconds=30)  # Normal when idle
POLLING_INTERVAL_STANDBY = timedelta(seconds=60)  # Slow when in standby


class AmbeoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Ambeo data with adaptive polling intervals."""

    def __init__(
        self,
        hass: HomeAssistant,
        api,
        entry_id: str,
    ) -> None:
        """Initialize the coordinator."""
        self.api = api
        self.entry_id = entry_id
        self._last_state = None
        self._consecutive_errors = 0
        self._max_consecutive_errors = 5

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry_id}",
            update_interval=POLLING_INTERVAL_IDLE,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API with error handling and adaptive interval."""
        try:
            # Fetch current state data
            data = await self._fetch_device_data()

        except Exception as err:
            self._consecutive_errors += 1

            if self._consecutive_errors >= self._max_consecutive_errors:
                # Log at info level only to avoid polluting logs
                _LOGGER.info(
                    "AMBEO Soundbar unavailable after %d consecutive attempts. Slowing down polling.",
                    self._consecutive_errors,
                )
                # Slow down polling when device is unreachable
                self.update_interval = POLLING_INTERVAL_STANDBY
            else:
                # Use debug level for transient errors
                _LOGGER.debug(
                    "Error fetching data (attempt %d/%d): %s",
                    self._consecutive_errors,
                    self._max_consecutive_errors,
                    err,
                )

            raise UpdateFailed("Device unavailable") from err

        else:
            # Reset error counter on success
            self._consecutive_errors = 0

            # Adjust polling interval based on state
            self._adjust_polling_interval(data)

            return data

    async def _fetch_device_data(self) -> dict[str, Any]:
        """Fetch all device data in one go to minimize API calls."""
        data = {}

        # Fetch power state
        try:
            data["power_state"] = await self.api.get_state()
        except Exception as ex:
            _LOGGER.debug("Failed to get power state: %s", ex)
            data["power_state"] = None

        # Only fetch other data if device is online
        if data["power_state"] not in [None, "standby"]:
            try:
                data["volume"] = await self.api.get_volume()
            except Exception:
                data["volume"] = None

            try:
                data["mute"] = await self.api.is_mute()
            except Exception:
                data["mute"] = None

            try:
                data["current_source"] = await self.api.get_current_source()
            except Exception:
                data["current_source"] = None

            try:
                data["player_data"] = await self.api.player_data()
            except Exception:
                data["player_data"] = None

        return data

    def _adjust_polling_interval(self, data: dict[str, Any]) -> None:
        """Adjust polling interval based on device state."""
        power_state = data.get("power_state")
        player_data = data.get("player_data", {})
        playback_state = player_data.get("state") if player_data else None

        # Determine optimal polling interval
        if power_state == "standby":
            new_interval = POLLING_INTERVAL_STANDBY
            state_description = "standby"
        elif playback_state == "playing":
            new_interval = POLLING_INTERVAL_PLAYING
            state_description = "playing"
        else:
            new_interval = POLLING_INTERVAL_IDLE
            state_description = "idle"

        # Update interval if changed
        if self.update_interval != new_interval:
            _LOGGER.debug(
                "Adjusting poll interval from %s to %s (state: %s)",
                self.update_interval,
                new_interval,
                state_description,
            )
            self.update_interval = new_interval

        self._last_state = playback_state
