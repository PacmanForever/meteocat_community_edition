"""Tests for UTCI Literal Sensor."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from unittest.mock import MagicMock
from homeassistant.components.sensor import SensorDeviceClass

from custom_components.meteocat_community_edition.sensor import MeteocatUTCILiteralSensor
from custom_components.meteocat_community_edition.const import MODE_LOCAL, MODE_EXTERNAL

@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.data = {}
    return coordinator

@pytest.fixture
def mock_entry():
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "mode": MODE_EXTERNAL,
        "station_code": "YM",
    }
    return entry

def test_sensor_init(mock_coordinator, mock_entry):
    sensor = MeteocatUTCILiteralSensor(mock_coordinator, mock_entry, "Test Device")
    assert sensor.unique_id == "test_entry_utci_literal"
    assert sensor.translation_key == "utci_category"
    assert sensor.device_class == SensorDeviceClass.ENUM
    assert sensor.native_unit_of_measurement is None

def test_update_status_heat_extreme(mock_coordinator, mock_entry):
    sensor = MeteocatUTCILiteralSensor(mock_coordinator, mock_entry, "Test Device")
    sensor._update_status_from_utci(50.0)
    assert sensor.native_value == "stress_extreme_heat"
    assert sensor.icon == "mdi:thermometer-alert"
    assert sensor.available is True

def test_update_status_comfort(mock_coordinator, mock_entry):
    sensor = MeteocatUTCILiteralSensor(mock_coordinator, mock_entry, "Test Device")
    sensor._update_status_from_utci(20.0)
    assert sensor.native_value == "comfort_no_stress"
    assert sensor.icon == "mdi:check-circle-outline"
    assert sensor.available is True

def test_update_status_cold_extreme(mock_coordinator, mock_entry):
    sensor = MeteocatUTCILiteralSensor(mock_coordinator, mock_entry, "Test Device")
    sensor._update_status_from_utci(-30.0)
    assert sensor.native_value == "stress_extreme_cold"
    assert sensor.icon == "mdi:snowflake-alert"
    assert sensor.available is True

def test_update_status_none(mock_coordinator, mock_entry):
    sensor = MeteocatUTCILiteralSensor(mock_coordinator, mock_entry, "Test Device")
    sensor._update_status_from_utci(None)
    assert sensor.native_value is None
    assert sensor.available is False
