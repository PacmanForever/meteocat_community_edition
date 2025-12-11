"""Tests for Meteocat config flow logic."""
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from custom_components.meteocat_community_edition.config_flow import (
    MeteocatConfigFlow,
    validate_update_times,
    is_valid_time_format,
    CONF_API_KEY,
    CONF_API_BASE_URL,
    CONF_MODE,
    CONF_COMARCA_CODE,
    CONF_COMARCA_NAME,
    CONF_STATION_CODE,
    MODE_EXTERNAL,
    CONF_MUNICIPALITY_CODE,
    CONF_MUNICIPALITY_NAME,
    MODE_LOCAL,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    CONF_UPDATE_TIME_3,
    CONF_ENABLE_FORECAST_DAILY,
    CONF_ENABLE_FORECAST_HOURLY,
)
from custom_components.meteocat_community_edition.api import MeteocatAPIError
from custom_components.meteocat_community_edition.const import CONF_SENSOR_TEMPERATURE, CONF_SENSOR_HUMIDITY

def test_is_valid_time_format():
    """Test time format validation."""
    assert is_valid_time_format("06:00")
    assert is_valid_time_format("23:59")
    assert not is_valid_time_format("24:00")
    assert not is_valid_time_format("12:60")
    assert not is_valid_time_format("invalid")
    assert not is_valid_time_format("")

def test_validate_update_times():
    """Test update times validation."""
    # Valid times
    assert validate_update_times("08:00", "20:00", "") == {}
    assert validate_update_times("08:00", "", "") == {}
    
    # Invalid format
    assert "update_time_1" in validate_update_times("invalid", "", "")
    assert "update_time_2" in validate_update_times("08:00", "invalid", "")
    
    # Duplicates
    assert "base" in validate_update_times("08:00", "08:00", "")
    assert "base" in validate_update_times("08:00", "20:00", "08:00")

@pytest.mark.asyncio
async def test_flow_user_step_valid_api_key():
    """Test user step with valid API key."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        mock_api.return_value.get_comarques = AsyncMock(return_value=[{"codi": "1", "nom": "Alt Camp"}])
        
        result = await flow.async_step_user({CONF_API_KEY: "valid_key"})
        
        assert result["type"] == "form"
        assert result["step_id"] == "mode"
        assert flow.api_key == "valid_key"

@pytest.mark.asyncio
async def test_flow_user_step_invalid_api_key():
    """Test user step with invalid API key."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        mock_api.return_value.get_comarques = AsyncMock(side_effect=MeteocatAPIError("Invalid key"))
        
        result = await flow.async_step_user({CONF_API_KEY: "invalid_key"})
        
        assert result["type"] == "form"
        assert result["errors"] == {"base": "cannot_connect"}

@pytest.mark.asyncio
async def test_flow_mode_step():
    """Test mode selection step."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "valid_key"
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        mock_api.return_value.get_comarques = AsyncMock(return_value=[{"codi": "1", "nom": "Alt Camp"}])
        
        result = await flow.async_step_mode({CONF_MODE: MODE_EXTERNAL})
        
        assert result["type"] == "form"
        assert result["step_id"] == "comarca"
        assert flow.mode == MODE_EXTERNAL

@pytest.mark.asyncio
async def test_flow_comarca_step_estacio():
    """Test comarca selection step in station mode."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "valid_key"
    flow.mode = MODE_EXTERNAL
    flow._comarques = [{"codi": "1", "nom": "Alt Camp"}]
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        mock_api.return_value.get_stations_by_comarca = AsyncMock(return_value=[{"codi": "YM", "nom": "Granollers"}])
        
        result = await flow.async_step_comarca({CONF_COMARCA_CODE: "1"})
        
        assert result["type"] == "form"
        assert result["step_id"] == "station"
        assert flow.comarca_code == "1"
        assert len(flow._stations) == 1

