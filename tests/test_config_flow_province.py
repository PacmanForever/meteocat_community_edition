"""Tests for Meteocat config flow province fallback."""
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from custom_components.meteocat_community_edition.config_flow import MeteocatConfigFlow
from custom_components.meteocat_community_edition.const import (
    CONF_API_KEY,
    CONF_MODE,
    CONF_MUNICIPALITY_CODE,
    CONF_COMARCA_CODE,
    MODE_MUNICIPI,
)

@pytest.fixture
def mock_api():
    """Mock the Meteocat API."""
    api = MagicMock()
    api.get_comarques = AsyncMock(return_value=[
        {"codi": "11", "nom": "Baix Llobregat", "provincia": {"codi": "08", "nom": "Barcelona"}},
        {"codi": "40", "nom": "Vallès Occidental", "provincia": {"codi": "08", "nom": "Barcelona"}}
    ])
    api.get_municipalities = AsyncMock(return_value=[
        {
            "codi": "080193", 
            "nom": "Barcelona", 
            "comarca": {"codi": "13"},
            "provincia": {"codi": "08", "nom": "Barcelona"}
        },
        {
            "codi": "081131", 
            "nom": "Granollers", 
            "comarca": {"codi": "41"},
            # Missing province data
        }
    ])
    return api

@pytest.mark.asyncio
async def test_municipality_step_extracts_province_from_municipality(mock_api):
    """Test that province is extracted from municipality data when available."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.mode = MODE_MUNICIPI
    flow.comarca_code = "13"
    flow.comarca_name = "Barcelonès"
    flow.api_key = "test_key"
    
    # Mock API calls
    with patch("custom_components.meteocat_community_edition.config_flow.async_get_clientsession"), \
         patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI", return_value=mock_api):
        
        # Pre-populate municipalities list as if comarca step just finished
        flow._municipalities = [
            {
                "codi": "080193", 
                "nom": "Barcelona", 
                "comarca": {"codi": "13"},
                "provincia": {"codi": "08", "nom": "Barcelona"}
            }
        ]
        
        # Select municipality
        result = await flow.async_step_municipality({CONF_MUNICIPALITY_CODE: "080193"})
        
        assert result["type"] == "form"
        assert result["step_id"] == "update_times"
        
        # Verify province was extracted
        assert flow.provincia_code == "08"
        assert flow.provincia_name == "Barcelona"

@pytest.mark.asyncio
async def test_municipality_step_extracts_province_from_comarca_fallback(mock_api):
    """Test that province is extracted from comarca when missing in municipality."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.mode = MODE_MUNICIPI
    flow.comarca_code = "40"
    flow.comarca_name = "Vallès Occidental"
    flow.api_key = "test_key"
    
    # Pre-populate comarques list
    flow._comarques = [
        {"codi": "40", "nom": "Vallès Occidental", "provincia": {"codi": "08", "nom": "Barcelona"}}
    ]
    
    # Mock API calls
    with patch("custom_components.meteocat_community_edition.config_flow.async_get_clientsession"), \
         patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI", return_value=mock_api):
        
        # Pre-populate municipalities list with one missing province
        flow._municipalities = [
            {
                "codi": "082665", 
                "nom": "Terrassa", 
                "comarca": {"codi": "40"},
                # No province data here
            }
        ]
        
        # Select municipality
        result = await flow.async_step_municipality({CONF_MUNICIPALITY_CODE: "082665"})
        
        assert result["type"] == "form"
        assert result["step_id"] == "update_times"
        
        # Verify province was extracted from comarca fallback
        assert flow.provincia_code == "08"
        assert flow.provincia_name == "Barcelona"

@pytest.mark.asyncio
async def test_municipality_step_handles_missing_province_everywhere(mock_api):
    """Test graceful handling when province is missing in both municipality and comarca."""
    flow = MeteocatConfigFlow()
    flow.hass = MagicMock()
    flow.mode = MODE_MUNICIPI
    flow.comarca_code = "99"
    flow.comarca_name = "Unknown"
    flow.api_key = "test_key"
    
    # Pre-populate comarques list with no province
    flow._comarques = [
        {"codi": "99", "nom": "Unknown"}
    ]
    
    # Mock API calls
    with patch("custom_components.meteocat_community_edition.config_flow.async_get_clientsession"), \
         patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI", return_value=mock_api):
        
        # Pre-populate municipalities list with no province
        flow._municipalities = [
            {
                "codi": "999999", 
                "nom": "Nowhere", 
                "comarca": {"codi": "99"},
            }
        ]
        
        # Select municipality
        result = await flow.async_step_municipality({CONF_MUNICIPALITY_CODE: "999999"})
        
        assert result["type"] == "form"
        assert result["step_id"] == "update_times"
        
        # Verify no province data
        assert not hasattr(flow, "provincia_code") or flow.provincia_code is None
        assert not hasattr(flow, "provincia_name") or flow.provincia_name is None
