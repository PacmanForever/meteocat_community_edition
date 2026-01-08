"""Extended tests for Meteocat API client."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientSession

from custom_components.meteocat_community_edition.api import (
    MeteocatAPI,
    MeteocatAPIError,
)

@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    return MagicMock(spec=ClientSession)

@pytest.fixture
def api_client(mock_session):
    """Create an API client with mock session."""
    return MeteocatAPI("test_api_key", mock_session, "https://api.test.com")

@pytest.mark.asyncio
async def test_find_municipality_for_station_by_name(api_client):
    """Test finding municipality by name match."""
    station = {
        "codi": "X1",
        "nom": "Barcelona - Raval",
        "coordenades": {"latitud": 41.3, "longitud": 2.1},
        "comarca": {"codi": "13"}
    }
    
    municipalities = [
        {"codi": "080193", "nom": "Barcelona", "comarca": {"codi": "13"}},
        {"codi": "081017", "nom": "Hospitalet de Llobregat", "comarca": {"codi": "13"}}
    ]
    
    api_client.get_municipalities = AsyncMock(return_value=municipalities)
    
    result = await api_client.find_municipality_for_station(station)
    assert result == "080193"

@pytest.mark.asyncio
async def test_find_municipality_for_station_by_comarca(api_client):
    """Test finding municipality by comarca fallback."""
    station = {
        "codi": "X2",
        "nom": "Unknown Place",
        "coordenades": {"latitud": 41.5, "longitud": 2.2},
        "comarca": {"codi": "13"}
    }
    
    municipalities = [
        {"codi": "080193", "nom": "Barcelona", "comarca": {"codi": "13"}},
        {"codi": "999999", "nom": "Other Place", "comarca": {"codi": "99"}}
    ]
    
    api_client.get_municipalities = AsyncMock(return_value=municipalities)
    
    result = await api_client.find_municipality_for_station(station)
    assert result == "080193"

@pytest.mark.asyncio
async def test_find_municipality_for_station_no_match(api_client):
    """Test finding municipality with no match."""
    station = {
        "codi": "X3",
        "nom": "Nowhere",
        "coordenades": {"latitud": 41.5, "longitud": 2.2},
        "comarca": {"codi": "99"}
    }
    
    municipalities = [
        {"codi": "080193", "nom": "Barcelona", "comarca": {"codi": "13"}}
    ]
    
    api_client.get_municipalities = AsyncMock(return_value=municipalities)
    
    result = await api_client.find_municipality_for_station(station)
    assert result is None

@pytest.mark.asyncio
async def test_find_municipality_for_station_no_coords(api_client):
    """Test finding municipality with missing coordinates."""
    station = {
        "codi": "X4",
        "nom": "No Coords",
        "coordenades": {}
    }
    
    api_client.get_municipalities = AsyncMock()
    
    result = await api_client.find_municipality_for_station(station)
    assert result is None
    api_client.get_municipalities.assert_called_once()

@pytest.mark.asyncio
async def test_find_municipality_for_station_error(api_client):
    """Test error handling in find_municipality_for_station."""
    station = {
        "codi": "X5",
        "nom": "Error Station",
        "coordenades": {"latitud": 41.5, "longitud": 2.2}
    }
    
    api_client.get_municipalities = AsyncMock(side_effect=MeteocatAPIError("API Error"))
    
    result = await api_client.find_municipality_for_station(station)
    assert result is None
