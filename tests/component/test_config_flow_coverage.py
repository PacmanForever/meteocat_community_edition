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
