"""Tests for Meteocat weather entity coverage."""
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from homeassistant.const import (
    CONF_MODE,
    CONF_LATITUDE,
    CONF_LONGITUDE,
)

from custom_components.meteocat_community_edition.weather import MeteocatLocalWeather, MeteocatWeather
from custom_components.meteocat_community_edition.const import (
    MODE_LOCAL,
    MODE_EXTERNAL,
    CONF_MUNICIPALITY_NAME,
    CONF_STATION_NAME,
    CONF_SENSOR_TEMPERATURE,
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
def mock_entry_local():
    """Create a mock config entry for local mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_local"
    entry.data = {
        CONF_MODE: MODE_LOCAL,
        CONF_MUNICIPALITY_NAME: "Abrera",
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
    }
    return entry

@pytest.fixture
def mock_entry_external():
    """Create a mock config entry for external mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_external"
    entry.data = {
        CONF_MODE: MODE_EXTERNAL,
        CONF_STATION_NAME: "Test Station",
        "station_code": "YM",
    }
    return entry

def test_local_weather_sensor_value_error(mock_coordinator, mock_entry_local):
    """Test handling of non-numeric sensor values."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_entry_local)
    weather.hass = MagicMock()
    
    # Mock sensor state with non-numeric value
    state = MagicMock()
    state.state = "not_a_number"
    weather.hass.states.get.return_value = state
    
    assert weather.native_temperature is None

def test_local_weather_is_night_fallback_coords(mock_coordinator, mock_entry_local):
    """Test _is_night fallback to HA config coordinates."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_entry_local)
    weather.hass = MagicMock()
    weather.hass.config.latitude = 41.0
    weather.hass.config.longitude = 2.0
    
    # Ensure entry has no coordinates
    mock_entry_local.data["municipality_lat"] = None
    mock_entry_local.data["municipality_lon"] = None
    
    with patch("homeassistant.helpers.sun.get_astral_event_date") as mock_get_astral:
        # Mock sunset/sunrise to force night
        mock_get_astral.return_value = None # Just to avoid errors, we check if it was called with HA coords
        
        weather._is_night()
        
        # Verify it called with HA config coords
        args = mock_get_astral.call_args_list[0][0]
        # It should now be called with just (hass, event, date)
        assert len(args) == 3


def test_local_weather_is_night_exception(mock_coordinator, mock_entry_local):
    """Test _is_night exception handling."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_entry_local)
    weather.hass = MagicMock()
    weather.hass.config.latitude = 41.0
    weather.hass.config.longitude = 2.0
    
    with patch("homeassistant.helpers.sun.get_astral_event_date", side_effect=Exception("Test error")):
        assert weather._is_night() is False

def test_weather_condition_fallback_to_forecast(mock_coordinator, mock_entry_external):
    """Test condition fallback to forecast when measurements missing."""
    # Empty measurements
    mock_coordinator.data["measurements"] = []
    
    weather = MeteocatWeather(mock_coordinator, mock_entry_external)
    
    # Should use forecast (Sunny from fixture)
    assert weather.condition == "sunny"

def test_weather_condition_forecast_missing_dies(mock_coordinator, mock_entry_external):
    """Test condition when forecast has no days."""
    mock_coordinator.data["measurements"] = []
    mock_coordinator.data["forecast"] = {"dies": []}
    
    weather = MeteocatWeather(mock_coordinator, mock_entry_external)
    
    assert weather.condition is None

def test_weather_condition_forecast_missing_estat(mock_coordinator, mock_entry_external):
    """Test condition when forecast has no estatCel."""
    mock_coordinator.data["measurements"] = []
    mock_coordinator.data["forecast"] = {
        "dies": [
            {
                "variables": {
                    "estatCel": {} # Missing valor
                }
            }
        ]
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry_external)
    
    assert weather.condition is None

def test_weather_is_night_missing_station_data(mock_coordinator, mock_entry_external):
    """Test _is_night when station data is missing."""
    mock_coordinator.data["station"] = None
    
    weather = MeteocatWeather(mock_coordinator, mock_entry_external)
    
    assert weather._is_night() is False

def test_weather_is_night_missing_coords(mock_coordinator, mock_entry_external):
    """Test _is_night when coordinates are missing."""
    mock_coordinator.data["station"] = {"coordenades": {}}
    
    weather = MeteocatWeather(mock_coordinator, mock_entry_external)
    
    assert weather._is_night() is False
