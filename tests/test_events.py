"""Tests for Meteocat events."""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call

from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
from custom_components.meteocat_community_edition.const import (
    MODE_ESTACIO,
    MODE_MUNICIPI,
    EVENT_DATA_UPDATED,
    EVENT_NEXT_UPDATE_CHANGED,
    EVENT_ATTR_MODE,
    EVENT_ATTR_STATION_CODE,
    EVENT_ATTR_MUNICIPALITY_CODE,
    EVENT_ATTR_TIMESTAMP,
    EVENT_ATTR_NEXT_UPDATE,
    EVENT_ATTR_PREVIOUS_UPDATE,
    CONF_MODE,
    CONF_STATION_CODE,
    CONF_MUNICIPALITY_CODE,
    CONF_API_KEY,
)


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
        "plans": []
    })
    api.find_municipality_for_station = AsyncMock(return_value="081131")
    return api


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.bus = MagicMock()
    hass.bus.fire = MagicMock()  # Usar fire, no fire
    return hass


@pytest.fixture
def mock_device_registry():
    """Create a mock device registry."""
    mock_device = MagicMock()
    mock_device.id = "test_device_id"
    mock_registry = MagicMock()
    mock_registry.async_get_device.return_value = mock_device
    return mock_registry


@pytest.fixture
def mock_entry_estacio():
    """Create a mock config entry for MODE_ESTACIO."""
    entry = MagicMock()
    entry.data = {
        CONF_API_KEY: "test_api_key_123456789",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
        CONF_MUNICIPALITY_CODE: None,
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
        CONF_STATION_CODE: None,
        CONF_MUNICIPALITY_CODE: "081131",
    }
    entry.options = {}
    entry.entry_id = "test_entry_municipi"
    return entry


@pytest.mark.asyncio
async def test_event_fired_estacio_mode(mock_hass, mock_entry_estacio, mock_api, mock_device_registry):
    """Test that event is fired after update in MODE_ESTACIO."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Perform update
        await coordinator._async_update_data()
        
        # Check that event was fired
        mock_hass.bus.fire.assert_called()
        
        # Get the data_updated event call (second call, after next_update_changed)
        calls = mock_hass.bus.fire.call_args_list
        data_update_call = [c for c in calls if c[0][0] == EVENT_DATA_UPDATED][0]
        
        event_type = data_update_call[0][0]
        event_data = data_update_call[0][1]
        
        # Verify event type
        assert event_type == EVENT_DATA_UPDATED
        
        # Verify event data structure
        assert EVENT_ATTR_MODE in event_data
        assert event_data[EVENT_ATTR_MODE] == MODE_ESTACIO
        
        assert EVENT_ATTR_STATION_CODE in event_data
        assert event_data[EVENT_ATTR_STATION_CODE] == "YM"
        
        assert EVENT_ATTR_MUNICIPALITY_CODE in event_data
        # Municipality should be found for station
        assert event_data[EVENT_ATTR_MUNICIPALITY_CODE] == "081131"
        
        assert EVENT_ATTR_TIMESTAMP in event_data
        # Verify timestamp is ISO 8601 format
        timestamp = event_data[EVENT_ATTR_TIMESTAMP]
        assert isinstance(timestamp, str)
        # Should be parseable as datetime
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))


@pytest.mark.asyncio
async def test_event_fired_municipi_mode(mock_hass, mock_entry_municipi, mock_api, mock_device_registry):
    """Test that event is fired after update in MODE_MUNICIPI."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_municipi)
        coordinator.api = mock_api
        
        # Perform update
        await coordinator._async_update_data()
        
        # Check that event was fired
        mock_hass.bus.fire.assert_called()
        
        # Get the data_updated event call
        calls = mock_hass.bus.fire.call_args_list
        data_update_call = [c for c in calls if c[0][0] == EVENT_DATA_UPDATED][0]
        
        event_type = data_update_call[0][0]
        event_data = data_update_call[0][1]
        
        # Verify event type
        assert event_type == EVENT_DATA_UPDATED
        
        # Verify event data structure
        assert EVENT_ATTR_MODE in event_data
        assert event_data[EVENT_ATTR_MODE] == MODE_MUNICIPI
        
        # Station code should NOT be present in municipal mode
        assert EVENT_ATTR_STATION_CODE in event_data
        assert event_data[EVENT_ATTR_STATION_CODE] is None
        
        assert EVENT_ATTR_MUNICIPALITY_CODE in event_data
        assert event_data[EVENT_ATTR_MUNICIPALITY_CODE] == "081131"
        
        assert EVENT_ATTR_TIMESTAMP in event_data


