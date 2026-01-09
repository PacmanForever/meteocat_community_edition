"""Tests for UTCI Sensor (Numeric)."""
import sys
import os
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature

from custom_components.meteocat_community_edition.sensor import MeteocatUTCISensor
from custom_components.meteocat_community_edition.const import MODE_EXTERNAL, MODE_LOCAL

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
        "station_name": "Test Station",
    }
    return entry

def test_sensor_init(mock_coordinator, mock_entry):
    sensor = MeteocatUTCISensor(mock_coordinator, mock_entry, "Test Station YM")
    assert sensor.unique_id == "test_entry_utci"
    assert sensor.translation_key == "utci_index"
    assert sensor.device_class == SensorDeviceClass.TEMPERATURE
    assert sensor.native_unit_of_measurement == UnitOfTemperature.CELSIUS
    assert sensor.state_class == SensorStateClass.MEASUREMENT

def test_external_calc_valid(mock_coordinator, mock_entry):
    sensor = MeteocatUTCISensor(mock_coordinator, mock_entry, "Test Device")
    
    # 32: Temp, 33: Hum, 30: Wind (m/s)
    mock_coordinator.data = {
        "mesures": {
            32: {"valor": 30.0},
            33: {"valor": 50.0},
            30: {"valor": 5.0}  # 5 m/s = 18 km/h
        }
    }
    
    sensor._update_external_value()
    # Approx calc: 30 + (...)
    # Check if value is set and available
    assert sensor.native_value is not None
    assert isinstance(sensor.native_value, float)
    assert sensor.available is True

def test_external_calc_missing_temps(mock_coordinator, mock_entry):
    # Test missing data handling
    sensor = MeteocatUTCISensor(mock_coordinator, mock_entry, "Test Device")

    mock_coordinator.data = {
        "mesures": {
            33: {"valor": 50.0},
            30: {"valor": 5.0} 
        }
    }
    sensor._update_external_value()
    assert sensor.native_value is None
    assert sensor.available is False

def test_external_calc_error_values(mock_coordinator, mock_entry):
    sensor = MeteocatUTCISensor(mock_coordinator, mock_entry, "Test Device")
    
    mock_coordinator.data = {
        "mesures": {
            32: {"valor": "invalid"},
            33: {"valor": 50.0},
            30: {"valor": 5.0} 
        }
    }
    sensor._update_external_value()
    assert sensor.native_value is None
    assert sensor.available is False
