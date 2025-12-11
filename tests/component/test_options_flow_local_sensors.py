"""Test the Meteocat options flow for Local Mode."""
from unittest.mock import patch
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_MODE,
    MODE_LOCAL,
    CONF_MUNICIPALITY_CODE,
    CONF_UPDATE_TIME_1,
    CONF_ENABLE_FORECAST_DAILY,
    CONF_ENABLE_FORECAST_HOURLY,
    CONF_SENSOR_TEMPERATURE,
    CONF_SENSOR_HUMIDITY,
    CONF_SENSOR_RAIN,
)

@pytest.mark.asyncio
async def test_options_flow_local_sensors(hass: HomeAssistant):
    """Test options flow for Local Mode allows reconfiguring sensors."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_UPDATE_TIME_1: "06:00",
            CONF_SENSOR_TEMPERATURE: "sensor.old_temp",
            CONF_SENSOR_HUMIDITY: "sensor.old_hum",
            "mapping_type": "meteocat",  # Add mapping_type to simulate existing entry
        },
        options={}
    )
    entry.add_to_hass(hass)

    # Initialize options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit init step (no changes to options)
    user_input_init = {
        CONF_UPDATE_TIME_1: "06:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_init
    )

    # Should redirect to sensors step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "sensors"

    # Submit sensors step with new values
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.new_temp",
        CONF_SENSOR_HUMIDITY: "sensor.new_hum",
        CONF_SENSOR_RAIN: "sensor.new_rain",
    }

    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input=user_input_sensors
        )

    # Should finish and update entry
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.data[CONF_SENSOR_TEMPERATURE] == "sensor.new_temp"
    assert entry.data[CONF_SENSOR_HUMIDITY] == "sensor.new_hum"
    assert entry.data[CONF_SENSOR_RAIN] == "sensor.new_rain"