@pytest.mark.asyncio
async def test_flow_station_step():
    """Test station selection step."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "valid_key"
    flow.mode = MODE_EXTERNAL
    flow.comarca_code = "1"
    flow._stations = [{"codi": "YM", "nom": "Granollers"}]
    flow.context = {}
    
    # Mock async_set_unique_id and _abort_if_unique_id_configured
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    
    result = await flow.async_step_station({CONF_STATION_CODE: "YM"})
    
    assert result["type"] == "form"
    assert result["step_id"] == "update_times"
    assert flow.station_code == "YM"
    assert flow.station_name == "Granollers"

@pytest.mark.asyncio
async def test_flow_municipality_step():
    """Test municipality selection step."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "valid_key"
    flow.mode = MODE_LOCAL
    flow.comarca_code = "1"
    flow._municipalities = [{"codi": "08001", "nom": "Abrera"}]
    flow.context = {}
    
    # Mock async_set_unique_id and _abort_if_unique_id_configured
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    
    result = await flow.async_step_municipality({CONF_MUNICIPALITY_CODE: "08001"})
    
    assert result["type"] == "form"
    assert result["step_id"] == "update_times"
    assert flow.municipality_code == "08001"
    assert flow.municipality_name == "Abrera"

@pytest.mark.asyncio
async def test_flow_update_times_step_estacio():
    """Test update times step in station mode."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "valid_key"
    flow.mode = MODE_EXTERNAL
    flow.station_code = "YM"
    flow.station_name = "Granollers"
    flow.comarca_code = "1"
    flow.comarca_name = "Valles Oriental"
    flow.context = {}
    flow.api_base_url = "https://api.meteocat.cat/release/v1"
    
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
    
    user_input = {
        CONF_UPDATE_TIME_1: "08:00",
        CONF_UPDATE_TIME_2: "20:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await flow.async_step_update_times(user_input)
    
    assert result["type"] == "create_entry"
    flow.async_create_entry.assert_called_once()
    call_args = flow.async_create_entry.call_args[1]
    assert call_args["title"] == "Granollers YM"
    assert call_args["data"][CONF_UPDATE_TIME_1] == "08:00"
    assert call_args["data"][CONF_UPDATE_TIME_2] == "20:00"
    # Regression test: ensure API key is included in external station entry data
    assert call_args["data"][CONF_API_KEY] == "valid_key"
    assert call_args["data"][CONF_MODE] == MODE_EXTERNAL

@pytest.mark.asyncio
async def test_flow_update_times_step_local():
    """Test that after update_times in local mode, the flow transitions to local_sensors, i després a condition_mapping."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "valid_key"
    flow.mode = MODE_LOCAL
    flow.municipality_code = "08001"
    flow.municipality_name = "Abrera"
    flow.comarca_code = "1"
    flow.comarca_name = "Baix Llobregat"
    flow.context = {}
    flow.api_base_url = "https://api.meteocat.cat/release/v1"
    user_input = {
        CONF_UPDATE_TIME_1: "08:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: True,
    }
    # Should transition to local_sensors step
    result = await flow.async_step_update_times(user_input)
    assert result["type"] == "form"
    assert result["step_id"] == "local_sensors"
    # Simula resposta de sensors locals
    sensors_input = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }
    result2 = await flow.async_step_local_sensors(sensors_input)
    assert result2["type"] == "form"
    assert result2["step_id"] == "condition_mapping_type"

