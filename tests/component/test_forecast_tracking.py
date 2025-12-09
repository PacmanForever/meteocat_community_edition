"""Tests for forecast tracking in Station Mode.

These tests verify that in MODE_ESTACIO, the coordinator correctly tracks
measurement updates (hourly) separately from forecast updates (scheduled).
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from homeassistant.util import dt as dt_util

from custom_components.meteocat_community_edition.coordinator import MeteocatLegacyCoordinator
from custom_components.meteocat_community_edition.const import (
    CONF_API_KEY,
    CONF_MODE,
    CONF_STATION_CODE,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    MODE_ESTACIO,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    return hass


@pytest.fixture
def mock_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        CONF_API_KEY: "test_key",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
        CONF_UPDATE_TIME_1: "06:00",
        CONF_UPDATE_TIME_2: "14:00",
    }
    entry.options = {}
    return entry


@pytest.mark.asyncio
async def test_coordinator_has_forecast_tracking_attributes(mock_hass, mock_entry):
    """Test that the coordinator has last_forecast_update and next_forecast_update."""
    coordinator = MeteocatLegacyCoordinator(mock_hass, mock_entry)
    
    assert hasattr(coordinator, "last_forecast_update")
    assert hasattr(coordinator, "next_forecast_update")
    assert coordinator.last_forecast_update is None
    assert coordinator.next_forecast_update is None


@pytest.mark.asyncio
async def test_schedule_next_update_calculates_next_forecast(mock_hass, mock_entry):
    """Test that _schedule_next_update calculates next_forecast_update."""
    coordinator = MeteocatLegacyCoordinator(mock_hass, mock_entry)
    
    # Mock time to 10:00 (between 06:00 and 14:00)
    mock_time = datetime(2025, 12, 9, 10, 0, 0, tzinfo=dt_util.UTC)
    
    with patch("custom_components.meteocat_community_edition.coordinator.dt_util.now", return_value=mock_time), \
         patch("custom_components.meteocat_community_edition.coordinator.dt_util.as_local", side_effect=lambda x: x.replace(tzinfo=dt_util.UTC) if x else x), \
         patch("custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time"):
        
        coordinator._schedule_next_update()
        
        # next_scheduled_update should be 11:00 (next hour)
        assert coordinator.next_scheduled_update is not None
        assert coordinator.next_scheduled_update.hour == 11
        
        # next_forecast_update should be 14:00
        assert coordinator.next_forecast_update is not None
        assert coordinator.next_forecast_update.hour == 14


@pytest.mark.asyncio
async def test_next_forecast_update_wraps_to_next_day(mock_hass, mock_entry):
    """Test that next_forecast_update wraps to next day after all times passed."""
    coordinator = MeteocatLegacyCoordinator(mock_hass, mock_entry)
    
    # Mock time to 20:00 (after both 06:00 and 14:00)
    mock_time = datetime(2025, 12, 9, 20, 0, 0, tzinfo=dt_util.UTC)
    
    with patch("custom_components.meteocat_community_edition.coordinator.dt_util.now", return_value=mock_time), \
         patch("custom_components.meteocat_community_edition.coordinator.dt_util.as_local", side_effect=lambda x: x.replace(tzinfo=dt_util.UTC) if x else x), \
         patch("custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time"):
        
        coordinator._schedule_next_update()
        
        # next_forecast_update should be 06:00 tomorrow
        assert coordinator.next_forecast_update is not None
        assert coordinator.next_forecast_update.day == 10
        assert coordinator.next_forecast_update.hour == 6


@pytest.mark.asyncio
async def test_hourly_update_does_not_affect_forecast_tracking(mock_hass, mock_entry):
    """Test that hourly updates don't interfere with forecast schedule tracking."""
    coordinator = MeteocatLegacyCoordinator(mock_hass, mock_entry)
    
    # Mock time to 10:30
    mock_time = datetime(2025, 12, 9, 10, 30, 0, tzinfo=dt_util.UTC)
    
    with patch("custom_components.meteocat_community_edition.coordinator.dt_util.now", return_value=mock_time), \
         patch("custom_components.meteocat_community_edition.coordinator.dt_util.as_local", side_effect=lambda x: x.replace(tzinfo=dt_util.UTC) if x else x), \
         patch("custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time"):
        
        coordinator._schedule_next_update()
        
        # Verify both tracking values are set correctly
        assert coordinator.next_scheduled_update.hour == 11  # Next hour for measurements
        assert coordinator.next_forecast_update.hour == 14  # Next configured time for forecast
