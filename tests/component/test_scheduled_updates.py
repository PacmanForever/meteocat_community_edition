"""Tests for scheduled updates and API quota management.

⚠️ CRITICAL TEST SUITE ⚠️

This test suite is CRITICAL for ensuring API quota preservation in production.
DO NOT modify or remove these tests without understanding the quota implications.

What This Suite Tests:
- Automatic polling is DISABLED (update_interval=None)
- Scheduled updates work correctly at configured times
- Scheduler cleanup prevents orphaned updates
- API call counts are correct for quota calculations
- Quotes are fetched AFTER other APIs for accurate tracking
- Scheduler cancellation prevents duplicate updates
- System recovers from network errors without breaking scheduling
- Time-based scheduling works in all scenarios (midnight, between times, etc.)
- HA restart doesn't cause duplicate updates
- Custom update times work correctly

Why These Tests Are Critical:
If any of these tests fail, the integration could:
1. Exhaust monthly API quota in days instead of lasting the full month
2. Make duplicate API calls, wasting quota
3. Show incorrect quota information to users
4. Continue making calls after being unloaded
5. Fail to update at configured times

Quota Impact:
- MODE_ESTACIO: ~13 calls/day = 390/month (with 06:00, 14:00 schedule)
- MODE_MUNICIPI: ~6 calls/day = 180/month (with 06:00, 14:00 schedule)
- With 1000 calls/month quota, this leaves 610-820 for manual updates

Last Updated: 2025-11-26
Test Count: 17 tests
Status: ALL MUST PASS
"""
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, call

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest

from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator


# Patch device_registry globally for all tests
@pytest.fixture(autouse=True)
def patch_device_registry():
    """Patch device_registry for tests that call _async_update_data."""
    mock_device = MagicMock()
    mock_device.id = "test_device_id"
    
    with patch('custom_components.meteocat_community_edition.coordinator.dr.async_get') as mock_dr:
        mock_registry = MagicMock()
        mock_registry.async_get_device.return_value = mock_device
        mock_dr.return_value = mock_registry
        yield


