"""Tests for Meteocat binary sensor entities."""
import sys
import os
from unittest.mock import MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from custom_components.meteocat_community_edition.binary_sensor import (
    MeteocatUpdateStatusBinarySensor,
)
from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    MODE_ESTACIO,
    MODE_MUNICIPI,
)


@pytest.fixture
def mock_coordinator_success():
    """Create a mock coordinator with successful update."""
    coordinator = MagicMock()
    coordinator.last_update_success = True
    coordinator.last_successful_update_time = datetime(2025, 11, 27, 12, 0, 0)
    coordinator.data = {
        "measurements": [{"codi": "YM", "variables": []}],
        "forecast": {"dies": []},
    }
    return coordinator


@pytest.fixture
def mock_coordinator_failure():
    """Create a mock coordinator with failed update."""
    coordinator = MagicMock()
    coordinator.last_update_success = False
    coordinator.last_successful_update_time = None
    coordinator.last_exception = Exception("Connection timeout")
    coordinator.data = {}
    return coordinator


@pytest.fixture
def mock_entry_station():
    """Create a mock config entry for station mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "mode": MODE_ESTACIO,
        "station_code": "YM",
        "station_name": "Granollers",
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_entry_municipality():
    """Create a mock config entry for municipality mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "080193",
        "municipality_name": "Barcelona",
    }
    entry.options = {}
    return entry


def test_binary_sensor_initialization_station_mode(mock_coordinator_success, mock_entry_station):
    """Test binary sensor initialization in station mode."""
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    assert sensor.unique_id == "test_entry_update_status"
    assert sensor.device_class == "problem"
    assert sensor.entity_category == "diagnostic"
    assert sensor.has_entity_name is True
    assert sensor.translation_key == "update_status"


def test_binary_sensor_initialization_municipality_mode(mock_coordinator_success, mock_entry_municipality):
    """Test binary sensor initialization in municipality mode."""
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_municipality,
        "Barcelona",
        "Barcelona",
        MODE_MUNICIPI,
        None,
    )
    
    assert sensor.unique_id == "test_entry_update_status"
    assert sensor.entity_category == "diagnostic"
    assert sensor.has_entity_name is True
    assert sensor.translation_key == "update_status"


def test_binary_sensor_success_state(mock_coordinator_success, mock_entry_station):
    """Test binary sensor shows OFF when update is successful (no problem)."""
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    assert sensor.is_on is False  # OFF = no problem
    assert sensor.icon == "mdi:check-circle"
    
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "ok"
    assert "last_success" in attrs


def test_binary_sensor_failure_state(mock_coordinator_failure, mock_entry_station):
    """Test binary sensor shows ON when update fails (problem detected)."""
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_failure,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    assert sensor.is_on is True  # ON = problem
    assert sensor.icon == "mdi:alert-circle"
    
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert "error" in attrs
    # Should detect no data available
    assert "No data available" in attrs["error"]


def test_binary_sensor_no_data(mock_coordinator_success, mock_entry_station):
    """Test binary sensor shows ON when coordinator has no data (problem)."""
    mock_coordinator_success.data = {}
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    assert sensor.is_on is True  # ON = problem (no data)
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert "No data available" in attrs["error"]


