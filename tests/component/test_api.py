"""Test Meteocat API class."""
from unittest.mock import MagicMock, patch
import pytest
from aiohttp import ClientSession
from freezegun import freeze_time
from datetime import datetime

from custom_components.meteocat_community_edition.api import MeteocatAPI, MeteocatAPIError
from custom_components.meteocat_community_edition.const import (
    ENDPOINT_XEMA_STATIONS,
    ENDPOINT_MUNICIPALITIES,
)

@pytest.mark.asyncio
async def test_get_stations_by_comarca():
    """Test getting stations filtered by comarca."""
    session = MagicMock(spec=ClientSession)
    api = MeteocatAPI("test_key", session)
    
    mock_stations = [
        {"codi": "S1", "comarca": {"codi": "C1"}},
        {"codi": "S2", "comarca": {"codi": "C2"}},
        {"codi": "S3", "comarca": {"codi": "C1"}},
    ]
    
    with patch.object(api, "get_stations", return_value=mock_stations):
        result = await api.get_stations_by_comarca("C1")
        assert len(result) == 2
        assert result[0]["codi"] == "S1"
        assert result[1]["codi"] == "S3"

@pytest.mark.asyncio
async def test_find_municipality_for_station_match_name():
    """Test finding municipality for station by name matching."""
    session = MagicMock(spec=ClientSession)
    api = MeteocatAPI("test_key", session)
    
    station = {
        "codi": "S1",
        "nom": "Station of Barcelona",
        "coordenades": {"latitud": 41.0, "longitud": 2.0},
        "comarca": {"codi": "C1"}
    }
    
    mock_municipalities = [
        {"codi": "M1", "nom": "Girona", "comarca": {"codi": "C2"}},
        {"codi": "M2", "nom": "Barcelona", "comarca": {"codi": "C1"}},
    ]
    
    with patch.object(api, "get_municipalities", return_value=mock_municipalities):
        result = await api.find_municipality_for_station(station)
        assert result == "M2"

@pytest.mark.asyncio
async def test_find_municipality_for_station_fallback_comarca():
    """Test finding municipality for station falling back to comarca."""
    session = MagicMock(spec=ClientSession)
    api = MeteocatAPI("test_key", session)
    
    station = {
        "codi": "S1",
        "nom": "Remote Station",
        "coordenades": {"latitud": 41.0, "longitud": 2.0},
        "comarca": {"codi": "C1"}
    }
    
    mock_municipalities = [
        {"codi": "M1", "nom": "City1", "comarca": {"codi": "C2"}},
        {"codi": "M2", "nom": "City2", "comarca": {"codi": "C1"}},
    ]
    
    with patch.object(api, "get_municipalities", return_value=mock_municipalities):
        result = await api.find_municipality_for_station(station)
        assert result == "M2"

@pytest.mark.asyncio
async def test_find_municipality_for_station_no_match():
    """Test finding municipality for station with no match."""
    session = MagicMock(spec=ClientSession)
    api = MeteocatAPI("test_key", session)
    
    station = {
        "codi": "S1",
        "nom": "Remote Station",
        "coordenades": {"latitud": 41.0, "longitud": 2.0},
        "comarca": {"codi": "C99"}
    }
    
    mock_municipalities = [
        {"codi": "M1", "nom": "City1", "comarca": {"codi": "C2"}},
    ]
    
    with patch.object(api, "get_municipalities", return_value=mock_municipalities):
        result = await api.find_municipality_for_station(station)
        assert result is None

@pytest.mark.asyncio
async def test_find_municipality_for_station_no_coords():
    """Test finding municipality for station without coordinates."""
    session = MagicMock(spec=ClientSession)
    api = MeteocatAPI("test_key", session)
    
    station = {
        "codi": "S1",
        "nom": "Station",
        # No coordenades
    }
    
    with patch.object(api, "get_municipalities", return_value=[]):
        result = await api.find_municipality_for_station(station)
        assert result is None

