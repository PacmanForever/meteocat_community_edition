"""Test the Meteocat options flow cancellation behavior."""
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
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    CONF_ENABLE_FORECAST_DAILY,
    CONF_ENABLE_FORECAST_HOURLY,
    CONF_SENSOR_TEMPERATURE,
    CONF_SENSOR_HUMIDITY,
    CONF_SENSOR_PRESSURE,
)

@pytest.mark.asyncio
async def test_options_flow_local_cancellation_no_save(hass: HomeAssistant):
    """Test that changes are not saved if the flow is not completed (Local Mode)."""
    # 1. Setup existing entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_LOCAL,
            CONF_UPDATE_TIME_1: "06:00",
            CONF_SENSOR_TEMPERATURE: "sensor.old_temp",
            CONF_SENSOR_HUMIDITY: "sensor.old_hum",
            "mapping_type": "meteocat",
        },
        options={
            CONF_UPDATE_TIME_1: "06:00",
            CONF_API_KEY: "test_key",
        }
    )
    entry.add_to_hass(hass)

    # 2. Start Options Flow
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # 3. Modify Step 1 (Init) - Change Update Time
    user_input_init = {
        CONF_UPDATE_TIME_1: "08:00",  # NEW VALUE
        CONF_UPDATE_TIME_2: "20:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_init
    )
    
    # Assert next step is local_sensors
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "local_sensors"

    # CRITICAL: Check that the config entry has NOT been updated yet
    # The option in memory should still be 06:00
    assert entry.options.get(CONF_UPDATE_TIME_1) == "06:00"
    
    # 4. Modify Step 2 (Local Sensors) - Change Sensors
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.new_temp", # NEW VALUE
        CONF_SENSOR_HUMIDITY: "sensor.new_hum",
        CONF_SENSOR_PRESSURE: "sensor.new_pressure",
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_sensors
    )
    
    # Assert next step is condition_mapping_type
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    # CRITICAL: Check that the config entry has NOT been updated yet
    # Still old values
    assert entry.options.get(CONF_UPDATE_TIME_1) == "06:00"
    assert entry.data.get(CONF_SENSOR_TEMPERATURE) == "sensor.old_temp"

    # 5. Stop here. Simulate user clicking "X" (we just don't continue the flow).
    # Since we haven't reached create_entry, nothing should be saved.
    
    # Re-verify nothing changed in the entry
    assert entry.options.get(CONF_UPDATE_TIME_1) == "06:00"
    assert entry.data.get(CONF_SENSOR_TEMPERATURE) == "sensor.old_temp"


@pytest.mark.asyncio
async def test_options_flow_local_success_save(hass: HomeAssistant):
    """Test that changes ARE saved when the flow IS completed (Local Mode)."""
    # 1. Setup existing entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_LOCAL,
            CONF_UPDATE_TIME_1: "06:00",
            CONF_SENSOR_TEMPERATURE: "sensor.old_temp",
            CONF_SENSOR_HUMIDITY: "sensor.old_hum",
            "mapping_type": "meteocat",
        },
        options={
            CONF_UPDATE_TIME_1: "06:00",
            CONF_API_KEY: "test_key",
        }
    )
    entry.add_to_hass(hass)

    # 2. Start Options Flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    # 3. Modify Step 1 (Init)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], 
        user_input={
            CONF_UPDATE_TIME_1: "08:00",
            CONF_UPDATE_TIME_2: "",
            CONF_ENABLE_FORECAST_DAILY: True,
            CONF_ENABLE_FORECAST_HOURLY: False,
        }
    )

    # 4. Modify Step 2 (Sensors)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], 
        user_input={
            CONF_SENSOR_TEMPERATURE: "sensor.new_temp",
            CONF_SENSOR_HUMIDITY: "sensor.old_hum",
        }
    )

    # 5. Modify Step 3 (Mapping Type) -> Select 'meteocat' to finish
    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], 
            user_input={
                "mapping_type": "meteocat"
            }
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    
    # CRITICAL: Verify NOW changes are saved
    assert entry.options.get(CONF_UPDATE_TIME_1) == "08:00"
    assert entry.data.get(CONF_SENSOR_TEMPERATURE) == "sensor.new_temp"


@pytest.mark.asyncio
async def test_options_flow_custom_mapping_save(hass: HomeAssistant):
    """Test that changes ARE saved when using Custom Mapping flow."""
    # 1. Setup existing entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_LOCAL,
            CONF_SENSOR_TEMPERATURE: "sensor.temp",
            CONF_SENSOR_HUMIDITY: "sensor.hum",
        },
        options={}
    )
    entry.add_to_hass(hass)

    # 2. Start Options Flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    # Step 1: Init
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], 
        user_input={
            CONF_UPDATE_TIME_1: "09:00",
            CONF_ENABLE_FORECAST_DAILY: True,
            CONF_ENABLE_FORECAST_HOURLY: False,
        }
    )

    # Step 2: Sensors
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], 
        user_input={
            CONF_SENSOR_TEMPERATURE: "sensor.temp",
            CONF_SENSOR_HUMIDITY: "sensor.hum",
        }
    )

    # Step 3: Mapping Type -> Custom
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], 
        user_input={
            "mapping_type": "custom"
        }
    )
    
    assert result["step_id"] == "condition_mapping_custom"
    
    # Check NOT SAVED YET
    assert entry.options.get(CONF_UPDATE_TIME_1) != "09:00"

    # Step 4: Custom Mapping
    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], 
            user_input={
                "local_condition_entity": "sensor.weather_code",
                "sunny": "1, 2",
                "cloudy": "3"
            }
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    
    # Check SAVED NOW
    assert entry.options.get(CONF_UPDATE_TIME_1) == "09:00"
    assert entry.data.get("mapping_type") == "custom"
    assert entry.data.get("custom_condition_mapping")["1"] == "sunny"
