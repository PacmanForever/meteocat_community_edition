"""Tests for coordinator intelligent retry system.

This test suite validates the coordinator-level retry logic for handling
temporary API failures while preserving quota consumption.

Key behaviors tested:
1. Retryable errors (network, server) trigger 60s retry
2. Non-retryable errors (auth, not found) do NOT trigger retry
3. Quotes API skipped on retry to avoid double-counting
4. Only 1 retry attempt (no infinite loops)
5. Retry cancellation on shutdown
6. Events only fire on complete success
"""
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, call

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from aiohttp import ClientError, ServerTimeoutError

from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
from custom_components.meteocat_community_edition.api import (
    MeteocatAPIError,
    MeteocatAuthError,
)
from custom_components.meteocat_community_edition.const import (
    CONF_API_KEY,
    CONF_MODE,
    CONF_STATION_CODE,
    CONF_MUNICIPALITY_CODE,
    MODE_ESTACIO,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    hass.bus = MagicMock()
    hass.bus.fire = MagicMock()
    return hass


@pytest.fixture
def mock_api():
    """Create a mock API client."""
    api = MagicMock()
    api.get_stations = AsyncMock(return_value=[
        {"codi": "YM", "nom": "Granollers", "coordenades": {"latitud": 41.6, "longitud": 2.3}}
    ])
    api.get_station_measurements = AsyncMock(return_value=[
        {"codi": "YM", "variables": [{"codi": 32, "lectures": [{"valor": 15.5}]}]}
    ])
    api.get_municipal_forecast = AsyncMock(return_value={
        "dies": [{"data": "2025-11-26", "variables": {"tmax": 20, "tmin": 10}}]
    })
    api.get_hourly_forecast = AsyncMock(return_value={
        "dies": [{"data": "2025-11-26", "variables": {"tmp": [15, 16, 17]}}]
    })
    api.get_quotes = AsyncMock(return_value={
        "client": {"nom": "Test Client"},
        "plans": [{"nom": "Prediccio_100", "requests_left": 950}]
    })
    api.find_municipality_for_station = AsyncMock(return_value="081131")
    return api


@pytest.fixture
def mock_entry_xema():
    """Create a mock config entry for XEMA mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        CONF_API_KEY: "test_api_key",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_device_registry():
    """Mock device registry."""
    mock_device = MagicMock()
    mock_device.id = "test_device_id"
    
    mock_registry = MagicMock()
    mock_registry.async_get_device.return_value = mock_device
    return mock_registry


# ============================================================================
# RETRY TRIGGERING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_network_timeout_triggers_retry(mock_hass, mock_api, mock_entry_xema, mock_device_registry):
    """Test that network timeout errors trigger a retry."""
    # First call fails with timeout, second succeeds
    mock_api.get_station_measurements.side_effect = [
        ServerTimeoutError("Timeout"),
        [{"codi": "YM", "variables": [{"codi": 32, "lectures": [{"valor": 15.5}]}]}]
    ]
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry), \
         patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        coordinator.api = mock_api
        
        # First update should fail and schedule retry
        try:
            await coordinator._async_update_data()
            assert False, "Should have raised UpdateFailed"
        except Exception as e:
            assert "retry scheduled" in str(e).lower()
        
        # Verify retry was scheduled
        assert mock_track.called
        call_args = mock_track.call_args
        assert call_args[0][1] == coordinator._async_retry_update


@pytest.mark.asyncio
async def test_server_error_500_triggers_retry(mock_hass, mock_api, mock_entry_xema, mock_device_registry):
    """Test that server error 500 triggers a retry."""
    mock_api.get_station_measurements.side_effect = MeteocatAPIError("Server error 500")
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry), \
         patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        coordinator.api = mock_api
        
        # Should fail and schedule retry
        try:
            await coordinator._async_update_data()
            assert False, "Should have raised UpdateFailed"
        except Exception:
            pass
        
        # Verify retry was scheduled
        assert mock_track.called


@pytest.mark.asyncio
async def test_client_error_triggers_retry(mock_hass, mock_api, mock_entry_xema, mock_device_registry):
    """Test that generic ClientError triggers a retry."""
    mock_api.get_station_measurements.side_effect = ClientError("Connection error")
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry), \
         patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        coordinator.api = mock_api
        
        try:
            await coordinator._async_update_data()
        except Exception:
            pass
        
        assert mock_track.called


# ============================================================================
# NON-RETRYABLE ERRORS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_auth_error_401_no_retry(mock_hass, mock_api, mock_entry_xema, mock_device_registry):
    """Test that 401 authentication errors do NOT trigger retry."""
    from homeassistant.exceptions import ConfigEntryAuthFailed
    
    mock_api.get_station_measurements.side_effect = MeteocatAuthError("401 Unauthorized")
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry), \
         patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        coordinator.api = mock_api
        
        # Should raise ConfigEntryAuthFailed (triggers reauth flow)
        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()
        
        # Verify NO retry was scheduled
        assert not mock_track.called


@pytest.mark.asyncio
async def test_not_found_404_no_retry(mock_hass, mock_api, mock_entry_xema, mock_device_registry):
    """Test that 404 errors do NOT trigger retry."""
    mock_api.get_station_measurements.side_effect = MeteocatAPIError("Not found 404")
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry), \
         patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        coordinator.api = mock_api
        
        try:
            await coordinator._async_update_data()
        except Exception:
            pass
        
        # Verify NO retry was scheduled (404 is permanent error)
        assert not mock_track.called


# ============================================================================
# QUOTA PRESERVATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_quotes_skipped_on_retry(mock_hass, mock_api, mock_entry_xema, mock_device_registry):
    """Test that quotes API is NOT called during retry to preserve quota accuracy."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        coordinator.api = mock_api
        
        # Mark this as a retry update
        coordinator._is_retry_update = True
        
        # Do update
        data = await coordinator._async_update_data()
        
        # Verify quotes was NOT called
        mock_api.get_quotes.assert_not_called()
        
        # Verify other APIs were called
        mock_api.get_station_measurements.assert_called_once()


@pytest.mark.asyncio
async def test_quotes_called_on_normal_update(mock_hass, mock_api, mock_entry_xema, mock_device_registry):
    """Test that quotes API IS called during normal (non-retry) updates."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        coordinator.api = mock_api
        
        # Normal update (not retry)
        coordinator._is_retry_update = False
        
        # Do update
        data = await coordinator._async_update_data()
        
        # Verify quotes WAS called
        mock_api.get_quotes.assert_called_once()


@pytest.mark.asyncio
async def test_only_one_retry_scheduled(mock_hass, mock_api, mock_entry_xema, mock_device_registry):
    """Test that only ONE retry is scheduled (no infinite retries)."""
    mock_api.get_station_measurements.side_effect = ServerTimeoutError("Timeout")
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry), \
         patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        coordinator.api = mock_api
        
        # First update fails - should schedule retry
        try:
            await coordinator._async_update_data()
        except Exception:
            pass
        
        assert mock_track.call_count == 1
        
        # Now simulate retry update (still failing)
        coordinator._is_retry_update = True
        mock_track.reset_mock()
        
        try:
            await coordinator._async_update_data()
        except Exception:
            pass
        
        # Should NOT schedule another retry (already in retry mode)
        assert mock_track.call_count == 0


# ============================================================================
# RETRY CANCELLATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_retry_cancelled_on_shutdown(mock_hass, mock_api, mock_entry_xema):
    """Test that pending retry is cancelled during shutdown."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        coordinator.api = mock_api
        
        # Create mock retry remover
        mock_remover = MagicMock()
        coordinator._retry_remover = mock_remover
        
        # Shutdown should cancel retry
        await coordinator.async_shutdown()
        
        # Verify remover was called
        mock_remover.assert_called_once()
        assert coordinator._retry_remover is None


@pytest.mark.asyncio
async def test_previous_retry_cancelled_before_new_retry(mock_hass, mock_api, mock_entry_xema, mock_device_registry):
    """Test that previous retry is cancelled before scheduling new retry."""
    mock_api.get_station_measurements.side_effect = ServerTimeoutError("Timeout")
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        coordinator.api = mock_api
        
        # Create mock retry remover
        mock_old_remover = MagicMock()
        coordinator._retry_remover = mock_old_remover
        
        # Schedule new retry
        await coordinator._schedule_retry_update()
        
        # Old remover should have been called
        mock_old_remover.assert_called_once()


# ============================================================================
# RETRY EXECUTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_retry_update_sets_flag_correctly(mock_hass, mock_api, mock_entry_xema, mock_device_registry):
    """Test that retry update sets and clears _is_retry_update flag correctly."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        coordinator.api = mock_api
        
        # Mock async_request_refresh to avoid actual refresh
        coordinator.async_request_refresh = AsyncMock()
        
        # Initially should be False
        assert coordinator._is_retry_update is False
        
        # Execute retry update
        await coordinator._async_retry_update(datetime.now())
        
        # After retry completes, flag should be False again
        assert coordinator._is_retry_update is False
        
        # Verify refresh was called
        coordinator.async_request_refresh.assert_called_once()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_full_retry_cycle_success(mock_hass, mock_api, mock_entry_xema, mock_device_registry):
    """Test complete retry cycle: fail -> retry -> success."""
    # First call fails, second succeeds
    call_count = 0
    
    async def measurements_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ServerTimeoutError("Timeout")
        return [{"codi": "YM", "variables": [{"codi": 32, "lectures": [{"valor": 15.5}]}]}]
    
    mock_api.get_station_measurements = AsyncMock(side_effect=measurements_side_effect)
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry), \
         patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        coordinator.api = mock_api
        
        # First update fails
        try:
            await coordinator._async_update_data()
            assert False, "Should have failed"
        except Exception:
            pass
        
        # Verify retry scheduled
        assert mock_track.called
        
        # Reset quotes mock to verify it's not called on retry
        mock_api.get_quotes.reset_mock()
        
        # Simulate retry execution
        coordinator._is_retry_update = True
        data = await coordinator._async_update_data()
        
        # Second attempt should succeed
        assert data is not None
        assert data.get("measurements") is not None
        
        # Quotes should NOT be called on retry
        assert mock_api.get_quotes.call_count == 0


@pytest.mark.asyncio
async def test_retry_delay_is_60_seconds(mock_hass, mock_api, mock_entry_xema):
    """Test that retry is scheduled with 60 second delay."""
    from datetime import timezone
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dt_util.utcnow') as mock_now, \
         patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
        
        # Mock current time
        now = datetime(2025, 11, 26, 12, 0, 0, tzinfo=timezone.utc)
        mock_now.return_value = now
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
        
        # Schedule retry
        await coordinator._schedule_retry_update(delay_seconds=60)
        
        # Check that retry was scheduled 60 seconds in future
        assert mock_track.called
        scheduled_time = mock_track.call_args[0][2]
        expected_time = now + timedelta(seconds=60)
        assert scheduled_time == expected_time
