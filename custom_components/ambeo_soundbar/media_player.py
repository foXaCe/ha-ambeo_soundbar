"""Media player platform for Ambeo Soundbar."""

from __future__ import annotations

import asyncio
import copy
import logging

from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.const import STATE_IDLE, STATE_ON, STATE_PAUSED, STATE_PLAYING
from homeassistant.core import HomeAssistant

from .const import AmbeoConfigEntry, Capability
from .entity import AmbeoBaseEntity
from .util import find_id_by_title, find_title_by_id

_LOGGER = logging.getLogger(__name__)

STATE_DICT = {
    "playing": STATE_PLAYING,
    "paused": STATE_PAUSED,
    "stopped": STATE_IDLE,
    "online": STATE_ON,
    "networkStandby": STATE_IDLE,
}


class AmbeoMediaPlayer(AmbeoBaseEntity, MediaPlayerEntity):
    """Representation of an Ambeo device as a media player entity."""

    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.SELECT_SOUND_MODE
        | MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
    )
    __slots__ = (
        "api",
        "_sources",
        "_presets",
        "_max_volume",
        "_debounce_cooldown",
        "_debounce_task",
        "_debounce_start",
        "_update_lock",
    )

    def __init__(
        self,
        config_entry: AmbeoConfigEntry,
        sources: list[dict],
        presets: list[dict],
    ) -> None:
        """Initialize the media player."""
        super().__init__(
            config_entry.runtime_data.coordinator,
            config_entry.runtime_data.device,
            "player",
        )
        self._attr_translation_key = "player"
        self.api = config_entry.runtime_data.api
        self._sources = sources
        self._presets = presets
        self._max_volume = 100
        self._debounce_cooldown = config_entry.options.get("debounce_cooldown", 0)
        self._debounce_task: asyncio.Task | None = None
        self._debounce_start: float = 0
        self._update_lock: asyncio.Lock | None = None

        if self.api.has_capability(Capability.STANDBY):
            self._attr_supported_features |= (
                MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF
            )
            STATE_DICT["networkStandby"] = MediaPlayerState.STANDBY

        if self.debounce_mode_activated:
            self._update_lock = asyncio.Lock()

    @property
    def debounce_mode_activated(self) -> bool:
        """Return if debounce mode is activated."""
        return self.api.support_debounce_mode() and self._debounce_cooldown > 0

    @property
    def state(self) -> MediaPlayerState | str | None:
        """Return the state of the device."""
        if self.coordinator.data is None:
            return None

        power_state = self.coordinator.data.get("power_state")
        if power_state == "online":
            # Player state from player_data
            player_data = self.coordinator.data.get("player_data")
            if player_data:
                player_state = player_data.get("state")
                return STATE_DICT.get(player_state, STATE_IDLE)
            return STATE_ON

        return STATE_DICT.get(power_state, STATE_IDLE)

    @property
    def volume_level(self) -> float | None:
        """Return the volume level (0-1)."""
        if self.coordinator.data is None:
            return None
        volume = self.coordinator.data.get("volume")
        if volume is not None:
            return volume / self._max_volume
        return None

    @property
    def volume_step(self) -> float:
        """Return the volume step."""
        return self.api.get_volume_step()

    @property
    def is_volume_muted(self) -> bool | None:
        """Return if volume is muted."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("mute")

    @property
    def source(self) -> str | None:
        """Return the current source."""
        if self.coordinator.data is None:
            return None
        source_id = self.coordinator.data.get("source")
        return find_title_by_id(source_id, self._sources)

    @property
    def source_list(self) -> list[str]:
        """Return the list of available sources."""
        titles = [entry["title"] for entry in self._sources if "title" in entry]
        return sorted(titles)

    @property
    def sound_mode(self) -> str | None:
        """Return the current sound mode (preset)."""
        if self.coordinator.data is None:
            return None
        preset_id = self.coordinator.data.get("preset")
        return find_title_by_id(preset_id, self._presets)

    @property
    def sound_mode_list(self) -> list[str]:
        """Return the list of available sound modes."""
        titles = [preset["title"] for preset in self._presets if "title" in preset]
        return sorted(titles)

    @property
    def media_title(self) -> str | None:
        """Return the title of current playing media."""
        if self.coordinator.data is None:
            return None
        player_data = self.coordinator.data.get("player_data")
        if player_data:
            track_roles = player_data.get("trackRoles", {})
            return track_roles.get("title")
        return None

    @property
    def media_artist(self) -> str | None:
        """Return the artist of current playing media."""
        if self.coordinator.data is None:
            return None
        player_data = self.coordinator.data.get("player_data")
        if player_data:
            track_roles = player_data.get("trackRoles", {})
            media_data = track_roles.get("mediaData", {})
            meta_data = media_data.get("metaData", {})
            return meta_data.get("artist")
        return None

    @property
    def media_album_name(self) -> str | None:
        """Return the album name of current playing media."""
        if self.coordinator.data is None:
            return None
        player_data = self.coordinator.data.get("player_data")
        if player_data:
            track_roles = player_data.get("trackRoles", {})
            media_data = track_roles.get("mediaData", {})
            meta_data = media_data.get("metaData", {})
            return meta_data.get("album")
        return None

    @property
    def media_image_url(self) -> str | None:
        """Return the image URL of current playing media."""
        if self.coordinator.data is None:
            return None
        player_data = self.coordinator.data.get("player_data")
        if player_data:
            track_roles = player_data.get("trackRoles", {})
            return track_roles.get("icon")
        return None

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level."""
        await self.api.set_volume(int(volume * self._max_volume))
        await self.coordinator.async_request_refresh()

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute volume."""
        await self.api.set_mute(mute)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn on the media player."""
        await self.api.wake()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn off the media player."""
        await self.api.stand_by()
        await self.coordinator.async_request_refresh()

    async def async_select_source(self, source: str) -> None:
        """Select source."""
        source_id = find_id_by_title(source, self._sources)
        if source_id is not None:
            await self.api.set_source(source_id)
            await self.coordinator.async_request_refresh()

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        """Select sound mode (preset)."""
        preset_id = find_id_by_title(sound_mode, self._presets)
        if preset_id is not None:
            await self.api.set_preset(preset_id)
            await self.coordinator.async_request_refresh()

    async def async_media_play(self) -> None:
        """Play media."""
        await self.api.play()
        await self.coordinator.async_request_refresh()

    async def async_media_pause(self) -> None:
        """Pause media."""
        await self.api.pause()
        await self.coordinator.async_request_refresh()

    async def async_media_next_track(self) -> None:
        """Next track."""
        await self.api.next()

    async def async_media_previous_track(self) -> None:
        """Previous track."""
        await self.api.previous()

    async def _cancel_existing_debounce(self) -> None:
        """Cancel the existing debounce task."""
        if self._debounce_task is not None and not self._debounce_task.done():
            _LOGGER.debug("[IMMEDIATE] Cancelling existing debounce task.")
            self._debounce_task.cancel()
            try:
                await self._debounce_task
            except asyncio.CancelledError:
                _LOGGER.debug("[IMMEDIATE] Debounce task fully cancelled.")
            self._debounce_task = None

    def _should_debounce(self, player_state: str) -> bool:
        """Determine if the update should be debounced."""
        power_state = (
            self.coordinator.data.get("power_state") if self.coordinator.data else None
        )
        current_state = self.state
        return (
            player_state == "stopped"
            and power_state != MediaPlayerState.STANDBY
            and current_state != STATE_IDLE
        )

    async def _debounced_update(self, player_data: dict[str, Any]) -> None:
        """Handle the debounced update after cooldown."""
        player_data_copy = copy.deepcopy(player_data)
        try:
            await asyncio.sleep(self._debounce_cooldown)

            if self._debounce_task is None or self._debounce_task.cancelled():
                _LOGGER.debug("Debounce update cancelled after cooldown.")
                return

            _LOGGER.debug("Cooldown passed, applying debounced update.")
            await self._process_player_data(player_data_copy)
        except asyncio.CancelledError:
            _LOGGER.debug("Debounce update cancelled within cooldown window.")
        finally:
            self._debounce_task = None

    async def _process_player_data(self, player_data: dict[str, Any]) -> None:
        """Process player data and update state."""
        # Trigger coordinator refresh to get updated data
        await self.coordinator.async_request_refresh()

    async def async_update(self) -> None:
        """Update the media player state."""
        _LOGGER.debug("Refreshing media player state...")
        # Fetch additional data like sources and presets if needed
        # The coordinator handles most data updates


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AmbeoConfigEntry,
    async_add_entities,
) -> None:
    """Set up media player entity."""
    api = config_entry.runtime_data.api

    sources = await api.get_all_sources()
    presets = await api.get_all_presets()

    async_add_entities(
        [AmbeoMediaPlayer(config_entry, sources, presets)],
        update_before_add=True,
    )
