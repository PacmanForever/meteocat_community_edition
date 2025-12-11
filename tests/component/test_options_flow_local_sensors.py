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


@pytest.mark.asyncio
async def test_options_flow_local_switch_to_custom_mapping(hass: HomeAssistant):
    """Test options flow for Local Mode allows switching from meteocat to custom mapping."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_UPDATE_TIME_1: "06:00",
            "mapping_type": "meteocat",
        },
        options={}
    )
    entry.add_to_hass(hass)

    # Initialize options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit init step with switch to custom mapping
    user_input_init = {
        CONF_UPDATE_TIME_1: "06:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
        "mapping_type": "custom",
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_init
    )

    # Should redirect to custom mapping step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_custom"

    # Submit custom mapping configuration
    user_input_custom = {
        "local_condition_entity": "sensor.weather_condition",
        "custom_condition_mapping": "0: clear-night\n1: sunny\n2: partlycloudy",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_custom
    )

    # Should redirect to sensors step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "sensors"

    # Submit sensors step
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
    }

    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input=user_input_sensors
        )

    # Should finish and update entry
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.data["mapping_type"] == "custom"
    assert entry.data["local_condition_entity"] == "sensor.weather_condition"
    assert "custom_condition_mapping" in entry.data


@pytest.mark.asyncio
async def test_options_flow_local_switch_to_meteocat_mapping(hass: HomeAssistant):
    """Test options flow for Local Mode allows switching from custom to meteocat mapping."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_UPDATE_TIME_1: "06:00",
            "mapping_type": "custom",
            "local_condition_entity": "sensor.old_condition",
            "custom_condition_mapping": {"0": "sunny", "1": "cloudy"},
        },
        options={}
    )
    entry.add_to_hass(hass)

    # Initialize options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit init step with switch to meteocat mapping
    user_input_init = {
        CONF_UPDATE_TIME_1: "06:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
        "mapping_type": "meteocat",
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_init
    )

    # Should redirect to sensors step (since meteocat mapping is updated automatically)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "sensors"

    # Submit sensors step
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
    }

    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input=user_input_sensors
        )

    # Should finish and update entry
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.data["mapping_type"] == "meteocat"
    assert "local_condition_entity" not in entry.data
    assert "custom_condition_mapping" not in entry.data
