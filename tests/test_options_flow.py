"""Test the Meteocat options flow."""
from unittest.mock import patch
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_MODE,
    MODE_ESTACIO,
    CONF_STATION_CODE,
    CONF_MUNICIPALITY_CODE,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    CONF_ENABLE_FORECAST_DAILY,
    CONF_ENABLE_FORECAST_HOURLY,
)

@pytest.mark.asyncio
async def test_options_flow_init(hass: HomeAssistant):
    """Test options flow initialization."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_ESTACIO,
            CONF_STATION_CODE: "YM",
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_UPDATE_TIME_1: "06:00",
        },
        options={}
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

@pytest.mark.asyncio
async def test_options_flow_save(hass: HomeAssistant):
    """Test saving options."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_ESTACIO,
            CONF_STATION_CODE: "YM",
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_UPDATE_TIME_1: "06:00",
        },
        options={}
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    
    user_input = {
        CONF_UPDATE_TIME_1: "07:00",
        CONF_UPDATE_TIME_2: "15:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input=user_input
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.data[CONF_UPDATE_TIME_1] == "07:00"
    assert entry.data[CONF_UPDATE_TIME_2] == "15:00"
