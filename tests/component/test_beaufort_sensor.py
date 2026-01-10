"""Tests for Beaufort Sensors (Numeric & Description)."""
import sys
import os
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from custom_components.meteocat_community_edition.sensor import (
    MeteocatBeaufortSensor,
    MeteocatBeaufortDescriptionSensor
)
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

# --- MeteocatBeaufortSensor Tests ---

def test_beaufort_sensor_init(mock_coordinator, mock_entry):
    sensor = MeteocatBeaufortSensor(mock_coordinator, mock_entry, "Test Station YM")
    assert sensor.unique_id == "test_entry_beaufort_index"
    assert sensor.translation_key == "beaufort_index"
    assert sensor.device_class is None # Integer
    assert sensor.state_class == SensorStateClass.MEASUREMENT
    assert sensor.icon == "mdi:weather-windy"

def test_external_wind_update(mock_coordinator, mock_entry):
    sensor = MeteocatBeaufortSensor(mock_coordinator, mock_entry, "Test Device")
    
    # Wind Speed (30) in m/s. 
    # Example: 10 km/h = 2.77 m/s -> Beaufort 2
    mock_coordinator.data = {
        "measurements": [
            {
                "variables": [
                    {"codi": 30, "lectures": [{"valor": 2.78}]} # ~10 km/h
                ]
            }
        ]
    }
    
    sensor._update_external_value()
    assert sensor.native_value == 2
    assert sensor.available is True

def test_external_wind_calm(mock_coordinator, mock_entry):
    sensor = MeteocatBeaufortSensor(mock_coordinator, mock_entry, "Test Device")
    mock_coordinator.data = {
        "measurements": [
            {
                "variables": [
                    {"codi": 30, "lectures": [{"valor": 0.0}]} # 0 km/h -> Beaufort 0
                ]
            }
        ]
    }
    sensor._update_external_value()
    assert sensor.native_value == 0

def test_external_wind_missing(mock_coordinator, mock_entry):
    sensor = MeteocatBeaufortSensor(mock_coordinator, mock_entry, "Test Device")
    mock_coordinator.data = {
        "measurements": [{"variables": []}]
    }
    sensor._update_external_value()
    assert sensor.native_value is None
    assert sensor.available is False

# --- MeteocatBeaufortDescriptionSensor Tests ---

def test_description_sensor_init(mock_coordinator, mock_entry):
    sensor = MeteocatBeaufortDescriptionSensor(mock_coordinator, mock_entry, "Test Station YM")
    assert sensor.unique_id == "test_entry_beaufort_description"
    assert sensor.translation_key == "beaufort_description"
    assert sensor.device_class == SensorDeviceClass.ENUM
    assert sensor.icon == "mdi:windsock"

def test_description_update(mock_coordinator, mock_entry):
    sensor = MeteocatBeaufortDescriptionSensor(mock_coordinator, mock_entry, "Test Device")
    
    # 2.78 m/s -> ~10 km/h -> Beaufort 2 -> "beaufort_2"
    mock_coordinator.data = {
        "measurements": [
            {
                "variables": [
                    {"codi": 30, "lectures": [{"valor": 2.78}]} 
                ]
            }
        ]
    }
    
    sensor._update_external_value()
    assert sensor.native_value == "beaufort_2"
    assert sensor.available is True

def test_description_update_hurricane(mock_coordinator, mock_entry):
    sensor = MeteocatBeaufortDescriptionSensor(mock_coordinator, mock_entry, "Test Device")
    
    # > 118 km/h -> > 32.7 m/s. Let's try 40 m/s (~144 km/h)
    mock_coordinator.data = {
        "measurements": [
            {
                "variables": [
                    {"codi": 30, "lectures": [{"valor": 40.0}]} 
                ]
            }
        ]
    }
    
    sensor._update_external_value()
    # Should correspond to > 12
    assert sensor.native_value == "beaufort_hurricane"

