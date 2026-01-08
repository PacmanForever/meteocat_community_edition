"""Test API station municipality logic."""
import pytest
from unittest.mock import MagicMock, patch
from custom_components.meteocat_community_edition.api import MeteocatAPI, MeteocatAPIError

@pytest.fixture
def api_client():
    from aiohttp import ClientSession
    session = MagicMock(spec=ClientSession)
    return MeteocatAPI("test_key", session)

async def test_get_station_municipality_match_name(api_client):
    """Test finding municipality by name match."""
    station = {
        "codi": "X1",
        "nom": "Estació de Barcelona - Raval",
        "coordenades": {"latitud": 1.0, "longitud": 1.0},
        "comarca": {"codi": "13"}
    }
    
    municipalities = [
        {"codi": "080193", "nom": "Barcelona", "comarca": {"codi": "13"}},
        {"codi": "080010", "nom": "Abrera", "comarca": {"codi": "11"}}
    ]
    
    with patch.object(api_client, "get_municipalities", return_value=municipalities):
        code = await api_client.find_municipality_for_station(station)
        assert code == "080193"

async def test_get_station_municipality_match_comarca(api_client):
    """Test finding municipality by comarca match (fallback)."""
    station = {
        "codi": "X1",
        "nom": "Estació Desconeguda",
        "coordenades": {"latitud": 1.0, "longitud": 1.0},
        "comarca": {"codi": "11"}
    }
    
    municipalities = [
        {"codi": "080193", "nom": "Barcelona", "comarca": {"codi": "13"}},
        {"codi": "080010", "nom": "Abrera", "comarca": {"codi": "11"}}
    ]
    
    with patch.object(api_client, "get_municipalities", return_value=municipalities):
        code = await api_client.find_municipality_for_station(station)
        assert code == "080010"

async def test_get_station_municipality_no_coordinates(api_client):
    """Test early exit if no coordinates."""
    station = {
        "codi": "X1",
        "nom": "No Coords",
        # Missing coordenades
        "comarca": {"codi": "13"}
    }
    
    with patch.object(api_client, "get_municipalities", return_value=[]):
        code = await api_client.find_municipality_for_station(station)
        assert code is None

async def test_get_station_municipality_no_match(api_client):
    """Test no match found."""
    station = {
        "codi": "X1",
        "nom": "No Match",
        "coordenades": {"latitud": 1.0, "longitud": 1.0},
        "comarca": {"codi": "99"}
    }
    
    municipalities = [
        {"codi": "080193", "nom": "Barcelona", "comarca": {"codi": "13"}}
    ]
    
    with patch.object(api_client, "get_municipalities", return_value=municipalities):
        code = await api_client.find_municipality_for_station(station)
        assert code is None

async def test_get_station_municipality_api_error(api_client):
    """Test error handling."""
    station = {
        "codi": "X1",
        "nom": "Error check",
        "coordenades": {"latitud": 1.0, "longitud": 1.0}
    }
    
    with patch.object(api_client, "get_municipalities", side_effect=MeteocatAPIError("Boom")):
        code = await api_client.find_municipality_for_station(station)
        assert code is None
