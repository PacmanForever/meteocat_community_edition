"""Tests for Meteocat config flow coverage."""
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from custom_components.meteocat_community_edition.config_flow import (
    MeteocatConfigFlow,
    validate_update_times,
    CONF_API_KEY,
    CONF_MODE,
    CONF_COMARCA_CODE,
    MODE_EXTERNAL,
    MODE_LOCAL,
)

@pytest.mark.asyncio
async def test_flow_user_step_no_comarques():
    """Test user step when no comarques found."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        # Return empty list
        mock_api.return_value.get_comarques = AsyncMock(return_value=[])
        
        result = await flow.async_step_user({CONF_API_KEY: "valid_key"})
        
        assert result["type"] == "form"
        assert result["errors"] == {"base": "no_comarques"}

@pytest.mark.asyncio
async def test_flow_comarca_step_no_stations():
    """Test comarca step when no stations found."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "valid_key"
    flow.mode = MODE_EXTERNAL
    flow._comarques = [{"codi": "1", "nom": "Alt Camp"}]
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        mock_api.return_value.get_stations_by_comarca = AsyncMock(return_value=[])
        
        result = await flow.async_step_comarca({CONF_COMARCA_CODE: "1"})
        
        assert result["type"] == "form"
        assert result["errors"] == {"base": "no_stations"}

@pytest.mark.asyncio
async def test_flow_comarca_step_no_municipalities():
    """Test comarca step when no municipalities found."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.api_key = "valid_key"
    flow.mode = MODE_LOCAL
    flow._comarques = [{"codi": "1", "nom": "Alt Camp"}]
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        # Return municipalities from other comarca
        mock_api.return_value.get_municipalities = AsyncMock(return_value=[
            {"codi": "08001", "nom": "Abrera", "comarca": {"codi": "2"}}
        ])
        
        result = await flow.async_step_comarca({CONF_COMARCA_CODE: "1"})
        
        assert result["type"] == "form"
        assert result["errors"] == {"base": "no_municipalities"}

@pytest.mark.asyncio
async def test_reauth_confirm_generic_exception():
    """Test reauth confirm generic exception."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.context = {"entry_id": "test_entry"}
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        mock_api.side_effect = Exception("Unexpected error")
        
        result = await flow.async_step_reauth_confirm({CONF_API_KEY: "new_key"})
        
        assert result["type"] == "form"
        assert result["errors"] == {"base": "unknown"}

def test_validate_update_times_coverage():
    """Test additional validation cases."""
    # Missing time 1
    assert "update_time_1" in validate_update_times("", "", "")
    assert "update_time_1" in validate_update_times(None, "", "")
    
    # Invalid time 3
    assert "update_time_3" in validate_update_times("08:00", "", "invalid")
    
    # Valid time 3
    assert validate_update_times("08:00", "", "20:00") == {}


@pytest.mark.asyncio
async def test_flow_condition_mapping_custom_duplicate_codes():
    """Test custom condition mapping with duplicate codes."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.mode = MODE_EXTERNAL
    flow.api_key = "test_key"
    flow.api_base_url = "https://api.meteo.cat"
    flow.municipality_name = "Test Municipality"
    flow._local_sensors_input = {
        "municipality_code": "08001",
        "municipality_name": "Test",
        "comarca_code": "01",
        "comarca_name": "Test Comarca"
    }

    user_input = {
        "local_condition_entity": "sensor.test_condition",
        "sunny": "1",
        "cloudy": "1" # Duplicate code
    }

    result = await flow.async_step_condition_mapping_custom(user_input)

    assert result["type"] == "form"
    assert result["errors"] == {"base": "duplicate_codes"}


@pytest.mark.asyncio
async def test_flow_condition_mapping_custom_empty_mapping():
    """Test custom condition mapping with empty mapping."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.mode = MODE_EXTERNAL
    flow.api_key = "test_key"
    flow.api_base_url = "https://api.meteo.cat"
    flow.municipality_name = "Test Municipality"
    flow._local_sensors_input = {
        "municipality_code": "08001",
        "municipality_name": "Test",
        "comarca_code": "01",
        "comarca_name": "Test Comarca"
    }

    user_input = {
        "local_condition_entity": "sensor.test_condition",
        # No conditions provided
    }

    # Since process_custom_mapping_form will raise "Empty mapping"
    # And currently we map "Empty mapping" to "invalid_format" via generic fallback or add check
    # Let's see implementation:
    # except ValueError as e: ... else: errors["base"] = "invalid_format"
    
    result = await flow.async_step_condition_mapping_custom(user_input)

    assert result["type"] == "form"
    assert result["errors"] == {"base": "invalid_format"}