@pytest.mark.asyncio
async def test_flow_local_sensors_step():
    """Test que la pantalla de sensors locals porta a la de mapping, i després es crea l'entrada."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "valid_key"
    flow.mode = MODE_LOCAL
    flow.municipality_code = "08001"
    flow.municipality_name = "Abrera"
    flow.comarca_code = "1"
    flow.comarca_name = "Baix Llobregat"
    flow.update_time_1 = "08:00"
    flow.update_time_2 = ""
    flow.update_time_3 = ""
    flow.enable_forecast_daily = True
    flow.enable_forecast_hourly = True
    flow.context = {}
    flow.api_base_url = "https://api.meteocat.cat/release/v1"
    # Import constants for sensors
    from custom_components.meteocat_community_edition.const import CONF_SENSOR_TEMPERATURE, CONF_SENSOR_HUMIDITY
    sensors_input = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }
    result = await flow.async_step_local_sensors(sensors_input)
    assert result["type"] == "form"
    assert result["step_id"] == "condition_mapping_type"

@pytest.mark.asyncio
async def test_flow_mapping_step_called():
    """Test que la pantalla de mapping (condition_mapping) es crida després de sensors locals."""
    from custom_components.meteocat_community_edition.const import CONF_SENSOR_TEMPERATURE, CONF_SENSOR_HUMIDITY
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "valid_key"
    flow.mode = MODE_LOCAL
    flow.municipality_code = "08001"
    flow.municipality_name = "Abrera"
    flow.comarca_code = "1"
    flow.comarca_name = "Baix Llobregat"
    flow.update_time_1 = "08:00"
    flow.update_time_2 = ""
    flow.update_time_3 = ""
    flow.enable_forecast_daily = True
    flow.enable_forecast_hourly = True
    flow.context = {}
    flow.api_base_url = "https://api.meteocat.cat/release/v1"
    sensors_input = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }
    result = await flow.async_step_local_sensors(sensors_input)
    assert result["type"] == "form"
    assert result["step_id"] == "condition_mapping_type"

@pytest.mark.asyncio
async def test_flow_mapping_type_meteocat_creates_entry():
    """Selecting 'meteocat' in mapping type creates entry immediately."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "test_api_key"  # Add API key
    flow.mode = MODE_LOCAL  # Add mode
    flow.municipality_code = "08001"  # Add municipality data
    flow.municipality_name = "Abrera"
    flow.comarca_code = "1"
    flow.comarca_name = "Baix Llobregat"
    flow._local_sensors_input = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }
    flow.api_base_url = "https://api.meteocat.cat/release/v1"
    result = await flow.async_step_condition_mapping_type({"mapping_type": "meteocat"})
    assert result["type"] == "create_entry"
    assert result["title"] == "Abrera"
    assert result["data"][CONF_SENSOR_TEMPERATURE] == "sensor.temp"
    assert result["data"][CONF_SENSOR_HUMIDITY] == "sensor.hum"
    assert result["data"]["mapping_type"] == "meteocat"
    # Regression test: ensure API key is included in entry data
    assert result["data"][CONF_API_KEY] == "test_api_key"
    assert result["data"][CONF_API_BASE_URL] == "https://api.meteocat.cat/release/v1"
    # Regression test: ensure mode is included in entry data
    assert result["data"][CONF_MODE] == MODE_LOCAL
    # Regression test: ensure municipality and comarca data are included
    assert result["data"][CONF_MUNICIPALITY_CODE] == "08001"
    assert result["data"][CONF_MUNICIPALITY_NAME] == "Abrera"
    assert result["data"][CONF_COMARCA_CODE] == "1"
    assert result["data"][CONF_COMARCA_NAME] == "Baix Llobregat"

