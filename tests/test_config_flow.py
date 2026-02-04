"""Test the Ambeo Soundbar config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.ambeo_soundbar.const import DOMAIN


@pytest.mark.asyncio
async def test_user_flow_success(hass: HomeAssistant) -> None:
    """Test successful user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "custom_components.ambeo_soundbar.config_flow.validate_input",
        AsyncMock(return_value={
            "title": "Test Ambeo",
            "serial": "test_serial_123",
            "model": "AMBEO Soundbar Max",
        }),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.100"},
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Test Ambeo"
    assert result["data"] == {CONF_HOST: "192.168.1.100"}
    assert result["result"].unique_id == "test_serial_123"


@pytest.mark.asyncio
async def test_user_flow_cannot_connect(hass: HomeAssistant) -> None:
    """Test user flow with connection error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    with patch(
        "custom_components.ambeo_soundbar.config_flow.validate_input",
        AsyncMock(side_effect=Exception("Cannot connect")),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.100"},
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.asyncio
async def test_user_flow_duplicate_unique_id(hass: HomeAssistant) -> None:
    """Test user flow with duplicate unique_id."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    # Create existing entry
    existing_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="test_serial_123",
        data={CONF_HOST: "192.168.1.100"},
    )
    existing_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    with patch(
        "custom_components.ambeo_soundbar.config_flow.validate_input",
        AsyncMock(return_value={
            "title": "Test Ambeo",
            "serial": "test_serial_123",
            "model": "AMBEO Soundbar Max",
        }),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.100"},
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_options_flow(hass: HomeAssistant) -> None:
    """Test options flow."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "192.168.1.100"},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"
