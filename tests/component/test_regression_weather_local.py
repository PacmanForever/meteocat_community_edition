"""Tests for Meteocat Local weather entity regression."""
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from homeassistant.const import (
    CONF_MODE,
)

from custom_components.meteocat_community_edition.weather import MeteocatLocalWeather
from custom_components.meteocat_community_edition.const import (
    DOMAIN, 
    MODE_LOCAL,
    CONF_MUNICIPALITY_NAME,
    CONF_SENSOR_TEMPERATURE,
    CONF_SENSOR_HUMIDITY,
    CONF_SENSOR_PRESSURE,
    CONF_SENSOR_WIND_SPEED,
    CONF_SENSOR_WIND_BEARING,
    CONF_SENSOR_VISIBILITY,
    CONF_SENSOR_UV_INDEX,
)

@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "forecast": {
            "dies": [
                {
                    "data": "2025-11-24",
                    "variables": {
                        "tmax": {"valor": 22},
                        "tmin": {"valor": 12},
                        "estatCel": {"valor": 1},  # Sunny
                    }
                }
            ]
        }
    }
    return coordinator

@pytest.fixture
def mock_entry_with_lists():
    """Create a mock config entry with lists as sensor IDs (regression case)."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        CONF_MODE: MODE_LOCAL,
        CONF_MUNICIPALITY_NAME: "Barcelona",
        # Simulate the bug: values are lists instead of strings
        CONF_SENSOR_TEMPERATURE: ["sensor.temp_local"],
        CONF_SENSOR_HUMIDITY: ["sensor.humidity_local"],
        CONF_SENSOR_PRESSURE: ["sensor.pressure_local"],
        CONF_SENSOR_WIND_SPEED: ["sensor.wind_speed_local"],
        CONF_SENSOR_WIND_BEARING: ["sensor.wind_bearing_local"],
    }
    return entry

def test_local_weather_sensors_list_regression(mock_coordinator, mock_entry_with_lists):
    """Test that the entity handles list values for sensors correctly."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_entry_with_lists)
    weather.hass = MagicMock()
    
    # Mock state machine
    def get_state(entity_id):
        state = MagicMock()
        if entity_id == "sensor.temp_local":
            state.state = "20.5"
        elif entity_id == "sensor.humidity_local":
            state.state = "60"
        elif entity_id == "sensor.pressure_local":
            state.state = "1013"
        elif entity_id == "sensor.wind_speed_local":
            state.state = "10"
        elif entity_id == "sensor.wind_bearing_local":
            state.state = "180"
        else:
            return None
        return state
        
    weather.hass.states.get.side_effect = get_state
    
    # Verify that the entity correctly extracted the string from the list
    assert weather.native_temperature == 20.5
    assert weather.humidity == 60
    assert weather.native_pressure == 1013
    assert weather.native_wind_speed == 10
    assert weather.wind_bearing == 180
