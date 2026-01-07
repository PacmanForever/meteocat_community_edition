"""Final coverage tests for config_flow.py."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from homeassistant import data_entry_flow
from homeassistant.config_entries import ConfigEntry
from custom_components.meteocat_community_edition.config_flow import MeteocatConfigFlow, MeteocatOptionsFlow
from custom_components.meteocat_community_edition.const import CONF_MUNICIPALITY_CODE, CONF_ENABLE_FORECAST_DAILY

async def test_municipality_duplicate_check_execution(hass):
    """Test that municipality step executes lines 637-642 (duplicate check)."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    
    # Setup dependencies
    flow._municipalities = [{"codi": "123", "nom": "Test Muni"}]
    
    # We want to verify lines 637-642 are executed.
    # 637: unique_id = ...
    # 639: await self.async_set_unique_id(unique_id)
    # 641: self._abort_if_unique_id_configured()
    
    with patch.object(flow, "async_set_unique_id", return_value=AsyncMock()) as mock_set_unique_id, \
         patch.object(flow, "_abort_if_unique_id_configured") as mock_abort, \
         patch.object(flow, "async_step_update_times", return_value=AsyncMock(return_value={"type": "done"})):
        
        await flow.async_step_municipality({CONF_MUNICIPALITY_CODE: "123"})
        
        # Verify execution
        mock_set_unique_id.assert_called_once()
        mock_abort.assert_called_once()

async def test_options_init_boolean_conversion_coverage(hass):
    """Test options init coverages lines 980-982 (boolean conversion)."""
    # Setup entry with non-bool values
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"  # Add entry_id
    entry.data = {
        CONF_ENABLE_FORECAST_DAILY: "not_a_bool", 
        "enable_forecast_hourly": 123,
        "mode": "local",
        "api_key": "key"
    }
    entry.options = {} 
    
    flow = MeteocatOptionsFlow(entry)
    flow.hass = hass
    # Mock update entry to prevent using real registry
    flow.hass.config_entries.async_update_entry = MagicMock()
    
    # Run init step (user_input=None)
    result = await flow.async_step_init()
    
    assert result["type"] == "form"
    schema = result["data_schema"]
    
    found_daily = False
    for key in schema.schema:
        if str(key) == CONF_ENABLE_FORECAST_DAILY:
            found_daily = True
            assert key.default() is True
            break
            
    assert found_daily

async def test_mapping_type_default_logic_valid_existing(hass):
    """Test mapping type step picks up valid existing value (lines 171-173)."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id_valid"
    entry.data = {
        "mapping_type": "custom",
    }
    
    flow = MeteocatConfigFlow()
    flow.hass = hass
    # Manually attach config_entry to simulate re-configure context or shared logic
    flow.config_entry = entry
    
    result = await flow.async_step_condition_mapping_type()
    
    assert result["type"] == "form"
    schema = result["data_schema"]
    key = list(schema.schema.keys())[0]
    # Should default to "custom"
    assert key.default() == "custom"
