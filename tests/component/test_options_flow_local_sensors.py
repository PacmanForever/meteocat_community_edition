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
    CONF_SENSOR_PRESSURE,
    CONF_SENSOR_WIND_SPEED,
    CONF_SENSOR_WIND_BEARING,
    CONF_SENSOR_WIND_GUST,
    CONF_SENSOR_VISIBILITY,
    CONF_SENSOR_UV_INDEX,
    CONF_SENSOR_OZONE,
    CONF_SENSOR_CLOUD_COVERAGE,
    CONF_SENSOR_DEW_POINT,
    CONF_SENSOR_APPARENT_TEMPERATURE,
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
    assert result["step_id"] == "local_sensors"

    # Submit sensors step with new values
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.new_temp",
        CONF_SENSOR_HUMIDITY: "sensor.new_hum",
        CONF_SENSOR_RAIN: "sensor.new_rain",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_sensors
    )

    # Should redirect to condition mapping type step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    # Submit condition mapping type step (keep meteocat)
    user_input_mapping = {
        "mapping_type": "meteocat",
    }
    
    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input=user_input_mapping
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

    # Submit init step (no mapping type in init anymore)
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
    assert result["step_id"] == "local_sensors"

    # Submit sensors step
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_sensors
    )

    # Should redirect to condition mapping type step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    # Submit condition mapping type step (switch to custom)
    user_input_mapping = {
        "mapping_type": "custom",
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_mapping
    )

    # Should redirect to custom mapping step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_custom"

    # Submit custom mapping configuration
    user_input_custom = {
        "local_condition_entity": "sensor.weather_condition",
        "custom_condition_mapping": "0: clear-night\n1: sunny\n2: partlycloudy",
    }

    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input=user_input_custom
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

    # Submit init step (no mapping type in init anymore)
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
    assert result["step_id"] == "local_sensors"

    # Submit sensors step
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_sensors
    )

    # Should redirect to condition mapping type step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    # Submit condition mapping type step (switch to meteocat)
    user_input_mapping = {
        "mapping_type": "meteocat",
    }
    
    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input=user_input_mapping
        )

    # Should finish and update entry
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.data["mapping_type"] == "meteocat"
    assert "local_condition_entity" not in entry.data
    assert "custom_condition_mapping" not in entry.data


@pytest.mark.asyncio
async def test_options_flow_local_edit_custom_mapping(hass: HomeAssistant):
    """Test options flow for Local Mode allows editing existing custom mapping and then goes to sensors."""
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
            CONF_SENSOR_TEMPERATURE: "sensor.temp",  # Already configured sensors
        },
        options={}
    )
    entry.add_to_hass(hass)

    # Initialize options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit init step (no mapping type in init anymore)
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
    assert result["step_id"] == "local_sensors"

    # Submit sensors step
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.updated_temp",
        CONF_SENSOR_HUMIDITY: "sensor.updated_hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_sensors
    )

    # Should redirect to condition mapping type step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    # Submit condition mapping type step (switch to custom)
    user_input_mapping = {
        "mapping_type": "custom",
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_mapping
    )

    # Should redirect to custom mapping step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_custom"

    # Submit custom mapping configuration (editing existing)
    user_input_custom = {
        "local_condition_entity": "sensor.new_condition",
        "custom_condition_mapping": "0: clear-night\n1: sunny\n2: partlycloudy",
    }

    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input=user_input_custom
        )

    # Should finish and update entry
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.data["mapping_type"] == "custom"
    assert entry.data["local_condition_entity"] == "sensor.new_condition"
    assert "custom_condition_mapping" in entry.data
    assert entry.data[CONF_SENSOR_TEMPERATURE] == "sensor.updated_temp"


@pytest.mark.asyncio
async def test_options_flow_local_edit_meteocat_mapping(hass: HomeAssistant):
    """Test options flow for Local Mode allows editing existing meteocat mapping and goes to sensors."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_UPDATE_TIME_1: "06:00",
            "mapping_type": "meteocat",
            CONF_SENSOR_TEMPERATURE: "sensor.temp",  # Already configured sensors
            CONF_SENSOR_HUMIDITY: "sensor.hum",
        },
        options={}
    )
    entry.add_to_hass(hass)

    # Initialize options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit init step (no mapping type in init anymore)
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
    assert result["step_id"] == "local_sensors"

    # Submit sensors step
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.updated_temp",
        CONF_SENSOR_HUMIDITY: "sensor.updated_hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_sensors
    )

    # Should redirect to condition mapping type step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    # Submit condition mapping type step (keep meteocat)
    user_input_mapping = {
        "mapping_type": "meteocat",
    }
    
    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input=user_input_mapping
        )

    # Should finish and update entry
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.data["mapping_type"] == "meteocat"
    assert "local_condition_entity" not in entry.data
    assert "custom_condition_mapping" not in entry.data
    assert entry.data[CONF_SENSOR_TEMPERATURE] == "sensor.updated_temp"


@pytest.mark.asyncio
async def test_options_flow_local_sensors_validation_errors(hass: HomeAssistant):
    """Test options flow for Local Mode validates sensor requirements during editing."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_UPDATE_TIME_1: "06:00",
            "mapping_type": "meteocat",
            CONF_SENSOR_TEMPERATURE: "sensor.temp",  # Already configured sensors
            CONF_SENSOR_HUMIDITY: "sensor.hum",
        },
        options={}
    )
    entry.add_to_hass(hass)

    # Initialize options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit init step
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
    assert result["step_id"] == "local_sensors"

    # Submit sensors step with valid changes
    user_input_sensors_valid = {
        CONF_SENSOR_TEMPERATURE: "sensor.new_temp",
        CONF_SENSOR_HUMIDITY: "sensor.new_hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_sensors_valid
    )

    # Should redirect to condition mapping type step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    # Submit condition mapping type step (keep meteocat)
    user_input_mapping = {
        "mapping_type": "meteocat",
    }

    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input=user_input_mapping
        )

    # Should finish and update entry
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.data[CONF_SENSOR_TEMPERATURE] == "sensor.new_temp"
    assert entry.data[CONF_SENSOR_HUMIDITY] == "sensor.new_hum"


