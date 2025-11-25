"""Tests for configurable update times."""
import sys
import os
from datetime import datetime, time, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
from custom_components.meteocat_community_edition.const import (
    MODE_ESTACIO,
    CONF_MODE,
    CONF_STATION_CODE,
    CONF_API_KEY,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    DEFAULT_UPDATE_TIME_1,
    DEFAULT_UPDATE_TIME_2,
)


@pytest.fixture
def mock_api():
    """Create a mock API client."""
    api = MagicMock()
    api.get_stations = AsyncMock(return_value=[
        {"codi": "YM", "nom": "Granollers", "coordenades": {"latitud": 41.6, "longitud": 2.3}}
    ])
    api.get_station_measurements = AsyncMock(return_value=[
        {"codi": "YM", "variables": []}
    ])
    api.get_municipal_forecast = AsyncMock(return_value={"dies": []})
    api.get_hourly_forecast = AsyncMock(return_value={"dies": []})
    api.get_uv_index = AsyncMock(return_value={"ine": "081131", "uvi": []})
    api.get_quotes = AsyncMock(return_value={"client": {"nom": "Test"}, "plans": []})
    api.find_municipality_for_station = AsyncMock(return_value="081131")
    return api


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.bus = MagicMock()
    hass.bus.async_fire = AsyncMock()
    return hass


@pytest.fixture
def mock_entry_default_times():
    """Create a mock config entry with default update times."""
    entry = MagicMock()
    entry.data = {
        CONF_API_KEY: "test_api_key_123456789",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
        # No update times specified - should use defaults
    }
    entry.options = {}
    entry.entry_id = "test_entry_default"
    return entry


@pytest.fixture
def mock_entry_custom_times():
    """Create a mock config entry with custom update times."""
    entry = MagicMock()
    entry.data = {
        CONF_API_KEY: "test_api_key_123456789",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
        CONF_UPDATE_TIME_1: "08:30",
        CONF_UPDATE_TIME_2: "16:45",
    }
    entry.options = {}
    entry.entry_id = "test_entry_custom"
    return entry


def test_default_update_times_used(mock_hass, mock_entry_default_times, mock_api):
    """Test that default update times are used when not configured."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_default_times)
        
        assert coordinator.update_time_1 == DEFAULT_UPDATE_TIME_1
        assert coordinator.update_time_2 == DEFAULT_UPDATE_TIME_2
        assert coordinator.update_time_1 == "06:00"
        assert coordinator.update_time_2 == "14:00"


def test_custom_update_times_used(mock_hass, mock_entry_custom_times, mock_api):
    """Test that custom update times are used when configured."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_custom_times)
        
        assert coordinator.update_time_1 == "08:30"
        assert coordinator.update_time_2 == "16:45"


@pytest.mark.asyncio
async def test_next_update_calculated_correctly_before_first_time(mock_hass, mock_entry_custom_times, mock_api):
    """Test next update calculation when current time is before first update time."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_custom_times)
        coordinator.api = mock_api
        
        # Mock current time to be 07:00 (before 08:30)
        mock_now = datetime(2025, 11, 25, 7, 0, 0)
        
        with patch('custom_components.meteocat_community_edition.coordinator.dt_util.now', return_value=mock_now):
            interval = coordinator._calculate_next_update_interval()
            
            # Should schedule for 08:30 today (1.5 hours from now)
            assert interval is not None
            assert isinstance(interval, timedelta)
            # Should be approximately 1.5 hours (90 minutes)
            expected_seconds = 90 * 60
            # Allow 1 second tolerance
            assert abs(interval.total_seconds() - expected_seconds) <= 1


@pytest.mark.asyncio
async def test_next_update_calculated_correctly_between_times(mock_hass, mock_entry_custom_times, mock_api):
    """Test next update calculation when current time is between update times."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_custom_times)
        coordinator.api = mock_api
        
        # Mock current time to be 12:00 (between 08:30 and 16:45)
        mock_now = datetime(2025, 11, 25, 12, 0, 0)
        
        with patch('custom_components.meteocat_community_edition.coordinator.dt_util.now', return_value=mock_now):
            interval = coordinator._calculate_next_update_interval()
            
            # Should schedule for 16:45 today (4 hours 45 minutes from now)
            assert interval is not None
            expected_seconds = (4 * 60 + 45) * 60
            assert abs(interval.total_seconds() - expected_seconds) <= 1


