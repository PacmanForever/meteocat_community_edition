"""Additional coverage tests for Meteocat config flow v2."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from custom_components.meteocat_community_edition.config_flow import MeteocatConfigFlow, MeteocatOptionsFlow
from custom_components.meteocat_community_edition.const import (
    CONF_API_KEY, CONF_MODE, MODE_LOCAL, CONF_MUNICIPALITY_CODE, CONF_COMARCA_CODE,
    CONF_SENSOR_TEMPERATURE, CONF_SENSOR_HUMIDITY, CONF_STATION_CODE
)

@pytest.mark.asyncio
async def test_creation_flow_custom_mapping_full_attributes():
    """Test creation flow with custom mapping having all attributes (lat/lon/provincia)."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    
    # Pre-populate flow state as if previous steps were completed
    flow.api_key = "test_key"
    flow.api_base_url = "http://test"
    flow.mode = MODE_LOCAL
    flow.municipality_code = "08001"
    flow.municipality_name = "Test Muni"
    flow.comarca_code = "10"
    flow.comarca_name = "Test Comarca"
    
    # Set the attributes targeted for coverage
    flow.municipality_lat = "41.1"
    flow.municipality_lon = "2.1"
    flow.provincia_code = "08"
    flow.provincia_name = "Barcelona"
    
    flow._local_sensors_input = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum"
    }
    
    # Mock async_create_entry
    with patch.object(flow, "async_create_entry", return_value={"type": "create_entry"}) as mock_create:
        result = await flow.async_step_condition_mapping_custom({
            "local_condition_entity": "sensor.cond",
            "condition_sunny": "1"
        })
        
        assert result["type"] == "create_entry"
        call_data = mock_create.call_args[1]["data"]
        
        # Verify targeted attributes are in data
        assert call_data["municipality_lat"] == "41.1"
        assert call_data["municipality_lon"] == "2.1"
        assert call_data["provincia_code"] == "08"
        assert call_data["provincia_name"] == "Barcelona"

@pytest.mark.asyncio
async def test_station_step_with_province_data():
    """Test station step extracting province data."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.context = {}  # Initialize context as mutable dict
    flow._stations = [
        {
            "codi": "X1", 
            "nom": "Station 1",
            "provincia": {"codi": "P1", "nom": "Prov 1"},
            "municipi": {"codi": "M1", "nom": "Muni 1"}
        }
    ]
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatConfigFlow.async_set_unique_id"), \
         patch("custom_components.meteocat_community_edition.config_flow.MeteocatConfigFlow._abort_if_unique_id_configured"), \
         patch("custom_components.meteocat_community_edition.config_flow.MeteocatConfigFlow.async_step_update_times", return_value={"type": "done"}):
        
        result = await flow.async_step_station({CONF_STATION_CODE: "X1"})
        
        # Use simple assert or fallback to check if attrs set
        assert flow.station_provincia_code == "P1"
        assert flow.station_provincia_name == "Prov 1"

@pytest.mark.asyncio
async def test_municipality_step_province_fallback():
    """Test municipality step getting province from comarca fallback."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.context = {}
    flow.comarca_code = "C1"
    
    # Municipality without province key (so .get defaults to {})
    # Note: If API returns None for province, we should handle that in code,
    # but here we simulate missing province data structure.
    flow._municipalities = [{
        "codi": "M1", "nom": "Muni 1"
        # "provincia" missing
    }]
    
    # Comarques with province
    flow._comarques = [{
        "codi": "C1", "nom": "Comarca 1",
        "provincia": {"codi": "P1", "nom": "Fallback Prov"}
    }]
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatConfigFlow.async_set_unique_id"), \
         patch("custom_components.meteocat_community_edition.config_flow.MeteocatConfigFlow._abort_if_unique_id_configured"), \
         patch("custom_components.meteocat_community_edition.config_flow.MeteocatConfigFlow.async_step_update_times", return_value={"type": "done"}):
        
        await flow.async_step_municipality({CONF_MUNICIPALITY_CODE: "M1"})
        
        assert flow.provincia_code == "P1"
        assert flow.provincia_name == "Fallback Prov"

@pytest.mark.asyncio
async def test_municipality_step_unique_id_abort():
    """Test municipality step checks unique_id."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.context = {}
    flow._municipalities = [{"codi": "M1", "nom": "Muni 1"}]
    
    # We want to ensure lines calling async_set_unique_id and abort are hit
    # async_set_unique_id is async, needs AsyncMock
    with patch.object(flow, "async_set_unique_id", new_callable=AsyncMock) as mock_set_uid, \
         patch.object(flow, "_abort_if_unique_id_configured") as mock_abort, \
         patch.object(flow, "async_step_update_times", return_value={"type": "done"}):
         
        await flow.async_step_municipality({CONF_MUNICIPALITY_CODE: "M1"})
        
        mock_set_uid.assert_called_with("municipal_M1")
        mock_abort.assert_called_once()

@pytest.mark.asyncio
async def test_options_init_boolean_input_validation():
    """Test options init step validating boolean inputs from user."""
    # This targets the user input processing block in async_step_init
    entry = MagicMock()
    entry.data = {CONF_API_KEY: "key", CONF_MODE: MODE_LOCAL}
    entry.options = {}
    
    flow = MeteocatOptionsFlow(entry)
    flow.hass = MagicMock()
    flow.hass.config_entries = MagicMock()
    
    user_input = {
        "update_time_1": "08:00",
        "enable_forecast_daily": "true", # string -> bool
        "enable_forecast_hourly": 0      # int -> bool
    }
    
    with patch.object(flow, "async_step_local_sensors", return_value={"type": "done"}):
        await flow.async_step_init(user_input)
        
        # Verify call to update_entry has booleans
        update_call = flow.hass.config_entries.async_update_entry
        assert update_call.called
        options_arg = update_call.call_args[1]["options"]
        assert options_arg["enable_forecast_daily"] is True
        assert options_arg["enable_forecast_hourly"] is False

@pytest.mark.asyncio
async def test_update_times_must_select_one_forecast_error():
    """Test update times step validation for forecast selection."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.mode = MODE_LOCAL
    
    user_input = {
        "update_time_1": "08:00",
        "enable_forecast_daily": False, 
        "enable_forecast_hourly": False
    }
    
    result = await flow.async_step_update_times(user_input)
    
    assert result["type"] == "form"
    assert result["errors"]["base"] == "must_select_one_forecast"

