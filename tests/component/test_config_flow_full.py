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
    CONF_MODE,
    CONF_COMARCA_CODE,
    CONF_STATION_CODE,
    MODE_EXTERNAL,
    CONF_MUNICIPALITY_CODE,
    MODE_LOCAL,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    CONF_UPDATE_TIME_3,
    CONF_ENABLE_FORECAST_DAILY,
    CONF_ENABLE_FORECAST_HOURLY,
)
from custom_components.meteocat_community_edition.api import MeteocatAPIError

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

@pytest.mark.asyncio
async def test_flow_update_times_step_local():
    """Test update times step in local mode."""
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

@pytest.mark.asyncio
async def test_flow_local_sensors_step():
    """Test local sensors step."""
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
    
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
    
    # Import constants for sensors
    from custom_components.meteocat_community_edition.const import CONF_SENSOR_TEMPERATURE, CONF_SENSOR_HUMIDITY
    
    user_input = {
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
    }
    
    result = await flow.async_step_local_sensors(user_input)
    
    assert result["type"] == "create_entry"
    flow.async_create_entry.assert_called_once()
    call_args = flow.async_create_entry.call_args[1]
    assert call_args["title"] == "Abrera"
    assert call_args["data"][CONF_SENSOR_TEMPERATURE] == "sensor.temp"
    assert call_args["data"][CONF_SENSOR_HUMIDITY] == "sensor.hum"
