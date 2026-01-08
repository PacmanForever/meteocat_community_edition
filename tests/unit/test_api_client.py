"""Tests for Meteocat API client."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from aiohttp import ClientSession
from unittest.mock import AsyncMock, MagicMock, patch

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
async def test_get_comarques(api_client, mock_session):
    """Test getting comarques list."""
    import json
    mock_response = AsyncMock()
    mock_data = [
        {"codi": "01", "nom": "Alt Camp"},
        {"codi": "02", "nom": "Alt Empordà"},
    ]
    mock_response.read = AsyncMock(return_value=json.dumps(mock_data).encode('utf-8'))
    mock_response.raise_for_status = MagicMock()
    mock_response.status = 200
    
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await api_client.get_comarques()
    
    assert len(result) == 2
    assert result[0]["codi"] == "01"
    assert result[0]["nom"] == "Alt Camp"


@pytest.mark.asyncio
async def test_get_stations(api_client, mock_session):
    """Test getting stations list."""
    import json
    mock_response = AsyncMock()
    mock_data = [
        {"codi": "UG", "nom": "Girona"},
        {"codi": "D5", "nom": "Barcelona"},
    ]
    mock_response.read = AsyncMock(return_value=json.dumps(mock_data).encode('utf-8'))
    mock_response.raise_for_status = MagicMock()
    mock_response.status = 200
    
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await api_client.get_stations()
    
    assert len(result) == 2
    assert result[0]["codi"] == "UG"


@pytest.mark.asyncio
async def test_api_error_handling(api_client, mock_session):
    """Test API error handling."""
    from aiohttp import ClientError
    
    mock_session.request.side_effect = ClientError("Connection error")
    
    with pytest.raises(MeteocatAPIError) as exc_info:
        await api_client.get_comarques()
    
    assert "Error connecting to Meteocat API" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_station_measurements(api_client, mock_session):
    """Test getting station measurements."""
    import json
    mock_response = AsyncMock()
    mock_data = [
        {
            "codi": "UG",
            "variables": [
                {"codi": 32, "lectures": [{"valor": 15.5}]},
                {"codi": 33, "lectures": [{"valor": 65.0}]},
            ],
        }
    ]
    mock_response.read = AsyncMock(return_value=json.dumps(mock_data).encode('utf-8'))
    mock_response.raise_for_status = MagicMock()
    mock_response.status = 200
    
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await api_client.get_station_measurements("UG")
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["codi"] == "UG"
    assert len(result[0]["variables"]) == 2


@pytest.mark.asyncio
async def test_get_quotes(api_client, mock_session):
    """Test getting API quota information."""
    import json
    mock_response = AsyncMock()
    mock_data = {
        "client": {"nom": "Test Client"},
        "plans": [
            {"nom": "Prediccio_100", "requests_left": 950, "requests_total": 1000},
            {"nom": "Referencia_200", "requests_left": 1800, "requests_total": 2000},
        ]
    }
    mock_response.read = AsyncMock(return_value=json.dumps(mock_data).encode('utf-8'))
    mock_response.raise_for_status = MagicMock()
    mock_response.status = 200
    
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await api_client.get_quotes()
    
    assert "client" in result
    assert "plans" in result
    assert len(result["plans"]) == 2
    assert result["plans"][0]["nom"] == "Prediccio_100"


@pytest.mark.asyncio
async def test_get_municipal_forecast(api_client, mock_session):
    """Test getting municipal forecast."""
    import json
    mock_response = AsyncMock()
    mock_data = {
        "dies": [
            {
                "data": "2025-11-24",
                "variables": {
                    "tmax": {"valor": 20},
                    "tmin": {"valor": 10}
                }
            }
        ]
    }
    mock_response.read = AsyncMock(return_value=json.dumps(mock_data).encode('utf-8'))
    mock_response.raise_for_status = MagicMock()
    mock_response.status = 200
    
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await api_client.get_municipal_forecast("081131")
    
    assert "dies" in result
    assert len(result["dies"]) == 1
    assert result["dies"][0]["data"] == "2025-11-24"


@pytest.mark.asyncio
async def test_get_stations_by_comarca(api_client, mock_session):
    """Test getting stations filtered by comarca."""
    import json
    mock_response = AsyncMock()
    mock_data = [
        {
            "codi": "C6",
            "nom": "Tarragona - Port",
            "comarca": {"codi": "01", "nom": "Alt Camp"}
        },
        {
            "codi": "C7", 
            "nom": "Vilafranca del Penedès",
            "comarca": {"codi": "02", "nom": "Alt Penedès"}
        },
        {
            "codi": "C8",
            "nom": "Valls",
            "comarca": {"codi": "01", "nom": "Alt Camp"}
        }
    ]
    mock_response.read = AsyncMock(return_value=json.dumps(mock_data).encode('utf-8'))
    mock_response.raise_for_status = MagicMock()
    mock_response.status = 200
    
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await api_client.get_stations_by_comarca("01")
    
    assert len(result) == 2
    assert result[0]["codi"] == "C6"
    assert result[0]["comarca"]["codi"] == "01"
    assert result[1]["codi"] == "C8"
    assert result[1]["comarca"]["codi"] == "01"


@pytest.mark.asyncio
async def test_get_municipalities(api_client, mock_session):
    """Test getting municipalities list."""
    import json
    mock_response = AsyncMock()
    mock_data = [
        {"codi": "081131", "nom": "Barcelona"},
        {"codi": "081232", "nom": "Girona"},
    ]
    mock_response.read = AsyncMock(return_value=json.dumps(mock_data).encode('utf-8'))
    mock_response.raise_for_status = MagicMock()
    mock_response.status = 200
    
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await api_client.get_municipalities()
    
    assert len(result) == 2
    assert result[0]["codi"] == "081131"
    assert result[0]["nom"] == "Barcelona"


@pytest.mark.asyncio
async def test_get_hourly_forecast(api_client, mock_session):
    """Test getting hourly forecast."""
    import json
    mock_response = AsyncMock()
    mock_data = {
        "municipi": "081131",
        "hores": [
            {"data_hora": "2025-11-24T12:00:00", "temperatura": 15.5},
            {"data_hora": "2025-11-24T13:00:00", "temperatura": 16.2},
        ]
    }
    mock_response.read = AsyncMock(return_value=json.dumps(mock_data).encode('utf-8'))
    mock_response.raise_for_status = MagicMock()
    mock_response.status = 200
    
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await api_client.get_hourly_forecast("081131")
    
    assert result["municipi"] == "081131"
    assert "hores" in result
    assert len(result["hores"]) == 2
    assert result["hores"][0]["temperatura"] == 15.5


@pytest.mark.asyncio
async def test_api_initialization():
    """Test API client initialization."""
    session = MagicMock(spec=ClientSession)
    api = MeteocatAPI("test_key", session, "https://api.test.com")
    
    assert api.api_key == "test_key"
    assert api.session == session
    assert api.base_url == "https://api.test.com"


@pytest.mark.asyncio
async def test_utf8_encoding_fallback(api_client, mock_session):
    """Test UTF-8 encoding fallback handling."""
    mock_response = AsyncMock()
    # Use ISO-8859-1 encoded data (common for Catalan)
    test_data = [{"nom": "Tarragona", "codi": "01"}]
    import json
    # Encode as ISO-8859-1
    raw_data = json.dumps(test_data, ensure_ascii=False).encode('iso-8859-1')
    
    mock_response.read = AsyncMock(return_value=raw_data)
    mock_response.raise_for_status = MagicMock()
    mock_response.status = 200
    
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await api_client.get_comarques()
    
    assert len(result) == 1
    assert result[0]["nom"] == "Tarragona"


@pytest.mark.asyncio
async def test_authentication_error_handling(api_client, mock_session):
    """Test authentication error handling."""
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock(side_effect=Exception("401"))
    mock_response.status = 401
    mock_response.headers = {}
    
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    from custom_components.meteocat_community_edition.api import MeteocatAuthError
    with pytest.raises(MeteocatAuthError, match="Authentication failed with status 401"):
        await api_client.get_comarques()


@pytest.mark.asyncio
async def test_find_municipality_for_station_by_coordinates(api_client, mock_session):
    """Test finding municipality for station by coordinates."""
    # Mock municipalities response
    mock_response = AsyncMock()
    municipalities_data = [
        {"codi": "080193", "nom": "Barcelona", "comarca": {"codi": "13"}},
        {"codi": "081017", "nom": "Hospitalet de Llobregat", "comarca": {"codi": "13"}}
    ]
    import json
    mock_response.read = AsyncMock(return_value=json.dumps(municipalities_data).encode('utf-8'))
    mock_response.raise_for_status = MagicMock()
    mock_response.status = 200
    
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    station = {
        "codi": "X1",
        "nom": "Barcelona - Centre",
        "coordenades": {"latitud": 41.385, "longitud": 2.173},
        "comarca": {"codi": "13"}
    }
    
    result = await api_client.find_municipality_for_station(station)
    
    # Should find Barcelona municipality by name matching
    assert result == "080193"
