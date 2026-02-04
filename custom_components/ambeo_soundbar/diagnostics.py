"""Diagnostics support for Ambeo Soundbar."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import AmbeoConfigEntry

TO_REDACT = {
    "serial",
    "host",
    "ip",
    "mac",
    "password",
    "token",
    "api_key",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: AmbeoConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    runtime_data = entry.runtime_data
    coordinator = runtime_data.coordinator
    device = runtime_data.device
    api = runtime_data.api

    diagnostics = {
        "entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "domain": entry.domain,
            "title": entry.title,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": async_redact_data(dict(entry.options), TO_REDACT),
            "unique_id": entry.unique_id,
        },
        "device": {
            "serial": async_redact_data({"serial": device.serial}, TO_REDACT).get(
                "serial"
            ),
            "name": device.name,
            "manufacturer": device.manufacturer,
            "model": device.model,
            "version": device.version,
            "host": async_redact_data({"host": device.host}, TO_REDACT).get("host"),
            "port": device.port,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_exception": str(coordinator.last_exception)
            if coordinator.last_exception
            else None,
        },
        "data": async_redact_data(coordinator.data or {}, TO_REDACT),
        "capabilities": api.capabilities if hasattr(api, "capabilities") else [],
    }

    return diagnostics