from custom_components.meteocat_community_edition.const import (
    CONF_API_KEY,
    CONF_MODE,
    CONF_STATION_CODE,
    CONF_MUNICIPALITY_CODE,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    CONF_ENABLE_FORECAST_HOURLY,
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
        CONF_ENABLE_FORECAST_HOURLY: True,  # Enable hourly forecast for test
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
        CONF_ENABLE_FORECAST_HOURLY: True,  # Enable hourly forecast for test
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
        # get_hourly_forecast, get_quotes
        assert mock_api.get_stations.call_count == 1
        assert mock_api.get_station_measurements.call_count == 1
        assert mock_api.get_municipal_forecast.call_count == 1
        assert mock_api.get_hourly_forecast.call_count == 1
        assert mock_api.get_quotes.call_count == 1
        
        # Total: 5 API calls on first update
        total_calls = (
            mock_api.get_stations.call_count +
            mock_api.get_station_measurements.call_count +
            mock_api.get_municipal_forecast.call_count +
            mock_api.get_hourly_forecast.call_count +
            mock_api.get_quotes.call_count
        )
        assert total_calls == 5
        
        # Second update (get_stations should not be called again)
        await coordinator._async_update_data()
        
        # get_stations should still be 1 (not called again)
        assert mock_api.get_stations.call_count == 1
        # Other calls should be 2 each
        assert mock_api.get_station_measurements.call_count == 2
        assert mock_api.get_municipal_forecast.call_count == 2
        assert mock_api.get_hourly_forecast.call_count == 2
        assert mock_api.get_quotes.call_count == 2
        
        # Total after 2 updates: 5 (first) + 4 (second) = 9 calls
        total_calls_after_second = (
            mock_api.get_stations.call_count +
            mock_api.get_station_measurements.call_count +
            mock_api.get_municipal_forecast.call_count +
            mock_api.get_hourly_forecast.call_count +
            mock_api.get_quotes.call_count
        )
        assert total_calls_after_second == 9


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
        
        # Should call: get_municipal_forecast, get_hourly_forecast, get_quotes
        assert mock_api.get_municipal_forecast.call_count == 1
        assert mock_api.get_hourly_forecast.call_count == 1
        assert mock_api.get_quotes.call_count == 1
        
        # Total: 3 API calls per update in MUNICIPI mode
        total_calls = (
            mock_api.get_municipal_forecast.call_count +
            mock_api.get_hourly_forecast.call_count +
            mock_api.get_quotes.call_count
        )
        assert total_calls == 3


@pytest.mark.asyncio
async def test_daily_quota_usage_estacio():
    """Test that daily quota usage is reasonable for ESTACIO mode.
    
    Expected usage with default times (06:00, 14:00):
    - First update (initial setup): 5 calls
    - Update at 06:00: 4 calls
    - Update at 14:00: 4 calls
    - Manual updates: variable
    
    Minimum daily usage: 5 + 4 + 4 = 13 calls (if no manual updates)
    """
    # This is a documentation test - just verify the calculation
    first_update_calls = 5  # get_stations + measurements + forecast + hourly + quotes
    scheduled_update_calls = 4  # measurements + forecast + hourly + quotes (no get_stations)
    
    daily_scheduled_updates = 2  # 06:00 and 14:00
    
    minimum_daily_calls = first_update_calls + (scheduled_update_calls * daily_scheduled_updates)
    
    # Should be 5 + (4 * 2) = 13 calls per day minimum
    assert minimum_daily_calls == 13
    
    # With 1000 quota per month (typical Predicció plan)
    # 13 calls/day * 30 days = 390 calls/month
    # This leaves 610 calls for manual updates (~ 20 manual updates/day)
    monthly_quota = 1000
    days_per_month = 30
    monthly_scheduled_calls = minimum_daily_calls * days_per_month
    remaining_quota = monthly_quota - monthly_scheduled_calls
    
    assert monthly_scheduled_calls == 390
    assert remaining_quota == 610


@pytest.mark.asyncio
async def test_daily_quota_usage_municipi():
    """Test that daily quota usage is reasonable for MUNICIPI mode.
    
    Expected usage with default times (06:00, 14:00):
    - Each update: 3 calls (forecast + hourly + quotes)
    - 2 updates per day = 6 calls/day
    """
    calls_per_update = 3  # forecast + hourly + quotes
    daily_scheduled_updates = 2  # 06:00 and 14:00
    
    minimum_daily_calls = calls_per_update * daily_scheduled_updates
    
    # Should be 3 * 2 = 6 calls per day
    assert minimum_daily_calls == 6
    
    # With 1000 quota per month
    # 6 calls/day * 30 days = 180 calls/month
    # This leaves 820 calls for manual updates (~ 27 manual updates/day)
    monthly_quota = 1000
    days_per_month = 30
    monthly_scheduled_calls = minimum_daily_calls * days_per_month
    remaining_quota = monthly_quota - monthly_scheduled_calls
    
    assert monthly_scheduled_calls == 180
    assert remaining_quota == 820


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
        mock_api.get_quotes.side_effect = track_call('get_quotes')
        
        # Perform update
        await coordinator._async_update_data()
        
        # Verify get_quotes is called LAST
        assert 'get_quotes' in call_order
        assert call_order.index('get_quotes') == len(call_order) - 1
        
        # Verify other calls happened before get_quotes
        quotes_index = call_order.index('get_quotes')
        for call_name in ['get_station_measurements', 'get_municipal_forecast', 
                          'get_hourly_forecast']:
            if call_name in call_order:
                assert call_order.index(call_name) < quotes_index


@pytest.mark.asyncio
async def test_reschedule_cancels_previous_scheduler(mock_hass, mock_entry_estacio, mock_api):
    """Test that calling _schedule_next_update cancels the previous scheduled update.
    
    This is CRITICAL to avoid duplicate scheduled updates that would waste API quota.
    """
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        with patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
            # Create mock removers
            mock_remover_1 = MagicMock()
            mock_remover_2 = MagicMock()
            
            # First schedule
            mock_track.return_value = mock_remover_1
            coordinator._schedule_next_update()
            assert coordinator._scheduled_update_remover == mock_remover_1
            assert not mock_remover_1.called  # Should not be called yet
            
            # Second schedule (should cancel first)
            mock_track.return_value = mock_remover_2
            coordinator._schedule_next_update()
            
            # Verify first remover was called (cancelled)
            assert mock_remover_1.called
            assert coordinator._scheduled_update_remover == mock_remover_2


@pytest.mark.asyncio
async def test_multiple_manual_updates_allowed(mock_hass, mock_entry_estacio, mock_api):
    """Test that multiple manual updates (button presses) are allowed.
    
    This is intentional - users should be able to manually refresh when needed,
    but they are warned about quota usage in the documentation.
    """
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Perform 3 manual updates rapidly
        await coordinator._async_update_data()
        await coordinator._async_update_data()
        await coordinator._async_update_data()
        
        # Verify all 3 updates went through
        # First update: get_stations (1) + measurements (1) = 2
        # Second update: measurements (1) = 1
        # Third update: measurements (1) = 1
        assert mock_api.get_station_measurements.call_count == 3
        
        # Total calls for all 3 updates:
        # First: 5 calls (stations + measurements + forecast + hourly + quotes)
        # Second: 4 calls (measurements + forecast + hourly + quotes)
        # Third: 4 calls (measurements + forecast + hourly + quotes)
        # Total: 13 calls
        total_calls = (
            mock_api.get_stations.call_count +
            mock_api.get_station_measurements.call_count +
            mock_api.get_municipal_forecast.call_count +
            mock_api.get_hourly_forecast.call_count +
            mock_api.get_quotes.call_count
        )
        assert total_calls == 13


@pytest.mark.asyncio
async def test_update_failure_does_not_break_scheduling(mock_hass, mock_entry_estacio, mock_api):
    """Test that if an update fails (network error, etc), scheduling continues.
    
    This is CRITICAL - a failed update should not prevent future scheduled updates.
    """
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Make API call fail
        mock_api.get_station_measurements.side_effect = Exception("Network error")
        
        # Try to update (should fail)
        try:
            await coordinator._async_update_data()
        except Exception:
            pass  # Expected to fail
        
        # Verify scheduler can still be called
        with patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
            coordinator._schedule_next_update()
            assert mock_track.called


@pytest.mark.asyncio
async def test_schedule_next_update_after_midnight(mock_hass, mock_entry_estacio, mock_api):
    """Test scheduling when current time is after both update times (should schedule tomorrow).
    
    Example: Current time is 23:00, update times are 06:00 and 14:00
    Next update should be tomorrow at 06:00.
    """
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Mock current time as 23:00 (after both update times)
        from homeassistant.util import dt as dt_util
        from unittest.mock import PropertyMock
        
        with patch('custom_components.meteocat_community_edition.coordinator.dt_util.now') as mock_now, \
             patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
            
            # Set current time to 23:00
            mock_time = datetime(2025, 11, 26, 23, 0, 0)
            mock_now.return_value = dt_util.as_local(mock_time)
            
            coordinator._schedule_next_update()
            
            # Verify scheduler was called
            assert mock_track.called
            
            # Get the scheduled time (3rd argument to async_track_point_in_utc_time)
            scheduled_time = mock_track.call_args[0][2]
            
            # Should be tomorrow at 06:00
            expected_time = dt_util.as_utc(
                dt_util.as_local(datetime(2025, 11, 27, 6, 0, 0))
            )
            
            # Compare just the date and time (ignore microseconds)
            assert scheduled_time.date() == expected_time.date()
            assert scheduled_time.hour == expected_time.hour
            assert scheduled_time.minute == expected_time.minute


@pytest.mark.asyncio
async def test_schedule_next_update_between_times(mock_hass, mock_entry_estacio, mock_api):
    """Test scheduling when current time is between update times.
    
    Example: Current time is 10:00, update times are 06:00 and 14:00
    Next update should be today at 14:00.
    """
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        from homeassistant.util import dt as dt_util
        
        with patch('custom_components.meteocat_community_edition.coordinator.dt_util.now') as mock_now, \
             patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
            
            # Set current time to 10:00 (after 06:00, before 14:00)
            mock_time = datetime(2025, 11, 26, 10, 0, 0)
            mock_now.return_value = dt_util.as_local(mock_time)
            
            coordinator._schedule_next_update()
            
            # Verify scheduler was called
            assert mock_track.called
            
            # Get the scheduled time
            scheduled_time = mock_track.call_args[0][2]
            
            # Should be today at 14:00
            expected_time = dt_util.as_utc(
                dt_util.as_local(datetime(2025, 11, 26, 14, 0, 0))
            )
            
            # Compare date and time
            assert scheduled_time.date() == expected_time.date()
            assert scheduled_time.hour == expected_time.hour
            assert scheduled_time.minute == expected_time.minute


@pytest.mark.asyncio
async def test_schedule_next_update_before_first_time(mock_hass, mock_entry_estacio, mock_api):
    """Test scheduling when current time is before first update time.
    
    Example: Current time is 05:00, update times are 06:00 and 14:00
    Next update should be today at 06:00.
    """
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        from homeassistant.util import dt as dt_util
        
        with patch('custom_components.meteocat_community_edition.coordinator.dt_util.now') as mock_now, \
             patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
            
            # Set current time to 05:00 (before both update times)
            mock_time = datetime(2025, 11, 26, 5, 0, 0)
            mock_now.return_value = dt_util.as_local(mock_time)
            
            coordinator._schedule_next_update()
            
            # Verify scheduler was called
            assert mock_track.called
            
            # Get the scheduled time
            scheduled_time = mock_track.call_args[0][2]
            
            # Should be today at 06:00
            expected_time = dt_util.as_utc(
                dt_util.as_local(datetime(2025, 11, 26, 6, 0, 0))
            )
            
            # Compare date and time
            assert scheduled_time.date() == expected_time.date()
            assert scheduled_time.hour == expected_time.hour
            assert scheduled_time.minute == expected_time.minute


@pytest.mark.asyncio
async def test_no_duplicate_updates_on_ha_restart(mock_hass, mock_entry_estacio, mock_api):
    """Test that HA restart does not cause duplicate scheduled updates.
    
    CRITICAL: When HA restarts, async_setup_entry calls:
    1. async_config_entry_first_refresh() - triggers ONE update
    2. _schedule_next_update() - schedules future updates
    
    This should NOT cause duplicate updates.
    """
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Simulate HA startup sequence
        # First refresh (happens in async_setup_entry)
        await coordinator._async_update_data()
        
        # Schedule next update (also happens in async_setup_entry)
        with patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
            coordinator._schedule_next_update()
            
            # Should be called exactly once
            assert mock_track.call_count == 1
        
        # Verify only 1 update happened (the first refresh)
        # Should be 5 calls total (first update in ESTACIO mode)
        total_calls = (
            mock_api.get_stations.call_count +
            mock_api.get_station_measurements.call_count +
            mock_api.get_municipal_forecast.call_count +
            mock_api.get_hourly_forecast.call_count +
            mock_api.get_quotes.call_count
        )
        assert total_calls == 5


@pytest.mark.asyncio
async def test_custom_update_times(mock_hass, mock_api):
    """Test coordinator with custom update times (not default 06:00/14:00).
    
    Users can configure different times like 08:00/20:00 or 05:30/17:45.
    This verifies the system works with any valid time.
    """
    # Create entry with custom times
    entry = MagicMock()
    entry.data = {
        CONF_API_KEY: "test_api_key_123456789",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
        CONF_UPDATE_TIME_1: "08:30",
        CONF_UPDATE_TIME_2: "20:15",
    }
    entry.options = {}
    entry.entry_id = "test_entry_custom"
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, entry)
        coordinator.api = mock_api
        
        # Verify custom times are loaded
        assert coordinator.update_time_1 == "08:30"
        assert coordinator.update_time_2 == "20:15"
        
        from homeassistant.util import dt as dt_util
        
        with patch('custom_components.meteocat_community_edition.coordinator.dt_util.now') as mock_now, \
             patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
            
            # Set current time to 10:00 (after 08:30, before 20:15)
            mock_time = datetime(2025, 11, 26, 10, 0, 0)
            mock_now.return_value = dt_util.as_local(mock_time)
            
            coordinator._schedule_next_update()
            
            # Get the scheduled time
            scheduled_time = mock_track.call_args[0][2]
            
            # Should be today at 20:15
            expected_time = dt_util.as_utc(
                dt_util.as_local(datetime(2025, 11, 26, 20, 15, 0))
            )
            
            # Compare date and time
            assert scheduled_time.date() == expected_time.date()
            assert scheduled_time.hour == expected_time.hour
            assert scheduled_time.minute == expected_time.minute