@pytest.mark.asyncio
async def test_flow_mapping_type_custom_leads_to_custom_step():
    """Selecting 'custom' in mapping type leads to custom mapping step."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow._local_sensors_input = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }
    flow.municipality_name = "Abrera"
    flow.api_base_url = "https://api.meteocat.cat/release/v1"
    result = await flow.async_step_condition_mapping_type({"mapping_type": "custom"})
    assert result["type"] == "form"
    assert result["step_id"] == "condition_mapping_custom"
    # Cannot check default mapping directly due to ObjectSelector limitations

@pytest.mark.asyncio
async def test_flow_custom_mapping_requires_fields():
    """Custom mapping step requires both fields."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "test_api_key"  # Add API key
    flow.mode = MODE_LOCAL  # Add mode
    flow.municipality_code = "08001"  # Add municipality data
    flow.municipality_name = "Abrera"
    flow.comarca_code = "1"
    flow.comarca_name = "Baix Llobregat"
    flow._local_sensors_input = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }
    flow.api_base_url = "https://api.meteocat.cat/release/v1"
    # Missing both fields
    result = await flow.async_step_condition_mapping_custom({})
    assert result["type"] == "form"
    assert "local_condition_entity" in result["errors"]
    assert "custom_condition_mapping" in result["errors"]
    # Only one field
    result2 = await flow.async_step_condition_mapping_custom({"local_condition_entity": "sensor.mycond"})
    assert "custom_condition_mapping" in result2["errors"]
    result3 = await flow.async_step_condition_mapping_custom({"custom_condition_mapping": "0: sunny"})
    assert "local_condition_entity" in result3["errors"]
    # Both fields present
    result4 = await flow.async_step_condition_mapping_custom({"local_condition_entity": "sensor.mycond", "custom_condition_mapping": "0: sunny"})
    assert result4["type"] == "create_entry"
    assert result4["data"]["mapping_type"] == "custom"
    assert result4["data"]["local_condition_entity"] == "sensor.mycond"
    assert "sunny" in result4["data"]["custom_condition_mapping"].values()
    # Regression test: ensure API key is included in entry data
    assert result4["data"][CONF_API_KEY] == "test_api_key"
    assert result4["data"][CONF_API_BASE_URL] == "https://api.meteocat.cat/release/v1"
    # Regression test: ensure mode is included in entry data
    assert result4["data"][CONF_MODE] == MODE_LOCAL
    # Regression test: ensure municipality and comarca data are included
    assert result4["data"][CONF_MUNICIPALITY_CODE] == "08001"
    assert result4["data"][CONF_MUNICIPALITY_NAME] == "Abrera"
    assert result4["data"][CONF_COMARCA_CODE] == "1"
    assert result4["data"][CONF_COMARCA_NAME] == "Baix Llobregat"

@pytest.mark.asyncio
async def test_coordinator_handles_missing_api_key():
    """Test that coordinator properly handles entries without API key (migration scenario)."""
    from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
    from unittest.mock import MagicMock
    
    hass = MagicMock()
    # Create a mock entry without API key (simulating old entry)
    entry = MagicMock()
    entry.title = "Test Station"
    entry.data = {
        "mode": "external",
        "station_code": "TEST",
        "station_name": "Test Station"
        # Missing api_key intentionally
    }
    entry.options = {}
    
    # Should raise ValueError with clear message
    with pytest.raises(ValueError, match="Entry 'Test Station' is missing API key"):
        MeteocatCoordinator(hass, entry)


@pytest.mark.asyncio
async def test_flow_external_mode_creates_entry_with_correct_mode():
    """Test that external mode station entries include the correct mode in data."""
    from custom_components.meteocat_community_edition.config_flow import MeteocatConfigFlow
    from unittest.mock import MagicMock, AsyncMock
    
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "test_api_key"
    flow.mode = MODE_EXTERNAL
    flow.station_code = "YM"
    flow.station_name = "Granollers"
    flow.comarca_code = "1"
    flow.comarca_name = "Vallès Oriental"
    flow.update_time_1 = "08:00"
    flow.update_time_2 = ""
    flow.update_time_3 = ""
    flow.enable_forecast_daily = True
    flow.enable_forecast_hourly = False
    flow.api_base_url = "https://api.meteocat.cat/release/v1"
    
    # Mock async_set_unique_id
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    
    user_input = {
        CONF_UPDATE_TIME_1: "08:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False,
    }
    
    result = await flow.async_step_update_times(user_input)
    
    assert result["type"] == "create_entry"
    assert result["title"] == "Granollers YM"
    assert result["data"][CONF_MODE] == MODE_EXTERNAL
    assert result["data"][CONF_API_KEY] == "test_api_key"
    assert result["data"][CONF_STATION_CODE] == "YM"
