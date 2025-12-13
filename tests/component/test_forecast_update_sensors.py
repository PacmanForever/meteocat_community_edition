"""Tests for forecast update sensors in Station Mode."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
from homeassistant.util import dt as dt_util

from custom_components.meteocat_community_edition.coordinator import MeteocatLegacyCoordinator
from custom_components.meteocat_community_edition.sensor import (
    MeteocatNextForecastUpdateSensor,
    MeteocatLastForecastUpdateSensor,
)
from custom_components.meteocat_community_edition.const import (
    CONF_API_KEY,
    CONF_MODE,
    CONF_STATION_CODE,
    MODE_EXTERNAL,
)


@pytest.fixture
def mock_hass():
    """Create a mock hass object."""
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
        CONF_MODE: MODE_EXTERNAL,
        CONF_STATION_CODE: "YM",
        "update_time_1": "06:00",
        "update_time_2": "14:00",
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_coordinator(mock_hass, mock_entry):
    """Create a mock coordinator with forecast tracking."""
    coordinator = MagicMock()
    coordinator.entry = mock_entry
    coordinator.last_forecast_update = None
    coordinator.next_forecast_update = None
    coordinator.data = {}
    return coordinator


class TestMeteocatNextForecastUpdateSensor:
    """Tests for MeteocatNextForecastUpdateSensor."""

    def test_sensor_initialization(self, mock_coordinator, mock_entry):
        """Test sensor initializes correctly."""
        sensor = MeteocatNextForecastUpdateSensor(
            mock_coordinator,
            mock_entry,
            "Test Station",
            "Test Station YM",
            "YM",
        )
        
        assert sensor._attr_unique_id == "test_entry_id_next_forecast_update"
        assert sensor._attr_translation_key == "next_forecast_update"
        assert "ym" in sensor.entity_id.lower()

    def test_sensor_returns_next_forecast_update(self, mock_coordinator, mock_entry):
        """Test sensor returns coordinator.next_forecast_update."""
        expected_time = dt_util.now() + timedelta(hours=2)
        mock_coordinator.next_forecast_update = expected_time
        
        sensor = MeteocatNextForecastUpdateSensor(
            mock_coordinator,
            mock_entry,
            "Test Station",
            "Test Station YM",
            "YM",
        )
        
        assert sensor.native_value == expected_time

    def test_sensor_returns_none_when_no_forecast_update(self, mock_coordinator, mock_entry):
        """Test sensor returns None when next_forecast_update is not set."""
        mock_coordinator.next_forecast_update = None
        
        sensor = MeteocatNextForecastUpdateSensor(
            mock_coordinator,
            mock_entry,
            "Test Station",
            "Test Station YM",
            "YM",
        )
        
        assert sensor.native_value is None

    def test_sensor_icon(self, mock_coordinator, mock_entry):
        """Test sensor has correct icon."""
        sensor = MeteocatNextForecastUpdateSensor(
            mock_coordinator,
            mock_entry,
            "Test Station",
            "Test Station YM",
            "YM",
        )
        
        assert sensor.icon == "mdi:calendar-clock"


class TestMeteocatLastForecastUpdateSensor:
    """Tests for MeteocatLastForecastUpdateSensor."""

    def test_sensor_initialization(self, mock_coordinator, mock_entry):
        """Test sensor initializes correctly."""
        sensor = MeteocatLastForecastUpdateSensor(
            mock_coordinator,
            mock_entry,
            "Test Station",
            "Test Station YM",
            "YM",
        )
        
        assert sensor._attr_unique_id == "test_entry_id_last_forecast_update"
        assert sensor._attr_translation_key == "last_forecast_update"
        assert "ym" in sensor.entity_id.lower()

    def test_sensor_returns_last_forecast_update(self, mock_coordinator, mock_entry):
        """Test sensor returns coordinator.last_forecast_update."""
        expected_time = dt_util.now() - timedelta(hours=2)
        mock_coordinator.last_forecast_update = expected_time
        
        sensor = MeteocatLastForecastUpdateSensor(
            mock_coordinator,
            mock_entry,
            "Test Station",
            "Test Station YM",
            "YM",
        )
        
        assert sensor.native_value == expected_time

    def test_sensor_returns_none_when_no_forecast_update(self, mock_coordinator, mock_entry):
        """Test sensor returns None when last_forecast_update is not set."""
        mock_coordinator.last_forecast_update = None
        
        sensor = MeteocatLastForecastUpdateSensor(
            mock_coordinator,
            mock_entry,
            "Test Station",
            "Test Station YM",
            "YM",
        )
        
        assert sensor.native_value is None

    def test_sensor_icon(self, mock_coordinator, mock_entry):
        """Test sensor has correct icon."""
        sensor = MeteocatLastForecastUpdateSensor(
            mock_coordinator,
            mock_entry,
            "Test Station",
            "Test Station YM",
            "YM",
        )
        
        assert sensor.icon == "mdi:calendar-check"


class TestCoordinatorForecastTracking:
    """Tests for coordinator forecast update tracking."""

    @pytest.mark.asyncio
    async def test_coordinator_initializes_forecast_tracking_variables(self, mock_hass, mock_entry):
        """Test that coordinator initializes forecast tracking variables."""
        with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"):
            coordinator = MeteocatLegacyCoordinator(mock_hass, mock_entry)
        
        assert hasattr(coordinator, "last_forecast_update")
        assert hasattr(coordinator, "next_forecast_update")
        assert coordinator.last_forecast_update is None
        assert coordinator.next_forecast_update is None

    @pytest.mark.asyncio
    async def test_coordinator_calculates_next_forecast_update(self, mock_hass, mock_entry):
        """Test that coordinator calculates next forecast update."""
        with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"):
            coordinator = MeteocatLegacyCoordinator(mock_hass, mock_entry)
        
        # Mock time to 10:00 local time
        mock_now = datetime(2025, 12, 9, 10, 0, 0, tzinfo=dt_util.UTC)
        
        # Mock as_local to return the datetime with timezone
        def mock_as_local(dt):
            if dt.tzinfo is None:
                return dt.replace(tzinfo=dt_util.UTC)
            return dt
        
        with patch("custom_components.meteocat_community_edition.coordinator.dt_util.now", return_value=mock_now), \
             patch("custom_components.meteocat_community_edition.coordinator.dt_util.as_local", side_effect=mock_as_local), \
             patch("custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time"):
            coordinator._schedule_next_update()
        
        # Next forecast should be 14:00 (the next configured update time)
        assert coordinator.next_forecast_update is not None
        assert coordinator.next_forecast_update.hour == 14

    @pytest.mark.asyncio
    async def test_coordinator_next_forecast_wraps_to_tomorrow(self, mock_hass, mock_entry):
        """Test that next forecast update wraps to tomorrow if all times passed."""
        with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"):
            coordinator = MeteocatLegacyCoordinator(mock_hass, mock_entry)
        
        # Mock time to 22:00 (after all update times)
        mock_now = datetime(2025, 12, 9, 22, 0, 0, tzinfo=dt_util.UTC)
        
        with patch("custom_components.meteocat_community_edition.coordinator.dt_util.now", return_value=mock_now), \
             patch("custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time"):
            coordinator._schedule_next_update()
        
        # Next forecast should be 06:00 tomorrow
        assert coordinator.next_forecast_update is not None
        assert coordinator.next_forecast_update.hour == 6
        assert coordinator.next_forecast_update.day == 10  # Tomorrow
