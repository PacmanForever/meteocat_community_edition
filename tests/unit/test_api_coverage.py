"""Coverage tests for Meteocat API client."""
import sys
import os
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from aiohttp import ClientError, ClientSession

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from custom_components.meteocat_community_edition.api import (
    MeteocatAPI,
    MeteocatAPIError,
    MeteocatAuthError,
    MAX_RETRIES,
)
from custom_components.meteocat_community_edition.const import DEFAULT_API_BASE_URL

@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    return MagicMock(spec=ClientSession)

@pytest.fixture
def api_client(mock_session):
    """Create an API client."""
    return MeteocatAPI("test_key", mock_session)

@pytest.mark.asyncio
async def test_rate_limit_retry_success(api_client, mock_session):
    """Test 429 Rate Limit retry logic success."""
    # Setup response sequence: 429 -> 429 -> 200
    mock_response_429 = AsyncMock()
    mock_response_429.status = 429
    mock_response_429.headers = {"Retry-After": "1"}
    # Sync mock for raise_for_status
    mock_response_429.raise_for_status = MagicMock()
    
    mock_response_200 = AsyncMock()
    mock_response_200.status = 200
    mock_response_200.read.return_value = b'{"success": true}'
    mock_response_200.raise_for_status = MagicMock()
    
    # We use side_effect on the entering the context manager
    mock_session.request.return_value.__aenter__.side_effect = [
        mock_response_429,
        mock_response_429,
        mock_response_200
    ]
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await api_client._request("GET", "/test")
        
        assert result == {"success": True}
        assert mock_session.request.call_count == 3
        # Should sleep twice
        assert mock_sleep.call_count == 2

@pytest.mark.asyncio
async def test_rate_limit_max_retries_exceeded(api_client, mock_session):
    """Test 429 Rate Limit max retries exceeded."""
    mock_response_429 = AsyncMock()
    mock_response_429.status = 429
    mock_response_429.headers = {"Retry-After": "0"}
    mock_response_429.raise_for_status = MagicMock()
    
    mock_session.request.return_value.__aenter__.return_value = mock_response_429
    
    with patch("asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(MeteocatAPIError) as exc:
            await api_client._request("GET", "/test")
        
        assert "Rate limit exceeded" in str(exc.value)
        # 1 initial + MAX_RETRIES (3) = 4 calls total? 
        # The recursion logic: call 0 invokes call 1... call MAX invokes raise.
        # Let's count calls.
        assert mock_session.request.call_count == MAX_RETRIES + 1

@pytest.mark.asyncio
async def test_network_error_retry_success(api_client, mock_session):
    """Test network error retry success."""
    mock_response_200 = AsyncMock()
    mock_response_200.status = 200
    mock_response_200.read.return_value = b'{"success": true}'
    mock_response_200.raise_for_status = MagicMock()
    
    # Fail twice with ClientError, then success
    mock_session.request.side_effect = [
        ClientError("Net Error 1"),
        asyncio.TimeoutError("Timeout 1"),
        MagicMock(__aenter__=AsyncMock(return_value=mock_response_200)) # Context manager for success
    ]
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await api_client._request("GET", "/test")
        
        assert result == {"success": True}
        assert mock_session.request.call_count == 3
        assert mock_sleep.call_count == 2

@pytest.mark.asyncio
async def test_network_error_max_retries_exceeded(api_client, mock_session):
    """Test network error max retries exceeded."""
    mock_session.request.side_effect = ClientError("Persistent Net Error")
    
    with patch("asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(MeteocatAPIError) as exc:
            await api_client._request("GET", "/test")
        
        assert "Error connecting to Meteocat API" in str(exc.value)
        assert mock_session.request.call_count == MAX_RETRIES + 1

@pytest.mark.asyncio
async def test_encoding_fallback_replace(api_client, mock_session):
    """Test encoding fallback to 'replace' error handler."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.raise_for_status = MagicMock()
    
    # We test the ISO fallback which is guaranteed reachable.
    # \xf3 is valid ISO.
    mock_response.read.return_value = b'{"city": "Castell\xf3"}' 
    mock_session.request.return_value.__aenter__.return_value = mock_response

    result = await api_client._request("GET", "/test")
    assert result == {"city": "Castelló"}

@pytest.mark.asyncio
async def test_find_municipality_no_coordinates(api_client):
    """Test find_municipality returns None if station has no coordinates."""
    station = {"codi": "X1", "nom": "Station", "coordenades": {}}
    
    # Should log warning
    with patch("custom_components.meteocat_community_edition.api._LOGGER.warning") as mock_warn:
        # Mock get_municipalities to avoid network call
        api_client.get_municipalities = AsyncMock(return_value=[])
        
        result = await api_client.find_municipality_for_station(station)
        
        assert result is None
        mock_warn.assert_called()

@pytest.mark.asyncio
async def test_find_municipality_fallback_comarca(api_client):
    """Test finding municipality by comarca fallback when name doesn't match."""
    municipalities = [
        {"codi": "111", "nom": "Town A", "comarca": {"codi": "10"}},
        {"codi": "222", "nom": "Town B", "comarca": {"codi": "20"}}
    ]
    api_client.get_municipalities = AsyncMock(return_value=municipalities)
    
    station = {
        "codi": "X1", 
        "nom": "Station In Comarca 10", 
        "coordenades": {"latitud": 1, "longitud": 1},
        "comarca": {"codi": "10"}
    }
    
    result = await api_client.find_municipality_for_station(station)
    
    # Name "Town A" not in "Station In Comarca 10", so name match fails.
    # Fallback to comarca match -> Town A has comarca 10.
    assert result == "111"

@pytest.mark.asyncio
async def test_find_municipality_no_match(api_client):
    """Test finding municipality returns None when no match found."""
    municipalities = [
        {"codi": "111", "nom": "Town A", "comarca": {"codi": "99"}}
    ]
    api_client.get_municipalities = AsyncMock(return_value=municipalities)
    
    station = {
        "codi": "X1", 
        "nom": "Station Z", 
        "coordenades": {"latitud": 1, "longitud": 1},
        "comarca": {"codi": "55"}
    }
    
    with patch("custom_components.meteocat_community_edition.api._LOGGER.warning") as mock_warn:
        result = await api_client.find_municipality_for_station(station)
        assert result is None
        mock_warn.assert_called()

@pytest.mark.asyncio
async def test_find_municipality_exception_handling(api_client):
    """Test find municipality handles API errors gracefully."""
    api_client.get_municipalities = AsyncMock(side_effect=MeteocatAPIError("Fail"))
    
    with patch("custom_components.meteocat_community_edition.api._LOGGER.error") as mock_error:
        result = await api_client.find_municipality_for_station({})
        assert result is None
        mock_error.assert_called()

@pytest.mark.asyncio
async def test_auth_error_logging(api_client, mock_session):
    """Test that auth errors log detailed info."""
    mock_response = AsyncMock()
    mock_response.status = 403
    mock_response.raise_for_status = MagicMock() 
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    with patch("custom_components.meteocat_community_edition.api._LOGGER.error") as mock_error:
        with pytest.raises(MeteocatAuthError):
            await api_client._request("GET", "/test")
            
        mock_error.assert_called()
        
        args, _ = mock_error.call_args
        # Logger args matching logic:
        # msg = args[0]
        # args[1] = status
        # args[2] = endpoint
        # args[3] = len(api_key)
        # args[4] = url
        assert args[3] == len(api_client.api_key)