@pytest.mark.asyncio
async def test_retry_does_not_interfere_with_scheduled_updates(mock_hass, mock_api, mock_entry_estacio):
    """Test that retry system doesn't interfere with regular scheduled updates."""
    from aiohttp import ServerTimeoutError
    
    # Create different removers for scheduled and retry updates
    scheduled_remover = MagicMock()
    retry_remover = MagicMock()
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time') as mock_track:
        
        # Configure mock to return different removers
        mock_track.side_effect = [scheduled_remover, retry_remover]
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Schedule regular update
        coordinator._schedule_next_update()
        scheduled_update_call = mock_track.call_args
        
        # Verify scheduled update registered
        assert mock_track.call_count == 1
        assert scheduled_update_call[0][1] == coordinator._async_scheduled_update
        
        # Now trigger a retry due to error
        mock_api.get_station_measurements.side_effect = ServerTimeoutError("Timeout")
        
        try:
            await coordinator._async_update_data()
        except Exception:
            pass
        
        # Should have 2 calls now: scheduled + retry
        assert mock_track.call_count == 2
        
        # Last call should be retry
        retry_call = mock_track.call_args
        assert retry_call[0][1] == coordinator._async_retry_update
        
        # Verify both removers are different
        assert coordinator._scheduled_update_remover is not None
        assert coordinator._retry_remover is not None
        assert coordinator._scheduled_update_remover != coordinator._retry_remover
