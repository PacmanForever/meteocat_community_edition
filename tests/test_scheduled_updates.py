"""Tests for scheduled updates and API quota management."""
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, call

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
from custom_components.meteocat_community_edition.const import (
    CONF_API_KEY,
    CONF_MODE,
    CONF_STATION_CODE,
    CONF_MUNICIPALITY_CODE,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    MODE_ESTACIO,
    MODE_MUNICIPI,
    DEFAULT_UPDATE_TIME_1,
    DEFAULT_UPDATE_TIME_2,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    return hass


@pytest.fixture
def mock_api():
    """Create a mock API client."""
    api = MagicMock()
    api.get_stations = AsyncMock(return_value=[
        {"codi": "YM", "nom": "Granollers", "coordenades": {"latitud": 41.6, "longitud": 2.3}}
    ])
    api.get_station_measurements = AsyncMock(return_value=[
        {
            "codi": "YM",
            "variables": [
                {"codi": 32, "lectures": [{"valor": 15.5}]},
            ]
        }
    ])
    api.get_municipal_forecast = AsyncMock(return_value={
        "dies": [{"data": "2025-11-24", "variables": {}}]
    })
    api.get_hourly_forecast = AsyncMock(return_value={
        "dies": [{"data": "2025-11-24", "variables": {}}]
    })
    api.get_uv_index = AsyncMock(return_value={
        "ine": "081131",
        "nom": "Granollers",
        "uvi": []
    })
    api.get_quotes = AsyncMock(return_value={
        "client": {"nom": "Test"},
        "plans": [{"nom": "Predicció", "consultesRestants": 950, "maxConsultes": 1000}]
    })
    api.find_municipality_for_station = AsyncMock(return_value="081131")
    return api


@pytest.fixture
def mock_entry_estacio():
    """Create a mock config entry for MODE_ESTACIO."""
    entry = MagicMock()
    entry.data = {
        CONF_API_KEY: "test_api_key_123456789",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
        CONF_UPDATE_TIME_1: "06:00",
        CONF_UPDATE_TIME_2: "14:00",
    }
    entry.options = {}
    entry.entry_id = "test_entry_estacio"
    return entry


@pytest.fixture
def mock_entry_municipi():
    """Create a mock config entry for MODE_MUNICIPI."""
    entry = MagicMock()
    entry.data = {
        CONF_API_KEY: "test_api_key_123456789",
        CONF_MODE: MODE_MUNICIPI,
        CONF_MUNICIPALITY_CODE: "081131",
        CONF_UPDATE_TIME_1: "06:00",
        CONF_UPDATE_TIME_2: "14:00",
    }
    entry.options = {}
    entry.entry_id = "test_entry_municipi"
    return entry


@pytest.mark.asyncio
async def test_no_automatic_polling(mock_hass, mock_entry_estacio, mock_api):
    """Test that automatic polling is disabled (update_interval is None)."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Verify update_interval is None (no automatic polling)
        assert coordinator.update_interval is None
        
        # Verify update times are configured
        assert coordinator.update_time_1 == "06:00"
        assert coordinator.update_time_2 == "14:00"


@pytest.mark.asyncio
async def test_schedule_next_update_is_called(mock_hass, mock_entry_estacio, mock_api):
    """Test that _schedule_next_update is called to schedule updates."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Mock the scheduler
        with patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
            coordinator._schedule_next_update()
            
            # Verify that async_track_point_in_utc_time was called
            assert mock_track.called
            assert mock_track.call_count == 1
            
            # Verify callback was registered
            call_args = mock_track.call_args
            assert call_args[0][0] == mock_hass  # hass
            assert callable(call_args[0][1])  # callback
            # call_args[0][2] is the scheduled time (datetime)


@pytest.mark.asyncio
async def test_cleanup_cancels_scheduled_update(mock_hass, mock_entry_estacio, mock_api):
    """Test that async_shutdown cancels scheduled updates."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Mock remover
        mock_remover = MagicMock()
        coordinator._scheduled_update_remover = mock_remover
        
        # Call shutdown
        await coordinator.async_shutdown()
        
        # Verify remover was called
        assert mock_remover.called
        assert coordinator._scheduled_update_remover is None


@pytest.mark.asyncio
async def test_api_calls_estacio_mode(mock_hass, mock_entry_estacio, mock_api):
    """Test API calls in ESTACIO mode to verify quota usage."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Perform first update
        await coordinator._async_update_data()
        
        # Verify API calls for ESTACIO mode (first time)
        # Should call: get_stations (once), get_station_measurements, get_municipal_forecast, 
        # get_hourly_forecast, get_uv_index, get_quotes
        assert mock_api.get_stations.call_count == 1
        assert mock_api.get_station_measurements.call_count == 1
        assert mock_api.get_municipal_forecast.call_count == 1
        assert mock_api.get_hourly_forecast.call_count == 1
        assert mock_api.get_uv_index.call_count == 1
        assert mock_api.get_quotes.call_count == 1
        
        # Total: 6 API calls on first update
        total_calls = (
            mock_api.get_stations.call_count +
            mock_api.get_station_measurements.call_count +
            mock_api.get_municipal_forecast.call_count +
            mock_api.get_hourly_forecast.call_count +
            mock_api.get_uv_index.call_count +
            mock_api.get_quotes.call_count
        )
        assert total_calls == 6
        
        # Second update (get_stations should not be called again)
        await coordinator._async_update_data()
        
        # get_stations should still be 1 (not called again)
        assert mock_api.get_stations.call_count == 1
        # Other calls should be 2 each
        assert mock_api.get_station_measurements.call_count == 2
        assert mock_api.get_municipal_forecast.call_count == 2
        assert mock_api.get_hourly_forecast.call_count == 2
        assert mock_api.get_uv_index.call_count == 2
        assert mock_api.get_quotes.call_count == 2
        
        # Total after 2 updates: 6 (first) + 5 (second) = 11 calls
        total_calls_after_second = (
            mock_api.get_stations.call_count +
            mock_api.get_station_measurements.call_count +
            mock_api.get_municipal_forecast.call_count +
            mock_api.get_hourly_forecast.call_count +
            mock_api.get_uv_index.call_count +
            mock_api.get_quotes.call_count
        )
        assert total_calls_after_second == 11


@pytest.mark.asyncio
async def test_api_calls_municipi_mode(mock_hass, mock_entry_municipi, mock_api):
    """Test API calls in MUNICIPI mode to verify quota usage."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_municipi)
        coordinator.api = mock_api
        
        # Perform update
        await coordinator._async_update_data()
        
        # Verify API calls for MUNICIPI mode
        # Should NOT call: get_stations, get_station_measurements
        assert mock_api.get_stations.call_count == 0
        assert mock_api.get_station_measurements.call_count == 0
        
        # Should call: get_municipal_forecast, get_hourly_forecast, get_uv_index, get_quotes
        assert mock_api.get_municipal_forecast.call_count == 1
        assert mock_api.get_hourly_forecast.call_count == 1
        assert mock_api.get_uv_index.call_count == 1
        assert mock_api.get_quotes.call_count == 1
        
        # Total: 4 API calls per update in MUNICIPI mode
        total_calls = (
            mock_api.get_municipal_forecast.call_count +
            mock_api.get_hourly_forecast.call_count +
            mock_api.get_uv_index.call_count +
            mock_api.get_quotes.call_count
        )
        assert total_calls == 4


@pytest.mark.asyncio
async def test_daily_quota_usage_estacio():
    """Test that daily quota usage is reasonable for ESTACIO mode.
    
    Expected usage with default times (06:00, 14:00):
    - First update (initial setup): 6 calls
    - Update at 06:00: 5 calls
    - Update at 14:00: 5 calls
    - Manual updates: variable
    
    Minimum daily usage: 6 + 5 + 5 = 16 calls (if no manual updates)
    """
    # This is a documentation test - just verify the calculation
    first_update_calls = 6  # get_stations + measurements + forecast + hourly + uv + quotes
    scheduled_update_calls = 5  # measurements + forecast + hourly + uv + quotes (no get_stations)
    
    daily_scheduled_updates = 2  # 06:00 and 14:00
    
    minimum_daily_calls = first_update_calls + (scheduled_update_calls * daily_scheduled_updates)
    
    # Should be 6 + (5 * 2) = 16 calls per day minimum
    assert minimum_daily_calls == 16
    
    # With 1000 quota per month (typical Predicció plan)
    # 16 calls/day * 30 days = 480 calls/month
    # This leaves 520 calls for manual updates (~ 17 manual updates/day)
    monthly_quota = 1000
    days_per_month = 30
    monthly_scheduled_calls = minimum_daily_calls * days_per_month
    remaining_quota = monthly_quota - monthly_scheduled_calls
    
    assert monthly_scheduled_calls == 480
    assert remaining_quota == 520


@pytest.mark.asyncio
async def test_daily_quota_usage_municipi():
    """Test that daily quota usage is reasonable for MUNICIPI mode.
    
    Expected usage with default times (06:00, 14:00):
    - Each update: 4 calls (forecast + hourly + uv + quotes)
    - 2 updates per day = 8 calls/day
    """
    calls_per_update = 4  # forecast + hourly + uv + quotes
    daily_scheduled_updates = 2  # 06:00 and 14:00
    
    minimum_daily_calls = calls_per_update * daily_scheduled_updates
    
    # Should be 4 * 2 = 8 calls per day
    assert minimum_daily_calls == 8
    
    # With 1000 quota per month
    # 8 calls/day * 30 days = 240 calls/month
    # This leaves 760 calls for manual updates (~ 25 manual updates/day)
    monthly_quota = 1000
    days_per_month = 30
    monthly_scheduled_calls = minimum_daily_calls * days_per_month
    remaining_quota = monthly_quota - monthly_scheduled_calls
    
    assert monthly_scheduled_calls == 240
    assert remaining_quota == 760


@pytest.mark.asyncio
async def test_scheduled_update_reschedules_itself(mock_hass, mock_entry_estacio, mock_api):
    """Test that scheduled update reschedules itself after execution."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Mock the scheduler and request_refresh
        with patch.object(coordinator, '_schedule_next_update') as mock_schedule, \
             patch.object(coordinator, 'async_request_refresh', new_callable=AsyncMock) as mock_refresh:
            
            # Call the scheduled update callback
            now = datetime.now()
            await coordinator._async_scheduled_update(now)
            
            # Verify refresh was called
            assert mock_refresh.called
            
            # Verify it rescheduled itself
            assert mock_schedule.called


@pytest.mark.asyncio
async def test_quotes_fetched_after_other_api_calls(mock_hass, mock_entry_estacio, mock_api):
    """Test that quotes are fetched AFTER other API calls to get accurate consumption."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Track call order
        call_order = []
        
        def track_call(name):
            def wrapper(*args, **kwargs):
                call_order.append(name)
                # Return the original mock's return value
                return getattr(mock_api, name).return_value
            return wrapper
        
        # Wrap each API call
        mock_api.get_stations.side_effect = track_call('get_stations')
        mock_api.get_station_measurements.side_effect = track_call('get_station_measurements')
        mock_api.get_municipal_forecast.side_effect = track_call('get_municipal_forecast')
        mock_api.get_hourly_forecast.side_effect = track_call('get_hourly_forecast')
        mock_api.get_uv_index.side_effect = track_call('get_uv_index')
        mock_api.get_quotes.side_effect = track_call('get_quotes')
        
        # Perform update
        await coordinator._async_update_data()
        
        # Verify get_quotes is called LAST
        assert 'get_quotes' in call_order
        assert call_order.index('get_quotes') == len(call_order) - 1
        
        # Verify other calls happened before get_quotes
        quotes_index = call_order.index('get_quotes')
        for call_name in ['get_station_measurements', 'get_municipal_forecast', 
                          'get_hourly_forecast', 'get_uv_index']:
            if call_name in call_order:
                assert call_order.index(call_name) < quotes_index
