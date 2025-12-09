"""Test schema validation for Meteocat config flow and options flow."""
import pytest
import voluptuous as vol
from unittest.mock import MagicMock, AsyncMock
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteocat_community_edition.config_flow import MeteocatConfigFlow, MeteocatOptionsFlow
from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_MODE,
    MODE_EXTERNAL,
    MODE_LOCAL,
    CONF_STATION_CODE,
    CONF_MUNICIPALITY_CODE,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    CONF_UPDATE_TIME_3,
    CONF_ENABLE_FORECAST_DAILY,
    CONF_ENABLE_FORECAST_HOURLY,
)

def get_schema_keys(schema):
    """Extract keys from a voluptuous schema."""
    keys = []
    if isinstance(schema, vol.Schema):
        for key in schema.schema:
            if isinstance(key, vol.Marker):
                keys.append(key.schema)
            else:
                keys.append(key)
    return keys

@pytest.mark.asyncio
async def test_config_flow_update_times_schema_contains_all_fields():
    """Test that the update_times step in config flow contains all expected fields."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.mode = MODE_EXTERNAL
    flow.config_entry = MagicMock()
    flow.config_entry.data = {}
    flow.config_entry.options = {}
    
    # Simulate entering the step
    result = await flow.async_step_update_times()
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "update_times"
    
    schema_keys = get_schema_keys(result["data_schema"])
    
    assert CONF_UPDATE_TIME_1 in schema_keys
    assert CONF_UPDATE_TIME_2 in schema_keys
    assert CONF_UPDATE_TIME_3 in schema_keys
    assert CONF_ENABLE_FORECAST_DAILY in schema_keys
    assert CONF_ENABLE_FORECAST_HOURLY in schema_keys
    
    # Check description placeholders
    assert "measurements_info" in result["description_placeholders"]

@pytest.mark.asyncio
async def test_options_flow_init_schema_contains_all_fields(hass: HomeAssistant):
    """Test that the init step in options flow contains all expected fields."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_EXTERNAL,
            CONF_STATION_CODE: "YM",
            CONF_MUNICIPALITY_CODE: "081131",
            CONF_UPDATE_TIME_1: "06:00",
        },
        options={}
    )
    entry.add_to_hass(hass)
    
    flow = MeteocatOptionsFlow(entry)
    flow.hass = hass
    
    result = await flow.async_step_init()
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"
    
    schema_keys = get_schema_keys(result["data_schema"])
    
    assert CONF_UPDATE_TIME_1 in schema_keys
    assert CONF_UPDATE_TIME_2 in schema_keys
    assert CONF_UPDATE_TIME_3 in schema_keys
    assert CONF_ENABLE_FORECAST_DAILY in schema_keys
    assert CONF_ENABLE_FORECAST_HOURLY in schema_keys
    
    # Check description placeholders
    assert "measurements_info" in result["description_placeholders"]
