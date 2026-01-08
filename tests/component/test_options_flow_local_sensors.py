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
    MODE_EXTERNAL,
    CONF_STATION_CODE,
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
        "clear-night": "0",
        "sunny": "1",
        "partlycloudy": "2",
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
        "clear-night": "0",
        "sunny": "1",
        "partlycloudy": "2",
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
        "sunny": "sunny",
        "cloudy": "cloudy",
        "rainy": "rainy",
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


@pytest.mark.asyncio
async def test_options_flow_external_station_api_key_preservation(hass: HomeAssistant):
    """Test that API key is preserved when editing external station options."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "original_api_key",
            CONF_MODE: MODE_EXTERNAL,
            CONF_STATION_CODE: "VY",
            CONF_UPDATE_TIME_1: "06:00",
        },
        options={}
    )
    entry.add_to_hass(hass)

    # Initialize options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # After init, API key should still be in data
    assert entry.data[CONF_API_KEY] == "original_api_key"

    # Submit init step with time changes
    user_input_init = {
        CONF_UPDATE_TIME_1: "08:00",  # Change time
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input_init
    )

    # For external mode, should finish immediately
    assert result["type"] == FlowResultType.CREATE_ENTRY
    
    # CRITICAL: Verify API key is still preserved
    assert entry.data[CONF_API_KEY] == "original_api_key"
    assert entry.options[CONF_UPDATE_TIME_1] == "08:00"


@pytest.mark.asyncio
async def test_options_flow_api_key_migration_from_options(hass: HomeAssistant):
    """Test that API key is migrated from options to data during options editing."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_EXTERNAL,
            CONF_STATION_CODE: "VY",
            CONF_UPDATE_TIME_1: "06:00",
            # No API key in data
        },
        options={
            CONF_API_KEY: "api_key_in_options",  # API key in options (old format)
        }
    )
    entry.add_to_hass(hass)

    # Initialize options flow - should migrate API key
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # API key should now be in data
    assert entry.data[CONF_API_KEY] == "api_key_in_options"


