"""Tests for Meteocat API client."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
async def test_get_uv_index(api_client, mock_session):
    """Test getting UV index forecast."""
    import json
    mock_response = AsyncMock()
    mock_data = {
        "ine": "081131",
        "nom": "Granollers",
        "comarca": 39,
        "capital": True,
        "uvi": [
            {
                "date": "2025-11-24",
                "hours": [
                    {"hour": 12, "uvi": 5, "uvi_clouds": 4},
                    {"hour": 13, "uvi": 6, "uvi_clouds": 5}
                ]
            }
        ]
    }
    mock_response.read = AsyncMock(return_value=json.dumps(mock_data).encode('utf-8'))
    mock_response.raise_for_status = MagicMock()
    mock_response.status = 200
    
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await api_client.get_uv_index("081131")
    
    assert "uvi" in result
    assert len(result["uvi"]) == 1
    assert result["uvi"][0]["date"] == "2025-11-24"
    assert len(result["uvi"][0]["hours"]) == 2