@pytest.mark.asyncio
async def test_find_municipality_for_station_error():
    """Test error handling in find_municipality_for_station."""
    session = MagicMock(spec=ClientSession)
    api = MeteocatAPI("test_key", session)
    
    station = {"codi": "S1"}
    
    with patch.object(api, "get_municipalities", side_effect=MeteocatAPIError("Boom")):
        result = await api.find_municipality_for_station(station)
        assert result is None

@pytest.mark.asyncio
async def test_get_station_measurements():
    """Test getting station measurements constructs correct URL."""
    session = MagicMock(spec=ClientSession)
    api = MeteocatAPI("test_key", session)
    
    with freeze_time("2023-10-15 12:00:00"):
        with patch.object(api, "_request") as mock_request:
            await api.get_station_measurements("S1")
            
            mock_request.assert_called_once()
            args = mock_request.call_args
            assert args[0][0] == "GET"
            assert "xema/v1/estacions/mesurades/S1/2023/10/15" in args[0][1]

@pytest.mark.asyncio
async def test_request_decoding_utf8():
    """Test response decoding with valid UTF-8."""
    session = MagicMock(spec=ClientSession)
    api = MeteocatAPI("test_key", session)
    
    msg = "Acció".encode("utf-8")
    
    mock_response = MagicMock()
    # read() is awaited, so it must return an awaitable
    async def mock_read():
        return msg
    mock_response.read = mock_read
    mock_response.status = 200
    mock_response.raise_for_status = MagicMock()
    
    mock_request_ctx = MagicMock()
    mock_request_ctx.__aenter__.return_value = mock_response
    mock_request_ctx.__aexit__.return_value = None
    
    session.request.return_value = mock_request_ctx
    
    with patch("json.loads", return_value={"test": "ok"}):
        await api._request("GET", "test")

@pytest.mark.asyncio
async def test_request_decoding_latin1():
    """Test response decoding with Latin-1 fallback."""
    session = MagicMock(spec=ClientSession)
    api = MeteocatAPI("test_key", session)
    
    # "Acció" in latin-1 is b'Acci\xf3'
    # \xf3 is invalid in UTF-8 start byte
    msg = b"Acci\xf3"
    
    mock_response = MagicMock()
    async def mock_read():
        return msg
    mock_response.read = mock_read
    mock_response.status = 200
    mock_response.raise_for_status = MagicMock()

    mock_request_ctx = MagicMock()
    mock_request_ctx.__aenter__.return_value = mock_response
    mock_request_ctx.__aexit__.return_value = None
    
    session.request.return_value = mock_request_ctx
    
    with patch("json.loads") as mock_json_loads:
        await api._request("GET", "test")
        
        # Verify it decoded correctly
        mock_json_loads.assert_called_with("Acció")

@pytest.mark.asyncio
async def test_request_decoding_fallback_replace():
    """Test response decoding fallback to replace."""
    session = MagicMock(spec=ClientSession)
    api = MeteocatAPI("test_key", session)
    
    # We mock raw_data to control decode behavior
    mock_raw_data = MagicMock()
    
    def decode_side_effect(encoding, errors=None):
        if encoding == 'utf-8' and errors != 'replace':
            raise UnicodeDecodeError('utf-8', b'', 0, 1, 'bad')
        if encoding == 'iso-8859-1':
            raise UnicodeDecodeError('iso-8859-1', b'', 0, 1, 'bad')
        return "REPLACED_CONTENT"
        
    mock_raw_data.decode.side_effect = decode_side_effect
    
    mock_response = MagicMock()
    async def mock_read():
        return mock_raw_data
    mock_response.read = mock_read
    mock_response.status = 200
    mock_response.raise_for_status = MagicMock()
    
    mock_request_ctx = MagicMock()
    mock_request_ctx.__aenter__.return_value = mock_response
    mock_request_ctx.__aexit__.return_value = None
    
    session.request.return_value = mock_request_ctx
    
    with patch("json.loads") as mock_json_loads:
        await api._request("GET", "test")
        
        args = mock_json_loads.call_args[0]
        assert "REPLACED_CONTENT" in args[0]