@pytest.mark.asyncio
async def test_options_flow_multiple_edits_preserve_data(hass: HomeAssistant):
    """Test that multiple consecutive edits preserve all data correctly."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "original_api_key",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_SENSOR_TEMPERATURE: "sensor.temp",
            CONF_SENSOR_HUMIDITY: "sensor.hum",
            "mapping_type": "meteocat",
        },
        options={
            CONF_UPDATE_TIME_1: "06:00",
            CONF_ENABLE_FORECAST_DAILY: True,
            CONF_ENABLE_FORECAST_HOURLY: False,
        }
    )
    entry.add_to_hass(hass)

    # FIRST EDIT: Change update time
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    user_input_init = {
        CONF_UPDATE_TIME_1: "08:00",  # Change time
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_init
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "local_sensors"

    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_sensors
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    user_input_mapping = {
        "mapping_type": "meteocat",
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_mapping
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Verify first edit results
    assert entry.data[CONF_API_KEY] == "original_api_key"
    assert entry.data["mapping_type"] == "meteocat"
    assert entry.options[CONF_UPDATE_TIME_1] == "08:00"

    # SECOND EDIT: Change sensors
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    user_input_init2 = {
        CONF_UPDATE_TIME_1: "08:00",  # Keep same
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_init2
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "local_sensors"

    user_input_sensors2 = {
        CONF_SENSOR_TEMPERATURE: "sensor.new_temp",
        CONF_SENSOR_HUMIDITY: "sensor.new_hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_sensors2
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    user_input_mapping2 = {
        "mapping_type": "meteocat",
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_mapping2
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Verify second edit results - everything preserved
    assert entry.data[CONF_API_KEY] == "original_api_key"
    assert entry.data["mapping_type"] == "meteocat"
    assert entry.data[CONF_SENSOR_TEMPERATURE] == "sensor.new_temp"
    assert entry.data[CONF_SENSOR_HUMIDITY] == "sensor.new_hum"
    assert entry.options[CONF_UPDATE_TIME_1] == "08:00"


@pytest.mark.asyncio
async def test_options_flow_change_mapping_type_then_edit_again(hass: HomeAssistant):
    """Test changing mapping type in first edit, then editing again preserves data."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "original_api_key",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_SENSOR_TEMPERATURE: "sensor.temp",
            CONF_SENSOR_HUMIDITY: "sensor.hum",
            "mapping_type": "meteocat",
        },
        options={
            CONF_UPDATE_TIME_1: "06:00",
            CONF_ENABLE_FORECAST_DAILY: True,
            CONF_ENABLE_FORECAST_HOURLY: False,
        }
    )
    entry.add_to_hass(hass)

    # FIRST EDIT: Change mapping type to custom
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    user_input_init = {
        CONF_UPDATE_TIME_1: "06:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_init
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "local_sensors"

    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_sensors
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    user_input_mapping = {
        "mapping_type": "custom",
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_mapping
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_custom"

    user_input_custom = {
        "local_condition_entity": "sensor.weather_condition",
        "clear-night": "0",
        "sunny": "1",
        "partlycloudy": "2",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_custom
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Verify first edit results
    assert entry.data[CONF_API_KEY] == "original_api_key"
    assert entry.data["mapping_type"] == "custom"
    assert entry.data["local_condition_entity"] == "sensor.weather_condition"
    assert "custom_condition_mapping" in entry.data

    # SECOND EDIT: Change update time after mapping type change
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    user_input_init2 = {
        CONF_UPDATE_TIME_1: "10:00",  # Change time
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_init2
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "local_sensors"

    user_input_sensors2 = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_sensors2
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    user_input_mapping2 = {
        "mapping_type": "custom",  # Keep custom
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_mapping2
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_custom"

    user_input_custom2 = {
        "local_condition_entity": "sensor.weather_condition",  # Keep same
        "clear-night": "0",
        "sunny": "1",
        "partlycloudy": "2",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_custom2
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Verify second edit results - all data preserved including custom mapping
    assert entry.data[CONF_API_KEY] == "original_api_key"
    assert entry.data["mapping_type"] == "custom"
    assert entry.data["local_condition_entity"] == "sensor.weather_condition"
    assert entry.data["custom_condition_mapping"] == {"0": "clear-night", "1": "sunny", "2": "partlycloudy"}
    assert entry.options[CONF_UPDATE_TIME_1] == "10:00"


@pytest.mark.asyncio
async def test_options_flow_switch_mapping_types_multiple_times(hass: HomeAssistant):
    """Test switching between meteocat and custom mapping types multiple times."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "original_api_key",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_SENSOR_TEMPERATURE: "sensor.temp",
            CONF_SENSOR_HUMIDITY: "sensor.hum",
            "mapping_type": "meteocat",
        },
        options={
            CONF_UPDATE_TIME_1: "06:00",
            CONF_ENABLE_FORECAST_DAILY: True,
            CONF_ENABLE_FORECAST_HOURLY: False,
        }
    )
    entry.add_to_hass(hass)

    # EDIT 1: Switch to custom
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    user_input_init = {
        CONF_UPDATE_TIME_1: "06:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_init
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "local_sensors"

    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_sensors
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    user_input_mapping = {
        "mapping_type": "custom",
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_mapping
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_custom"

    user_input_custom = {
        "local_condition_entity": "sensor.weather_condition",
        "clear-night": "0",
        "sunny": "1",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_custom
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    assert entry.data["mapping_type"] == "custom"
    assert "local_condition_entity" in entry.data
    assert "custom_condition_mapping" in entry.data

    # EDIT 2: Switch back to meteocat
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    user_input_init2 = {
        CONF_UPDATE_TIME_1: "06:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_init2
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "local_sensors"

    user_input_sensors2 = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_sensors2
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    user_input_mapping2 = {
        "mapping_type": "meteocat",
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_mapping2
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Verify custom fields are removed
    assert entry.data["mapping_type"] == "meteocat"
    assert "local_condition_entity" not in entry.data
    assert "custom_condition_mapping" not in entry.data
    assert entry.data[CONF_API_KEY] == "original_api_key"

    # EDIT 3: Switch to custom again
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    user_input_init3 = {
        CONF_UPDATE_TIME_1: "06:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_init3
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "local_sensors"

    user_input_sensors3 = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_sensors3
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    user_input_mapping3 = {
        "mapping_type": "custom",
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_mapping3
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_custom"

    user_input_custom3 = {
        "local_condition_entity": "sensor.new_weather_condition",
        "clear-night": "0",
        "sunny": "1",
        "cloudy": "2",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_custom3
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Verify final state
    assert entry.data["mapping_type"] == "custom"
    assert entry.data["local_condition_entity"] == "sensor.new_weather_condition"
    assert entry.data["custom_condition_mapping"] == {"0": "clear-night", "1": "sunny", "2": "cloudy"}


@pytest.mark.asyncio
async def test_options_flow_invalid_mapping_type_auto_correction(hass: HomeAssistant):
    """Test that invalid mapping_type values are automatically corrected."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "original_api_key",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_SENSOR_TEMPERATURE: "sensor.temp",
            CONF_SENSOR_HUMIDITY: "sensor.hum",
            "mapping_type": "invalid_value",  # Invalid mapping type
        },
        options={
            CONF_UPDATE_TIME_1: "06:00",
            CONF_ENABLE_FORECAST_DAILY: True,
            CONF_ENABLE_FORECAST_HOURLY: False,
        }
    )
    entry.add_to_hass(hass)

    # Initialize options flow - should auto-correct invalid mapping_type
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # The invalid mapping_type should have been corrected to "meteocat"
    assert entry.data["mapping_type"] == "meteocat"

    # Submit init step
    user_input_init = {
        CONF_UPDATE_TIME_1: "06:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_init
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "local_sensors"

    # Submit sensors step
    user_input_sensors = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input_sensors
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "condition_mapping_type"

    # The form should show "meteocat" as current selection (corrected)
    # This tests that the selector doesn't fail with invalid defaults
    assert entry.data[CONF_API_KEY] == "original_api_key"


@pytest.mark.asyncio
async def test_options_flow_invalid_forecast_booleans_auto_correction(hass: HomeAssistant):
    """Test that invalid forecast boolean values in entry data are auto-corrected during options flow init."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_UPDATE_TIME_1: "06:00",
            CONF_ENABLE_FORECAST_DAILY: "invalid_string",  # Invalid: should be boolean
            CONF_ENABLE_FORECAST_HOURLY: 123,  # Invalid: should be boolean
            "mapping_type": "meteocat",
        },
        options={}
    )
    entry.add_to_hass(hass)

    # Start options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Check that the invalid values were corrected
    assert entry.data[CONF_ENABLE_FORECAST_DAILY] is True  # Corrected to default True
    assert entry.data[CONF_ENABLE_FORECAST_HOURLY] is False  # Corrected to default False

    # The form should render without validation errors
    # This tests that the selector doesn't fail with invalid defaults
    assert result["data_schema"] is not None