def test_binary_sensor_station_mode_requires_measurements_or_forecast(mock_coordinator_success, mock_entry_station):
    """Test station mode requires measurements data."""
    # With measurements - no problem
    mock_coordinator_success.data = {
        "measurements": [{"codi": "YM"}],
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    assert sensor.is_on is False  # OFF = no problem
    
    # Without measurements - problem
    mock_coordinator_success.data = {
        "forecast": {"dies": [{"data": "2025-11-27"}]},  # Forecast doesn't help without measurements
    }
    
    assert sensor.is_on is True  # ON = problem (no measurements)
    
    # Empty data - problem
    mock_coordinator_success.data = {}
    
    assert sensor.is_on is True  # ON = problem (no data)


def test_binary_sensor_station_mode_checks_all_api_calls_with_municipality(mock_coordinator_success, mock_entry_station):
    """Test station mode checks ALL API calls when municipality_code is present."""
    # Station with municipality: must check measurements + all forecast calls
    mock_coordinator_success.data = {
        "municipality_code": "080193",
        "measurements": [{"codi": "YM"}],
        "forecast": {"dies": [{"data": "2025-11-27"}]},
        "forecast_hourly": {"dies": [{"data": "2025-11-27"}]},
        "uv_index": {"dies": [{"data": "2025-11-27"}]},
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    # All calls present - no problem
    assert sensor.is_on is False
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "ok"
    
    # Missing measurements - problem
    mock_coordinator_success.data = {
        "municipality_code": "080193",
        "forecast": {"dies": [{"data": "2025-11-27"}]},
        "forecast_hourly": {"dies": [{"data": "2025-11-27"}]},
        "uv_index": {"dies": [{"data": "2025-11-27"}]},
    }
    
    assert sensor.is_on is True
    attrs = sensor.extra_state_attributes
    assert "measurements" in attrs["error"]
    
    # Missing forecast - problem
    mock_coordinator_success.data = {
        "municipality_code": "080193",
        "measurements": [{"codi": "YM"}],
        "forecast_hourly": {"dies": [{"data": "2025-11-27"}]},
        "uv_index": {"dies": [{"data": "2025-11-27"}]},
    }
    
    assert sensor.is_on is True
    attrs = sensor.extra_state_attributes
    assert "forecast" in attrs["error"]
    
    # Missing uv_index - problem
    mock_coordinator_success.data = {
        "municipality_code": "080193",
        "measurements": [{"codi": "YM"}],
        "forecast": {"dies": [{"data": "2025-11-27"}]},
        "forecast_hourly": {"dies": [{"data": "2025-11-27"}]},
    }
    
    assert sensor.is_on is True
    attrs = sensor.extra_state_attributes
    assert "uv_index" in attrs["error"]


def test_binary_sensor_municipality_mode_requires_forecast(mock_coordinator_success, mock_entry_municipality):
    """Test municipality mode requires ALL forecast data (forecast, hourly, uv)."""
    # Has ALL forecasts - no problem
    mock_coordinator_success.data = {
        "forecast": {"dies": [{"data": "2025-11-27"}]},
        "forecast_hourly": {"dies": [{"data": "2025-11-27"}]},
        "uv_index": {"dies": [{"data": "2025-11-27"}]},
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_municipality,
        "Barcelona",
        "Barcelona",
        MODE_MUNICIPI,
        None,
    )
    
    assert sensor.is_on is False  # OFF = no problem
    
    # Only one forecast (missing others) - problem
    mock_coordinator_success.data = {
        "forecast": {"dies": [{"data": "2025-11-27"}]},
    }
    
    assert sensor.is_on is True  # ON = problem (missing hourly and uv)
    
    # No forecast - problem
    mock_coordinator_success.data = {}
    
    assert sensor.is_on is True  # ON = problem (no data)


def test_binary_sensor_municipality_mode_checks_all_api_calls(mock_coordinator_success, mock_entry_municipality):
    """Test municipality mode checks ALL API calls: forecast, forecast_hourly, and uv_index."""
    # All API calls present - no problem
    mock_coordinator_success.data = {
        "forecast": {"dies": [{"data": "2025-11-27"}]},
        "forecast_hourly": {"dies": [{"data": "2025-11-27"}]},
        "uv_index": {"dies": [{"data": "2025-11-27"}]},
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_municipality,
        "Barcelona",
        "Barcelona",
        MODE_MUNICIPI,
        None,
    )
    
    assert sensor.is_on is False  # OFF = no problem
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "ok"
    
    # Missing forecast - problem
    mock_coordinator_success.data = {
        "forecast_hourly": {"dies": [{"data": "2025-11-27"}]},
        "uv_index": {"dies": [{"data": "2025-11-27"}]},
    }
    
    assert sensor.is_on is True  # ON = problem
    attrs = sensor.extra_state_attributes
    assert "forecast" in attrs["error"]
    
    # Missing forecast_hourly - problem
    mock_coordinator_success.data = {
        "forecast": {"dies": [{"data": "2025-11-27"}]},
        "uv_index": {"dies": [{"data": "2025-11-27"}]},
    }
    
    assert sensor.is_on is True  # ON = problem
    attrs = sensor.extra_state_attributes
    assert "forecast_hourly" in attrs["error"]
    
    # Missing uv_index - problem
    mock_coordinator_success.data = {
        "forecast": {"dies": [{"data": "2025-11-27"}]},
        "forecast_hourly": {"dies": [{"data": "2025-11-27"}]},
    }
    
    assert sensor.is_on is True  # ON = problem
    attrs = sensor.extra_state_attributes
    assert "uv_index" in attrs["error"]
    
    # Multiple missing calls
    mock_coordinator_success.data = {
        "forecast": {"dies": [{"data": "2025-11-27"}]},
    }
    
    assert sensor.is_on is True  # ON = problem
    attrs = sensor.extra_state_attributes
    assert "forecast_hourly" in attrs["error"]
    assert "uv_index" in attrs["error"]


def test_binary_sensor_quota_exhausted_station_mode(mock_coordinator_success, mock_entry_station):
    """Test binary sensor detects quota exhaustion in station mode."""
    # Simulate quota exhausted: update success with empty measurements
    mock_coordinator_success.last_update_success = True
    mock_coordinator_success.data = {
        "measurements": [],  # Empty list = quota exhausted
        "quotes": {}
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    assert sensor.is_on is True  # ON = problem (missing data)
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert "quota exhausted" in attrs["error"].lower()


def test_binary_sensor_quota_exhausted_municipality_mode(mock_coordinator_success, mock_entry_municipality):
    """Test binary sensor detects quota exhaustion in municipality mode."""
    # Simulate quota exhausted: update success with empty forecasts
    mock_coordinator_success.last_update_success = True
    mock_coordinator_success.data = {
        "forecast": [],  # Empty list = quota exhausted
        "forecast_hourly": [],
        "uv_index": [],
        "quotes": {}
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_municipality,
        "Barcelona",
        "Barcelona",
        MODE_MUNICIPI,
        None,
    )
    
    assert sensor.is_on is True  # ON = problem (missing data)
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert "quota exhausted" in attrs["error"].lower()


def test_binary_sensor_always_available(mock_coordinator_failure, mock_entry_station):
    """Test binary sensor is always available, even when updates fail."""
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_failure,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    # Should be available even though coordinator failed
    assert sensor.available is True


def test_binary_sensor_device_info_station_mode(mock_coordinator_success, mock_entry_station):
    """Test binary sensor device info in station mode."""
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    device_info = sensor.device_info
    assert device_info["name"] == "Granollers YM"
    assert device_info["model"] == "Estació XEMA"
    assert (DOMAIN, "test_entry") in device_info["identifiers"]


def test_binary_sensor_device_info_municipality_mode(mock_coordinator_success, mock_entry_municipality):
    """Test binary sensor device info in municipality mode."""
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_municipality,
        "Barcelona",
        "Barcelona",
        MODE_MUNICIPI,
        None,
    )
    
    device_info = sensor.device_info
    assert device_info["name"] == "Barcelona"
    assert device_info["model"] == "Predicció Municipal"


def test_binary_sensor_icon_when_ok(mock_coordinator_success, mock_entry_station):
    """Test binary sensor shows check-circle icon when no problem."""
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    assert sensor.is_on is False
    assert sensor.icon == "mdi:check-circle"


def test_binary_sensor_icon_when_problem(mock_coordinator_failure, mock_entry_station):
    """Test binary sensor shows alert-circle icon when problem detected."""
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_failure,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    assert sensor.is_on is True
    assert sensor.icon == "mdi:alert-circle"


def test_binary_sensor_attributes_when_ok(mock_coordinator_success, mock_entry_station):
    """Test binary sensor attributes when everything is ok."""
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "ok"
    assert "last_success" in attrs
    assert "error" not in attrs
    assert attrs["last_success"] == "2025-11-27T12:00:00"


def test_binary_sensor_attributes_when_error(mock_coordinator_success, mock_entry_station):
    """Test binary sensor attributes show specific error message."""
    # Simulate empty data (quota exhausted)
    mock_coordinator_success.data = {
        "measurements": [],  # Empty list indicates quota exhausted
        "quotes": {}
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert "error" in attrs
    assert "quota exhausted" in attrs["error"].lower()


def test_binary_sensor_device_class_is_problem(mock_coordinator_success, mock_entry_station):
    """Test binary sensor has device_class PROBLEM."""
    from homeassistant.components.binary_sensor import BinarySensorDeviceClass
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    assert sensor.device_class == BinarySensorDeviceClass.PROBLEM


def test_binary_sensor_entity_category_is_diagnostic(mock_coordinator_success, mock_entry_station):
    """Test binary sensor has entity_category DIAGNOSTIC."""
    from homeassistant.helpers.entity import EntityCategory
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    assert sensor.entity_category == EntityCategory.DIAGNOSTIC


def test_binary_sensor_translation_key(mock_coordinator_success, mock_entry_station):
    """Test binary sensor has correct translation_key."""
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator_success,
        mock_entry_station,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM",
    )
    
    assert hasattr(sensor, "_attr_translation_key")
    assert sensor._attr_translation_key == "update_status"
