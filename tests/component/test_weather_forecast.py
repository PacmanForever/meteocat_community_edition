"""Tests for Meteocat weather entity forecast and condition."""
import sys
import os
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from custom_components.meteocat_community_edition.weather import MeteocatWeather
from custom_components.meteocat_community_edition.const import MODE_ESTACIO, CONF_STATION_NAME, CONF_STATION_CODE

@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {}
    return coordinator

@pytest.fixture
def mock_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_STATION_NAME: "Test Station",
        CONF_STATION_CODE: "TS",
    }
    return entry

@pytest.mark.asyncio
async def test_async_forecast_hourly(mock_coordinator, mock_entry):
    """Test hourly forecast retrieval."""
    mock_coordinator.data = {
        "forecast_hourly": {
            "dies": [
                {
                    "data": "2025-12-08",
                    "variables": {
                        "temp": {"valors": [{"data": "2025-12-08T10:00Z", "valor": 10}, {"data": "2025-12-08T11:00Z", "valor": 11}]},
                        "estatCel": {"valors": [{"data": "2025-12-08T10:00Z", "valor": 1}, {"data": "2025-12-08T11:00Z", "valor": 2}]},
                        "precipitacio": {"valors": [{"data": "2025-12-08T10:00Z", "valor": 0.0}, {"data": "2025-12-08T11:00Z", "valor": 0.5}]},
                    }
                }
            ]
        }
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    forecast = await weather.async_forecast_hourly()
    
    assert forecast is not None
    assert len(forecast) == 2
    # Sort by datetime to ensure order
    forecast.sort(key=lambda x: x["datetime"])
    
    assert forecast[0]["temperature"] == 10
    assert forecast[0]["condition"] == "sunny"
    assert forecast[1]["temperature"] == 11
    assert forecast[1]["condition"] == "partlycloudy"

@pytest.mark.asyncio
async def test_async_forecast_daily(mock_coordinator, mock_entry):
    """Test daily forecast retrieval."""
    mock_coordinator.data = {
        "forecast": {
            "dies": [
                {
                    "data": "2025-12-08",
                    "variables": {
                        "tmax": {"valor": 15},
                        "tmin": {"valor": 5},
                        "estatCel": {"valor": 1},
                        "precipitacio": {"valor": 0.0},
                    }
                }
            ]
        }
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    forecast = await weather.async_forecast_daily()
    
    assert forecast is not None
    assert len(forecast) == 1
    assert forecast[0]["temperature"] == 15
    assert forecast[0]["templow"] == 5
    assert forecast[0]["condition"] == "sunny"

def test_condition_from_measurements(mock_coordinator, mock_entry):
    """Test condition from measurements."""
    mock_coordinator.data = {
        "measurements": [
            {
                "variables": [
                    {"codi": 32, "lectures": [{"valor": 1}]} # Sunny
                ]
            }
        ]
    }
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    assert weather.condition == "sunny"

def test_condition_from_forecast_fallback(mock_coordinator, mock_entry):
    """Test condition fallback to forecast if measurements missing."""
    mock_coordinator.data = {
        "measurements": [],
        "forecast": {
            "dies": [
                {
                    "variables": {
                        "estatCel": {"valor": 2} # Partly cloudy
                    }
                }
            ]
        }
    }
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    assert weather.condition == "partlycloudy"

def test_is_night(mock_coordinator, mock_entry):
    """Test is_night logic."""
    mock_coordinator.data = {
        "station": {
            "coordenades": {"latitud": 41.0, "longitud": 2.0}
        }
    }
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    weather.hass = MagicMock()
    
    # Mock sun helper
    with patch("homeassistant.helpers.sun.get_astral_event_date") as mock_get_astral:
        # Simulate day
        mock_get_astral.side_effect = [
            datetime(2025, 12, 8, 18, 0, 0), # Sunset
            datetime(2025, 12, 8, 6, 0, 0)   # Sunrise
        ]
        with patch("homeassistant.util.dt.now", return_value=datetime(2025, 12, 8, 12, 0, 0)):
            assert weather._is_night() is False
            
        # Simulate night
        mock_get_astral.side_effect = [
            datetime(2025, 12, 8, 18, 0, 0), # Sunset
            datetime(2025, 12, 8, 6, 0, 0)   # Sunrise
        ]
        with patch("homeassistant.util.dt.now", return_value=datetime(2025, 12, 8, 20, 0, 0)):
            assert weather._is_night() is True
