"""Logbook integration for Ambeo Soundbar."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.components.logbook import (
    LOGBOOK_ENTRY_ICON,
    LOGBOOK_ENTRY_MESSAGE,
    LOGBOOK_ENTRY_NAME,
)
from homeassistant.core import Event, HomeAssistant, callback

from .const import DOMAIN

EVENT_AMBEO_SOURCE_CHANGED = f"{DOMAIN}_source_changed"
EVENT_AMBEO_PRESET_CHANGED = f"{DOMAIN}_preset_changed"
EVENT_AMBEO_POWER_STATE_CHANGED = f"{DOMAIN}_power_state_changed"


@callback
def async_describe_events(
    hass: HomeAssistant,
    async_describe_event: Callable[[str, str, Callable[[Event], dict[str, str]]], None],
) -> None:
    """Describe logbook events."""

    @callback
    def async_describe_source_changed(event: Event) -> dict[str, str]:
        """Describe source changed event."""
        return {
            LOGBOOK_ENTRY_NAME: event.data.get("device_name", "Ambeo Soundbar"),
            LOGBOOK_ENTRY_MESSAGE: f"Source changed to {event.data.get('source', 'Unknown')}",
            LOGBOOK_ENTRY_ICON: "mdi:speaker",
        }

    @callback
    def async_describe_preset_changed(event: Event) -> dict[str, str]:
        """Describe preset changed event."""
        return {
            LOGBOOK_ENTRY_NAME: event.data.get("device_name", "Ambeo Soundbar"),
            LOGBOOK_ENTRY_MESSAGE: f"Sound mode changed to {event.data.get('preset', 'Unknown')}",
            LOGBOOK_ENTRY_ICON: "mdi:equalizer",
        }

    @callback
    def async_describe_power_state_changed(event: Event) -> dict[str, str]:
        """Describe power state changed event."""
        state = event.data.get("state", "Unknown")
        icon = "mdi:power-on" if state == "online" else "mdi:power-off"
        return {
            LOGBOOK_ENTRY_NAME: event.data.get("device_name", "Ambeo Soundbar"),
            LOGBOOK_ENTRY_MESSAGE: f"Power state changed to {state}",
            LOGBOOK_ENTRY_ICON: icon,
        }

    async_describe_event(
        DOMAIN, EVENT_AMBEO_SOURCE_CHANGED, async_describe_source_changed
    )
    async_describe_event(
        DOMAIN, EVENT_AMBEO_PRESET_CHANGED, async_describe_preset_changed
    )
    async_describe_event(
        DOMAIN, EVENT_AMBEO_POWER_STATE_CHANGED, async_describe_power_state_changed
    )
