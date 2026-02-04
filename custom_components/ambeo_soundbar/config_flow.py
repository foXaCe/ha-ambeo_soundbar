import logging

import aiohttp
from homeassistant import config_entries
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
import voluptuous as vol

from .api.factory import AmbeoAPIFactory
from .const import (
    CONFIG_DEBOUNCE_COOLDOWN,
    CONFIG_DEBOUNCE_COOLDOWN_DEFAULT,
    CONFIG_HOST,
    CONFIG_HOST_DEFAULT,
    DEFAULT_PORT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def validate_connection(hass, host, port=DEFAULT_PORT):
    """Validate connection to Ambeo device and return name if successful."""
    async with aiohttp.ClientSession() as client_session:
        try:
            ambeo_api = await AmbeoAPIFactory.create_api(
                host, port, client_session, hass
            )
            name = await ambeo_api.get_name()
            serial = await ambeo_api.get_serial()
        except Exception as error:
            _LOGGER.exception("Connection error to %s: %s", host, error)
            return None, None, "cannot_connect"
        else:
            return name, serial, None


class AmbeoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options configuration for Ambeo Soundbar integration."""

    async def async_step_init(self, user_input=None):
        errors = {}
        host_default = self.config_entry.options.get(
            CONFIG_HOST, self.config_entry.data.get(CONFIG_HOST)
        )
        if user_input is not None:
            _name, _serial, error = await validate_connection(
                self.hass, user_input[CONFIG_HOST]
            )
            if error is not None:
                errors["base"] = error
                return self.display_form(errors, host_default)
            return self.async_create_entry(data=user_input)

        return self.display_form(errors, host_default)

    def display_form(self, errors, host_default):
        try:
            support_debounce = self.hass.data[DOMAIN][self.config_entry.entry_id][
                "api"
            ].support_debounce_mode()
        except Exception:
            support_debounce = False

        if self.config_entry.options.get(CONFIG_DEBOUNCE_COOLDOWN, 0) > 0:
            errors["base"] = "experimental_feature_activated"
        options_schema = (
            vol.Schema(
                {
                    vol.Optional(CONFIG_HOST, default=host_default): str,
                    vol.Optional(
                        CONFIG_DEBOUNCE_COOLDOWN,
                        default=self.config_entry.options.get(
                            CONFIG_DEBOUNCE_COOLDOWN, CONFIG_DEBOUNCE_COOLDOWN_DEFAULT
                        ),
                    ): int,
                }
            )
            if support_debounce
            else vol.Schema({vol.Optional(CONFIG_HOST, default=host_default): str})
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )


class AmbeoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Manage the configuration flow for Ambeo Soundbar integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a configuration initiated by the user."""
        errors = {}

        if user_input is not None:
            host = user_input.get(CONFIG_HOST)
            name, serial, error = await validate_connection(self.hass, host)
            if error:
                errors["base"] = error
            else:
                await self.async_set_unique_id(serial)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=name, data=user_input)

        data_schema = vol.Schema(
            {vol.Required(CONFIG_HOST, default=CONFIG_HOST_DEFAULT): str}
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo):
        """Handle zeroconf discovery of AMBEO soundbar."""
        _LOGGER.debug("Zeroconf discovery info: %s", discovery_info)

        # Extract host from discovery info
        host = discovery_info.host

        # Validate connection to discovered device
        name, serial, error = await validate_connection(self.hass, host)

        if error or not serial:
            _LOGGER.warning(
                "Failed to validate discovered device at %s: %s", host, error
            )
            return self.async_abort(reason="cannot_connect")

        # Set unique ID to prevent duplicate entries
        await self.async_set_unique_id(serial)
        self._abort_if_unique_id_configured(updates={CONFIG_HOST: host})

        # Store discovery info for confirmation step
        self.context["title_placeholders"] = {"name": name or "AMBEO Soundbar"}
        self._discovered_host = host
        self._discovered_name = name

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(self, user_input=None):
        """Confirm discovery of AMBEO soundbar."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._discovered_name,
                data={CONFIG_HOST: self._discovered_host},
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"name": self._discovered_name},
        )

    @staticmethod
    def async_get_options_flow(_config_entry):
        """Get the options flow for this handler."""
        return AmbeoOptionsFlowHandler()