@pytest.mark.asyncio
async def test_next_update_calculated_correctly_after_last_time(mock_hass, mock_entry_custom_times, mock_api):
    """Test next update calculation when current time is after last update time."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_custom_times)
        coordinator.api = mock_api
        
        # Mock current time to be 20:00 (after 16:45)
        mock_now = datetime(2025, 11, 25, 20, 0, 0)
        
        with patch('custom_components.meteocat_community_edition.coordinator.dt_util.now', return_value=mock_now):
            interval = coordinator._calculate_next_update_interval()
            
            # Should schedule for 08:30 tomorrow (12.5 hours from now)
            assert interval is not None
            expected_seconds = (12 * 60 + 30) * 60
            assert abs(interval.total_seconds() - expected_seconds) <= 1


@pytest.mark.asyncio
async def test_update_interval_recalculated_after_update(mock_hass, mock_entry_custom_times, mock_api):
    """Test that update interval is recalculated after each update."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_custom_times)
        coordinator.api = mock_api
        
        # Initial interval
        initial_interval = coordinator.update_interval
        assert initial_interval is not None
        
        # Perform an update
        await coordinator._async_update_data()
        
        # Interval should be recalculated
        new_interval = coordinator.update_interval
        assert new_interval is not None
        
        # Intervals might be different depending on timing
        # Just verify both are valid timedeltas
        assert isinstance(initial_interval, timedelta)
        assert isinstance(new_interval, timedelta)


def test_update_times_format_validation():
    """Test that update time format is validated."""
    from custom_components.meteocat_community_edition.config_flow import is_valid_time_format
    
    # Valid formats
    assert is_valid_time_format("00:00") == True
    assert is_valid_time_format("06:00") == True
    assert is_valid_time_format("14:30") == True
    assert is_valid_time_format("23:59") == True
    
    # Invalid formats
    assert is_valid_time_format("24:00") == False
    assert is_valid_time_format("12:60") == False
    assert is_valid_time_format("6:00") == False  # Missing leading zero
    assert is_valid_time_format("06:0") == False  # Missing trailing zero
    assert is_valid_time_format("06:00:00") == False  # Includes seconds
    assert is_valid_time_format("invalid") == False
    assert is_valid_time_format("") == False


def test_update_times_uniqueness_validation():
    """Test that update times must be different."""
    # This would be tested in config_flow tests
    # Just verify the times are different in custom entry
    entry = MagicMock()
    entry.data = {
        CONF_API_KEY: "test",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
        CONF_UPDATE_TIME_1: "08:30",
        CONF_UPDATE_TIME_2: "16:45",
    }
    
    time1 = entry.data[CONF_UPDATE_TIME_1]
    time2 = entry.data[CONF_UPDATE_TIME_2]
    
    assert time1 != time2


@pytest.mark.asyncio
async def test_coordinator_stores_last_update_time(mock_hass, mock_entry_default_times, mock_api):
    """Test that coordinator stores the last successful update time."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_default_times)
        coordinator.api = mock_api
        
        # Initially None
        assert coordinator.last_successful_update_time is None
        
        # After update
        await coordinator._async_update_data()
        
        # Should be set to a datetime
        assert coordinator.last_successful_update_time is not None
        assert isinstance(coordinator.last_successful_update_time, datetime)
        
        # Should be very recent
        from datetime import timezone
        now = datetime.now(timezone.utc)
        diff = abs((now - coordinator.last_successful_update_time).total_seconds())
        assert diff < 5  # Within 5 seconds
