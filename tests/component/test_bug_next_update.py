
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
from custom_components.meteocat_community_edition.const import (
    CONF_API_KEY,
    CONF_MODE,
    CONF_STATION_CODE,
    CONF_MUNICIPALITY_CODE,
    MODE_EXTERNAL,
)
from homeassistant.util import dt as dt_util

@pytest.fixture
def mock_hass():
    hass = MagicMock()
    hass.data = {}
    return hass

@pytest.fixture
def mock_entry():
    entry = MagicMock()
    entry.data = {
        CONF_API_KEY: "test_key",
        CONF_MODE: MODE_EXTERNAL,
        CONF_STATION_CODE: "YM",
        "update_time_1": "06:00",
        "update_time_2": "14:00",
    }
    entry.options = {}
    return entry

@pytest.mark.asyncio
async def test_next_update_value_during_refresh(mock_hass, mock_entry):
    """Test that next_scheduled_update is updated BEFORE listeners are notified."""
    
    # Setup coordinator
    coordinator = MeteocatCoordinator(mock_hass, mock_entry)
    coordinator.meteocat = MagicMock()
    coordinator.meteocat.get_station_measurements = AsyncMock(return_value=[])
    coordinator.meteocat.get_forecast_daily = AsyncMock(return_value={})
    coordinator.meteocat.get_quotes = AsyncMock(return_value={})
    
    # Mock async_request_refresh to simulate what it does: notify listeners
    async def mock_refresh():
        coordinator.async_update_listeners()
        
    coordinator.async_request_refresh = AsyncMock(side_effect=mock_refresh)
    
    # Mock time to 05:59 UTC
    initial_time = datetime(2025, 12, 9, 5, 59, 0, tzinfo=dt_util.UTC)
    
    # Patch as_local to treat everything as UTC to avoid timezone confusion in tests
    with patch("custom_components.meteocat_community_edition.coordinator.dt_util.now", return_value=initial_time), \
         patch("custom_components.meteocat_community_edition.coordinator.dt_util.as_local", side_effect=lambda x: x.replace(tzinfo=dt_util.UTC)):
        
        # Initial schedule
        coordinator._schedule_next_update()
        
        # Verify initial next update is 06:00
        assert coordinator.next_scheduled_update.hour == 6
        assert coordinator.next_scheduled_update.minute == 0
    
    # Create a listener to capture the value when notified
    captured_next_update = []
    def listener():
        captured_next_update.append(coordinator.next_scheduled_update)
        
    coordinator.async_add_listener(listener)
    
    # Advance time to 06:00:01 UTC
    update_time = datetime(2025, 12, 9, 6, 0, 1, tzinfo=dt_util.UTC)
    
    with patch("custom_components.meteocat_community_edition.coordinator.dt_util.now", return_value=update_time), \
         patch("custom_components.meteocat_community_edition.coordinator.dt_util.as_local", side_effect=lambda x: x.replace(tzinfo=dt_util.UTC)):
        
        # Run the scheduled update
        await coordinator._async_scheduled_update(update_time)
        
    # Check what the listener saw
    assert len(captured_next_update) > 0, "Listener was not called"
    last_seen_value = captured_next_update[-1]
    
    # We expect the next update to be 07:00 (hourly updates)
    assert last_seen_value.hour == 7, f"Listener saw next update at {last_seen_value.hour}:{last_seen_value.minute}, expected 07:00"
