"""Config flow for Ambeo Soundbar integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONFIG_DEBOUNCE_COOLDOWN,
    CONFIG_DEBOUNCE_COOLDOWN_DEFAULT,
    CONFIG_ENTRY_VERSION,
    CONFIG_HOST_DEFAULT,
    DEFAULT_PORT,
    DOMAIN,
)
from .api.factory import AmbeoAPIFactory

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=CONFIG_HOST_DEFAULT): str,
    }
)


async def validate_input(hass, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    host = data[CONF_HOST]
    session = async_get_clientsession(hass)

    try:
        api = await AmbeoAPIFactory.create_api(host, DEFAULT_PORT, session, hass)
        serial = await api.get_serial()
        name = await api.get_name()
        model = await api.get_model()
    except aiohttp.ClientError as err:
        raise CannotConnect from err
    except Exception as err:
        _LOGGER.exception("Unexpected exception")
        raise UnknownError from err

    return {"title": name, "serial": serial, "model": model}


class AmbeoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ambeo Soundbar."""

    VERSION = CONFIG_ENTRY_VERSION

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                await self.async_set_unique_id(info["serial"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except UnknownError:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reconfiguration of the device."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                # Verify it's the same device
                if info["serial"] != reconfigure_entry.unique_id:
                    errors["base"] = "wrong_device"
                else:
                    return self.async_update_reload_and_abort(
                        reconfigure_entry,
                        data_updates=user_input,
                    )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except UnknownError:
                errors["base"] = "unknown"

        # Pre-fill with current host
        current_host = reconfigure_entry.data.get(CONF_HOST, CONFIG_HOST_DEFAULT)
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current_host): str,
            }
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> AmbeoOptionsFlowHandler:
        """Get the options flow for this handler."""
        return AmbeoOptionsFlowHandler(config_entry)


class AmbeoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Ambeo Soundbar."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate new host if changed
            new_host = user_input.get(CONF_HOST)
            if new_host and new_host != self.config_entry.data.get(CONF_HOST):
                try:
                    info = await validate_input(self.hass, {CONF_HOST: new_host})
                    if info["serial"] != self.config_entry.unique_id:
                        errors["base"] = "wrong_device"
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except UnknownError:
                    errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(data=user_input)

        # Build schema based on device capabilities
        supports_debounce = False
        if self.hass.data.get(DOMAIN):
            runtime_data = self.hass.data[DOMAIN].get(self.config_entry.entry_id)
            if runtime_data:
                supports_debounce = runtime_data.get("api", {}).support_debounce_mode()

        host_default = self.config_entry.options.get(
            CONF_HOST, self.config_entry.data.get(CONF_HOST, CONFIG_HOST_DEFAULT)
        )
        debounce_default = self.config_entry.options.get(
            CONFIG_DEBOUNCE_COOLDOWN, CONFIG_DEBOUNCE_COOLDOWN_DEFAULT
        )

        if supports_debounce:
            schema = vol.Schema(
                {
                    vol.Optional(CONF_HOST, default=host_default): str,
                    vol.Optional(
                        CONFIG_DEBOUNCE_COOLDOWN, default=debounce_default
                    ): int,
                }
            )
        else:
            schema = vol.Schema(
                {
                    vol.Optional(CONF_HOST, default=host_default): str,
                }
            )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class UnknownError(Exception):
    """Error to indicate an unknown error occurred."""
