"""Tests for retry logic and error handling."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.meteocat_community_edition.api import (
    MeteocatAPI,
    MeteocatAPIError,
    MeteocatAuthError,
)


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    return AsyncMock(spec=aiohttp.ClientSession)


@pytest.fixture
def api_client(mock_session):
    """Create API client with mock session."""
    return MeteocatAPI("test_api_key", mock_session)


@pytest.mark.asyncio
async def test_auth_error_401_no_retry(api_client, mock_session):
    """Test that 401 errors raise MeteocatAuthError without retry."""
    mock_response = AsyncMock()
    mock_response.status = 401
    mock_response.headers = {}
    mock_response.raise_for_status = MagicMock(side_effect=aiohttp.ClientResponseError(
        request_info=MagicMock(),
        history=(),
        status=401
    ))
    mock_session.request.return_value.__aenter__.return_value = mock_response

    with pytest.raises(MeteocatAuthError) as exc_info:
        await api_client._request("GET", "/test")
    
    assert "Authentication failed with status 401" in str(exc_info.value)
    # Should only attempt once (no retries for auth errors)
    assert mock_session.request.call_count == 1


@pytest.mark.asyncio
async def test_auth_error_403_no_retry(api_client, mock_session):
    """Test that 403 errors raise MeteocatAuthError without retry."""
    mock_response = AsyncMock()
    mock_response.status = 403
    mock_response.headers = {}
    mock_response.raise_for_status = MagicMock(side_effect=aiohttp.ClientResponseError(
        request_info=MagicMock(),
        history=(),
        status=403
    ))
    mock_session.request.return_value.__aenter__.return_value = mock_response

    with pytest.raises(MeteocatAuthError) as exc_info:
        await api_client._request("GET", "/test")
    
    assert "Authentication failed with status 403" in str(exc_info.value)
    assert mock_session.request.call_count == 1


@pytest.mark.asyncio
async def test_rate_limit_retry_with_backoff(api_client, mock_session):
    """Test that 429 errors are retried with exponential backoff."""
    # First two calls return 429, third succeeds
    mock_response_429 = AsyncMock()
    mock_response_429.status = 429
    mock_response_429.headers = {"Retry-After": "1"}
    mock_response_429.raise_for_status = MagicMock(side_effect=aiohttp.ClientResponseError(
        request_info=MagicMock(),
        history=(),
        status=429
    ))
    
    mock_response_200 = AsyncMock()
    mock_response_200.status = 200
    mock_response_200.read = AsyncMock(return_value=b'{"result": "success"}')
    mock_response_200.raise_for_status = MagicMock()
    
    mock_session.request.return_value.__aenter__.side_effect = [
        mock_response_429,
        mock_response_429,
        mock_response_200,
    ]

    with patch("asyncio.sleep") as mock_sleep:
        result = await api_client._request("GET", "/test")
    
    assert result == {"result": "success"}
    assert mock_session.request.call_count == 3
    # Should have slept twice (after first two 429 responses)
    assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_rate_limit_max_retries_exceeded(api_client, mock_session):
    """Test that rate limiting fails after max retries."""
    mock_response = AsyncMock()
    mock_response.status = 429
    mock_response.headers = {"Retry-After": "1"}
    mock_response.raise_for_status = MagicMock(side_effect=aiohttp.ClientResponseError(
        request_info=MagicMock(),
        history=(),
        status=429
    ))
    mock_session.request.return_value.__aenter__.return_value = mock_response

    with patch("asyncio.sleep"):
        with pytest.raises(MeteocatAPIError) as exc_info:
            await api_client._request("GET", "/test")
    
    assert "Rate limit exceeded" in str(exc_info.value)
    # Should attempt MAX_RETRIES + 1 times (initial + 3 retries)
    assert mock_session.request.call_count == 4


@pytest.mark.asyncio
async def test_network_error_retry_with_exponential_backoff(api_client, mock_session):
    """Test that network errors are retried with exponential backoff."""
    # First two calls fail with network error, third succeeds
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b'{"result": "success"}')
    mock_response.raise_for_status = MagicMock()
    
    mock_session.request.return_value.__aenter__.side_effect = [
        aiohttp.ClientError("Connection error"),
        aiohttp.ClientError("Connection error"),
        mock_response,
    ]

    with patch("asyncio.sleep") as mock_sleep:
        result = await api_client._request("GET", "/test")
    
    assert result == {"result": "success"}
    assert mock_session.request.call_count == 3
    # Should sleep with exponential backoff: 1s, 2s
    assert mock_sleep.call_count == 2
    mock_sleep.assert_any_call(1)  # 2^0
    mock_sleep.assert_any_call(2)  # 2^1


@pytest.mark.asyncio
async def test_timeout_error_retry(api_client, mock_session):
    """Test that timeout errors are retried."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b'{"result": "success"}')
    mock_response.raise_for_status = MagicMock()
    
    mock_session.request.return_value.__aenter__.side_effect = [
        asyncio.TimeoutError(),
        mock_response,
    ]

    with patch("asyncio.sleep"):
        result = await api_client._request("GET", "/test")
    
    assert result == {"result": "success"}
    assert mock_session.request.call_count == 2


@pytest.mark.asyncio
async def test_network_error_max_retries_exceeded(api_client, mock_session):
    """Test that network errors fail after max retries."""
    mock_session.request.return_value.__aenter__.side_effect = aiohttp.ClientError("Persistent error")

    with patch("asyncio.sleep"):
        with pytest.raises(MeteocatAPIError) as exc_info:
            await api_client._request("GET", "/test")
    
    assert "Error connecting to Meteocat API" in str(exc_info.value)
    assert mock_session.request.call_count == 4  # Initial + 3 retries


@pytest.mark.asyncio
async def test_successful_request_no_retry(api_client, mock_session):
    """Test that successful requests don't retry."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b'{"data": "test"}')
    mock_response.raise_for_status = MagicMock()
    mock_session.request.return_value.__aenter__.return_value = mock_response

    result = await api_client._request("GET", "/test")
    
    assert result == {"data": "test"}
    assert mock_session.request.call_count == 1