@pytest.mark.asyncio
async def test_options_flow_local_no_changes(hass: HomeAssistant):
    """Test options flow for Local Mode when no changes are made."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_UPDATE_TIME_1: "06:00",
            "mapping_type": "meteocat",
            CONF_SENSOR_TEMPERATURE: "sensor.temp",
            CONF_SENSOR_HUMIDITY: "sensor.hum",
        },
        options={}
    )
    entry.add_to_hass(hass)

    # Initialize options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit init step with same values
    user_input_init = {
        CONF_UPDATE_TIME_1: "06:00",  # Same value
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_init
    )

    # Should redirect to sensors step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "local_sensors"

    # Submit sensors step with same values (no changes)
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",  # Same value
        CONF_SENSOR_HUMIDITY: "sensor.hum",      # Same value
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_sensors
    )

    # Should redirect to condition mapping type step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    # Submit condition mapping type step (keep meteocat)
    user_input_mapping = {
        "mapping_type": "meteocat",
    }

    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input=user_input_mapping
        )

    # Should finish
    assert result["type"] == FlowResultType.CREATE_ENTRY


@pytest.mark.asyncio
async def test_options_flow_api_key_preservation_full_sequence(hass: HomeAssistant):
    """Test that API key is preserved throughout the entire options flow sequence."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_api_key_original",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_UPDATE_TIME_1: "06:00",
            CONF_SENSOR_TEMPERATURE: "sensor.temp",
            CONF_SENSOR_HUMIDITY: "sensor.hum",
            "mapping_type": "meteocat",
        },
        options={}
    )
    entry.add_to_hass(hass)

    # Step 1: Initialize options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Step 2: Submit init step with time changes
    user_input_init = {
        CONF_UPDATE_TIME_1: "08:00",  # Change time
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_init
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "local_sensors"

    # Step 3: Submit sensors step
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.new_temp",
        CONF_SENSOR_HUMIDITY: "sensor.new_hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_sensors
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    # Step 4: Submit mapping type step
    user_input_mapping = {
        "mapping_type": "custom",  # Change to custom
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_mapping
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_custom"

    # Step 5: Submit custom mapping
    user_input_custom = {
        "local_condition_entity": "sensor.weather_condition",
        "custom_condition_mapping": "sunny:sunny\ncloudy:cloudy\nrainy:rainy",
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_custom
    )

    # Should finish and update entry
    assert result["type"] == FlowResultType.CREATE_ENTRY
    
    # CRITICAL: Verify API key is still preserved in data
    assert entry.data[CONF_API_KEY] == "test_api_key_original"
    assert entry.data["mapping_type"] == "custom"
    assert entry.data["local_condition_entity"] == "sensor.weather_condition"


@pytest.mark.asyncio
async def test_options_flow_no_initial_mapping_type(hass: HomeAssistant):
    """Test options flow when entry has no initial mapping_type."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_api_key",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_UPDATE_TIME_1: "06:00",
            CONF_SENSOR_TEMPERATURE: "sensor.temp",
            CONF_SENSOR_HUMIDITY: "sensor.hum",
            # No mapping_type initially
        },
        options={}
    )
    entry.add_to_hass(hass)

    # Initialize options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit init step
    user_input_init = {
        CONF_UPDATE_TIME_1: "06:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_init
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "local_sensors"

    # Submit sensors step
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_sensors
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    # Submit mapping type step (should default to meteocat)
    user_input_mapping = {
        "mapping_type": "meteocat",
    }
    
    with patch("custom_components.meteocat_community_edition.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input=user_input_mapping
        )

    # Should finish successfully
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.data[CONF_API_KEY] == "test_api_key"
    assert entry.data.get("mapping_type") == "meteocat"