@pytest.mark.asyncio
async def test_flow_condition_mapping_type_meteocat_with_location_data():
    """Test meteocat mapping type creates entry with location data."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.mode = MODE_EXTERNAL
    flow.api_key = "test_key"
    flow.api_base_url = "https://api.meteo.cat"
    flow.municipality_name = "Test Municipality"
    # Set the location attributes that should be included in entry data
    flow.municipality_lat = 41.123
    flow.municipality_lon = 2.456
    flow.provincia_code = "08"
    flow.provincia_name = "Barcelona"
    flow.municipality_code = "08001"
    flow.comarca_code = "01"
    flow.comarca_name = "Test Comarca"
    flow._local_sensors_input = {
        "municipality_code": "08001",
        "municipality_name": "Test",
        "comarca_code": "01",
        "comarca_name": "Test Comarca"
    }

    user_input = {
        "mapping_type": "meteocat"
    }

    # Mock async_create_entry to capture the call
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

    result = await flow.async_step_condition_mapping_type(user_input)

    assert result["type"] == "create_entry"
    flow.async_create_entry.assert_called_once()
    call_args = flow.async_create_entry.call_args[1]
    
    # Verify that location data is included in entry creation
    entry_data = call_args['data']
    assert "municipality_lat" in entry_data
    assert entry_data["municipality_lat"] == 41.123
    assert "municipality_lon" in entry_data
    assert entry_data["municipality_lon"] == 2.456
    assert "provincia_code" in entry_data
    assert entry_data["provincia_code"] == "08"
    assert "provincia_name" in entry_data
    assert entry_data["provincia_name"] == "Barcelona"


@pytest.mark.asyncio
async def test_flow_condition_mapping_type_meteocat_with_location_data():
    """Test meteocat mapping type creates entry with location data."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.mode = MODE_EXTERNAL
    flow.api_key = "test_key"
    flow.api_base_url = "https://api.meteo.cat"
    flow.municipality_name = "Test Municipality"
    # Set the location attributes that should be included in entry data
    flow.municipality_lat = 41.123
    flow.municipality_lon = 2.456
    flow.provincia_code = "08"
    flow.provincia_name = "Barcelona"
    flow.municipality_code = "08001"
    flow.comarca_code = "01"
    flow.comarca_name = "Test Comarca"
    flow._local_sensors_input = {
        "municipality_code": "08001",
        "municipality_name": "Test",
        "comarca_code": "01",
        "comarca_name": "Test Comarca"
    }

    user_input = {
        "mapping_type": "meteocat"
    }

    # Mock async_create_entry to capture the call
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

    result = await flow.async_step_condition_mapping_type(user_input)

    assert result["type"] == "create_entry"
    flow.async_create_entry.assert_called_once()
    call_args = flow.async_create_entry.call_args[1]
    
    # Verify that location data is included in entry creation
    entry_data = call_args['data']
    assert "municipality_lat" in entry_data
    assert entry_data["municipality_lat"] == 41.123
    assert "municipality_lon" in entry_data
    assert entry_data["municipality_lon"] == 2.456
    assert "provincia_code" in entry_data
    assert entry_data["provincia_code"] == "08"
    assert "provincia_name" in entry_data
    assert entry_data["provincia_name"] == "Barcelona"


@pytest.mark.asyncio
async def test_flow_condition_mapping_custom_with_location_data():
    """Test custom condition mapping creates entry with location data."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.mode = MODE_EXTERNAL
    flow.api_key = "test_key"
    flow.api_base_url = "https://api.meteo.cat"
    flow.municipality_name = "Test Municipality"
    # Set the location attributes that should be included in entry data
    flow.municipality_lat = 41.123
    flow.municipality_lon = 2.456
    flow.provincia_code = "08"
    flow.provincia_name = "Barcelona"
    flow.municipality_code = "08001"
    flow.comarca_code = "01"
    flow.comarca_name = "Test Comarca"
    flow._local_sensors_input = {
        "municipality_code": "08001",
        "municipality_name": "Test",
        "comarca_code": "01",
        "comarca_name": "Test Comarca"
    }

    user_input = {
        "local_condition_entity": "sensor.test_condition",
        "sunny": "0",
        "cloudy": "1"
    }

    # Mock async_create_entry to capture the call
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

    result = await flow.async_step_condition_mapping_custom(user_input)

    assert result["type"] == "create_entry"
    flow.async_create_entry.assert_called_once()
    call_args = flow.async_create_entry.call_args[1]
    
    # Verify that location data is included in entry creation
    entry_data = call_args['data']
    assert "municipality_lat" in entry_data
    assert entry_data["municipality_lat"] == 41.123
    assert "municipality_lon" in entry_data
    assert entry_data["municipality_lon"] == 2.456
    assert "provincia_code" in entry_data
    assert entry_data["provincia_code"] == "08"
    assert "provincia_name" in entry_data
    assert entry_data["provincia_name"] == "Barcelona"




@pytest.mark.asyncio
async def test_step_reauth():
    """Test reauth step."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.context = {"entry_id": "test_entry"}

    mock_entry = MagicMock()
    flow.hass.config_entries.async_get_entry.return_value = mock_entry

    with patch.object(flow, 'async_step_reauth_confirm') as mock_reauth_confirm:
        mock_reauth_confirm.return_value = {"type": "form"}

        result = await flow.async_step_reauth({})

        flow.hass.config_entries.async_get_entry.assert_called_once_with("test_entry")
        mock_reauth_confirm.assert_called_once()


@pytest.mark.asyncio
async def test_step_user_unexpected_exception():
    """Test user step with unexpected exception."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()

    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        mock_api.return_value.get_comarques.side_effect = Exception("Unexpected error")

        result = await flow.async_step_user({CONF_API_KEY: "test_key"})

        assert result["type"] == "form"
        assert result["errors"] == {"base": "unknown"}