@pytest.mark.asyncio
async def test_event_contains_valid_timestamp_format(mock_hass, mock_entry_estacio, mock_api, mock_device_registry):
    """Test that event timestamp is in valid ISO 8601 format."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        await coordinator._async_update_data()
        
        calls = mock_hass.bus.fire.call_args_list
        data_update_call = [c for c in calls if c[0][0] == EVENT_DATA_UPDATED][0]
        event_data = data_update_call[0][1]
        timestamp_str = event_data[EVENT_ATTR_TIMESTAMP]
        
        # Should be able to parse as ISO 8601
        parsed = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        assert isinstance(parsed, datetime)
        
        # Should be recent (within last minute)
        from datetime import timezone
        now = datetime.now(timezone.utc)
        diff = abs((now - parsed).total_seconds())
        assert diff < 60  # Within 1 minute


@pytest.mark.asyncio
async def test_event_not_fired_on_error(mock_hass, mock_entry_estacio, mock_api, mock_device_registry):
    """Test that event is NOT fired when update fails."""
    from custom_components.meteocat_community_edition.api import MeteocatAPIError
    
    # Make API fail
    mock_api.get_station_measurements.side_effect = MeteocatAPIError("API Error")
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # Perform update (should fail)
        with pytest.raises(Exception):
            await coordinator._async_update_data()
        
        # Event should NOT be fired
        mock_hass.bus.fire.assert_not_called()


@pytest.mark.asyncio
async def test_multiple_updates_fire_multiple_events(mock_hass, mock_entry_estacio, mock_api, mock_device_registry):
    """Test that each update fires a new event."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # First update
        await coordinator._async_update_data()
        first_count = mock_hass.bus.fire.call_count
        
        # Second update
        await coordinator._async_update_data()
        second_count = mock_hass.bus.fire.call_count
        
        # Third update
        await coordinator._async_update_data()
        third_count = mock_hass.bus.fire.call_count
        
        # Each update should fire events (both data_updated + potentially next_update_changed)
        assert second_count > first_count
        assert third_count > second_count


# -------------------------------------------------------------------
# Tests for EVENT_NEXT_UPDATE_CHANGED
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_next_update_changed_event_fired(mock_hass, mock_entry_estacio, mock_api, mock_device_registry):
    """Test that next_update_changed event is fired when next update time changes."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # First update - should fire both data_updated and next_update_changed
        await coordinator._async_update_data()
        
        # Should have 2 events: next_update_changed + data_updated
        assert mock_hass.bus.fire.call_count == 2
        
        # Get the calls
        calls = mock_hass.bus.fire.call_args_list
        
        # First call should be next_update_changed (fires first)
        next_update_call = calls[0]
        assert next_update_call[0][0] == EVENT_NEXT_UPDATE_CHANGED
        
        next_update_data = next_update_call[0][1]
        assert EVENT_ATTR_MODE in next_update_data
        assert next_update_data[EVENT_ATTR_MODE] == MODE_ESTACIO
        assert EVENT_ATTR_NEXT_UPDATE in next_update_data
        assert EVENT_ATTR_PREVIOUS_UPDATE in next_update_data
        assert next_update_data[EVENT_ATTR_PREVIOUS_UPDATE] is None  # First time
        assert next_update_data[EVENT_ATTR_NEXT_UPDATE] is not None
        
        # Second call should be data_updated
        data_update_call = calls[1]
        assert data_update_call[0][0] == EVENT_DATA_UPDATED


@pytest.mark.asyncio
async def test_next_update_changed_event_not_fired_when_same(mock_hass, mock_entry_estacio, mock_api, mock_device_registry):
    """Test that next_update_changed event is NOT fired when next update stays the same."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        # First update
        await coordinator._async_update_data()
        initial_call_count = mock_hass.bus.fire.call_count
        assert initial_call_count == 2  # next_update_changed + data_updated
        
        # Get the next_update value from first call
        first_next_update = mock_hass.bus.fire.call_args_list[0][0][1][EVENT_ATTR_NEXT_UPDATE]
        
        # Store it so second update has same value
        coordinator._previous_next_update = coordinator.last_successful_update_time + coordinator.update_interval if coordinator.last_successful_update_time and coordinator.update_interval else None
        
        # Second update (with mocked same next_update time)
        await coordinator._async_update_data()
        
        # Should only fire data_updated (not next_update_changed)
        # If next update didn't change, only 1 new event
        assert mock_hass.bus.fire.call_count == initial_call_count + 1
        
        # Last call should be data_updated only
        last_call = mock_hass.bus.fire.call_args_list[-1]
        assert last_call[0][0] == EVENT_DATA_UPDATED


@pytest.mark.asyncio
async def test_next_update_changed_event_includes_station_code(mock_hass, mock_entry_estacio, mock_api, mock_device_registry):
    """Test that next_update_changed event includes station code in ESTACIO mode."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        await coordinator._async_update_data()
        
        # Get next_update_changed event (first call)
        next_update_call = mock_hass.bus.fire.call_args_list[0]
        event_data = next_update_call[0][1]
        
        assert EVENT_ATTR_STATION_CODE in event_data
        assert event_data[EVENT_ATTR_STATION_CODE] == "YM"


@pytest.mark.asyncio
async def test_next_update_changed_event_includes_municipality_code(mock_hass, mock_entry_municipi, mock_api, mock_device_registry):
    """Test that next_update_changed event includes municipality code in MUNICIPI mode."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_municipi)
        coordinator.api = mock_api
        
        await coordinator._async_update_data()
        
        # Get next_update_changed event (first call)
        next_update_call = mock_hass.bus.fire.call_args_list[0]
        event_data = next_update_call[0][1]
        
        assert EVENT_ATTR_MUNICIPALITY_CODE in event_data
        assert event_data[EVENT_ATTR_MUNICIPALITY_CODE] == "081131"


@pytest.mark.asyncio
async def test_next_update_changed_event_has_valid_timestamp_format(mock_hass, mock_entry_estacio, mock_api, mock_device_registry):
    """Test that next_update_changed event next_update is in valid ISO 8601 format."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get', return_value=mock_device_registry):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api
        
        await coordinator._async_update_data()
        
        # Get next_update_changed event
        next_update_call = mock_hass.bus.fire.call_args_list[0]
        event_data = next_update_call[0][1]
        
        next_update_str = event_data[EVENT_ATTR_NEXT_UPDATE]
        assert next_update_str is not None
        
        # Should be parseable as ISO 8601
        parsed = datetime.fromisoformat(next_update_str.replace('Z', '+00:00'))
        assert isinstance(parsed, datetime)
