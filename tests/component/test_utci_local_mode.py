"""Tests for UTCI Sensor in Local Mode."""
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from homeassistant.const import STATE_UNKNOWN, STATE_UNAVAILABLE
from homeassistant.core import Event
from homeassistant.components.sensor import SensorDeviceClass

from custom_components.meteocat_community_edition.sensor import MeteocatUTCISensor, MeteocatUTCILiteralSensor
from custom_components.meteocat_community_edition.const import MODE_LOCAL

@pytest.fixture
def mock_hass():
    hass = MagicMock()
    hass.states.get = MagicMock()
    return hass

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
        "mode": MODE_LOCAL,
        "station_code": "YM",
        "station_name": "Test Station",
        "sensor_humidity": "sensor.hum",
        "sensor_temperature": "sensor.temp",
        "sensor_wind_speed": "sensor.wind"
    }
    entry.options = {}
    return entry

class MockState:
    def __init__(self, state):
        self.state = state

def test_sensor_init_local(mock_hass, mock_coordinator, mock_entry):
    sensor = MeteocatUTCISensor(mock_coordinator, mock_entry, "Test Local")
    sensor.hass = mock_hass
    
    # Check that source sensors are read from options
    assert sensor._source_temp == "sensor.temp"
    assert sensor._source_hum == "sensor.hum"
    assert sensor._source_wind == "sensor.wind"

def test_local_calc_valid(mock_hass, mock_coordinator, mock_entry):
    sensor = MeteocatUTCISensor(mock_coordinator, mock_entry, "Test Local")
    sensor.hass = mock_hass
    sensor.async_write_ha_state = MagicMock()
    
    # Mock source states
    def get_state_side_effect(entity_id):
        if entity_id == "sensor.temp":
            return MockState("20.0")
        if entity_id == "sensor.hum":
            return MockState("50.0")
        if entity_id == "sensor.wind":
            return MockState("10.0")
        return None
    
    mock_hass.states.get.side_effect = get_state_side_effect
    
    # Trigger update
    sensor._update_local_value()
    
    assert sensor.native_value is not None
    assert isinstance(sensor.native_value, float)
    assert sensor.available is True

def test_local_calc_missing_source_state(mock_hass, mock_coordinator, mock_entry):
    sensor = MeteocatUTCISensor(mock_coordinator, mock_entry, "Test Local")
    sensor.hass = mock_hass
    sensor.async_write_ha_state = MagicMock()
    
    # Missing one sensor
    def get_state_side_effect(entity_id):
        if entity_id == "sensor.temp":
            return MockState("20.0")
        return None # Hum/Wind missing
    
    mock_hass.states.get.side_effect = get_state_side_effect
    
    sensor._update_local_value()
    assert sensor.native_value is None
    assert sensor.available is False

def test_local_calc_unavailable_source(mock_hass, mock_coordinator, mock_entry):
    sensor = MeteocatUTCISensor(mock_coordinator, mock_entry, "Test Local")
    sensor.hass = mock_hass
    sensor.async_write_ha_state = MagicMock()
    
    def get_state_side_effect(entity_id):
        if entity_id == "sensor.temp":
            return MockState("20.0")
        if entity_id == "sensor.hum":
            return MockState(STATE_UNAVAILABLE)
        if entity_id == "sensor.wind":
            return MockState("10.0")
        return None
    
    mock_hass.states.get.side_effect = get_state_side_effect
    
    sensor._update_local_value()
    assert sensor.native_value is None
    assert sensor.available is False

def test_local_calc_invalid_value(mock_hass, mock_coordinator, mock_entry):
    sensor = MeteocatUTCISensor(mock_coordinator, mock_entry, "Test Local")
    sensor.hass = mock_hass
    sensor.async_write_ha_state = MagicMock()
    
    def get_state_side_effect(entity_id):
        if entity_id == "sensor.temp":
            return MockState("foo")
        if entity_id == "sensor.hum":
            return MockState("50.0")
        if entity_id == "sensor.wind":
            return MockState("10.0")
        return None
    
    mock_hass.states.get.side_effect = get_state_side_effect
    
    sensor._update_local_value()
    assert sensor.native_value is None
    assert sensor.available is False

def test_handle_local_update_callback(mock_hass, mock_coordinator, mock_entry):
    sensor = MeteocatUTCISensor(mock_coordinator, mock_entry, "Test Local")
    sensor.hass = mock_hass
    sensor.async_write_ha_state = MagicMock()
    
    # Mock valid states
    mock_hass.states.get.return_value = MockState("20")
    
    # Trigger callback
    sensor._handle_local_update(MagicMock(spec=Event))
    
    assert sensor.async_write_ha_state.called

def test_literal_sensor_local_update(mock_hass, mock_coordinator, mock_entry):
    sensor = MeteocatUTCILiteralSensor(mock_coordinator, mock_entry, "Test Local Literal")
    sensor.hass = mock_hass
    sensor.async_write_ha_state = MagicMock()
    
    # Valid setup
    def get_state_side_effect(entity_id):
        if entity_id == "sensor.temp":
            return MockState("20.0")
        if entity_id == "sensor.hum":
            return MockState("50.0")
        if entity_id == "sensor.wind":
            return MockState("10.0") # UTCI approx 32.9 (Strong Heat) from utils test
        return None
    
    mock_hass.states.get.side_effect = get_state_side_effect
    
    sensor._update_local_value()
    
    assert sensor.native_value is not None
    assert isinstance(sensor.native_value, str)
    assert sensor.available is True

def test_literal_sensor_local_update_missing(mock_hass, mock_coordinator, mock_entry):
    sensor = MeteocatUTCILiteralSensor(mock_coordinator, mock_entry, "Test Local Literal")
    sensor.hass = mock_hass
    sensor.async_write_ha_state = MagicMock()
    
    mock_hass.states.get.return_value = None
    
    sensor._update_local_value()
    
    assert sensor.native_value is None
    assert sensor.available is False
    assert sensor.icon == "mdi:help-circle-outline"
