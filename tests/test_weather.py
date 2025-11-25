"""Tests for Meteocat weather entity."""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, AsyncMock

from homeassistant.components.weather import WeatherEntityFeature

from custom_components.meteocat_community_edition.weather import MeteocatWeather
from custom_components.meteocat_community_edition.const import DOMAIN, MODE_ESTACIO


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator with weather data."""
    coordinator = MagicMock()
    coordinator.data = {
        "measurements": [
            {
                "codi": "YM",
                "nom": "Granollers",
                "coordenades": {"latitud": 41.6, "longitud": 2.3},
                "variables": [
                    {"codi": 32, "nom": "Temperatura", "lectures": [{"valor": 18.5, "data": "2025-11-24T12:00:00Z"}]},
                    {"codi": 33, "nom": "Humitat", "lectures": [{"valor": 65.0, "data": "2025-11-24T12:00:00Z"}]},
                    {"codi": 34, "nom": "Pressio", "lectures": [{"valor": 1013.25, "data": "2025-11-24T12:00:00Z"}]},
                    {"codi": 30, "nom": "Vel. vent", "lectures": [{"valor": 5.5, "data": "2025-11-24T12:00:00Z"}]},
                    {"codi": 31, "nom": "Dir. vent", "lectures": [{"valor": 180.0, "data": "2025-11-24T12:00:00Z"}]},
                ],
            }
        ],
        "forecast": {
            "dies": [
                {
                    "data": "2025-11-24",
                    "variables": {
                        "tmax": {"valor": 22},
                        "tmin": {"valor": 12},
                        "estat": {"codi": 1},  # Sunny
                    }
                },
                {
                    "data": "2025-11-25",
                    "variables": {
                        "tmax": {"valor": 20},
                        "tmin": {"valor": 11},
                        "estat": {"codi": 2},  # Partly cloudy
                    }
                },
            ]
        },
        "forecast_hourly": {
            "dies": [
                {
                    "data": "2025-11-24",
                    "variables": {
                        "temp": {"valors": [15, 16, 17, 18, 19, 20]},
                        "estat": {"valors": [{"codi": 1}, {"codi": 1}, {"codi": 2}, {"codi": 2}, {"codi": 3}, {"codi": 3}]},
                    }
                }
            ]
        }
    }
    return coordinator


@pytest.fixture
def mock_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_weather"
    entry.data = {
        "mode": MODE_ESTACIO,
        "station_code": "YM",
        "station_name": "Granollers",
    }
    return entry


def test_weather_entity_initialization(mock_coordinator, mock_entry):
    """Test weather entity initialization."""
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    # Check name
    assert weather.name == "Granollers"
    
    # Check unique_id
    assert weather.unique_id == "test_entry_weather_weather"
    
    # Check entity_id includes station code
    assert weather.entity_id == "weather.granollers_ym"
    
    # Check device_info
    assert weather._attr_device_info["name"] == "Granollers YM"
    assert (DOMAIN, "test_entry_weather") in weather._attr_device_info["identifiers"]
    assert weather._attr_device_info["manufacturer"] == "Meteocat Edició Comunitària"


def test_weather_entity_native_temperature(mock_coordinator, mock_entry):
    """Test native_temperature property."""
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    temperature = weather.native_temperature
    assert temperature == 18.5


def test_weather_entity_humidity(mock_coordinator, mock_entry):
    """Test humidity property."""
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    humidity = weather.humidity
    assert humidity == 65.0


def test_weather_entity_native_pressure(mock_coordinator, mock_entry):
    """Test native_pressure property."""
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    pressure = weather.native_pressure
    assert pressure == 1013.25


def test_weather_entity_native_wind_speed(mock_coordinator, mock_entry):
    """Test native_wind_speed property."""
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    wind_speed = weather.native_wind_speed
    assert wind_speed == 5.5


def test_weather_entity_wind_bearing(mock_coordinator, mock_entry):
    """Test wind_bearing property."""
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    wind_bearing = weather.wind_bearing
    assert wind_bearing == 180.0


def test_weather_entity_missing_measurements(mock_coordinator, mock_entry):
    """Test that entity handles missing measurements gracefully."""
    mock_coordinator.data = {}
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    assert weather.native_temperature is None
    assert weather.humidity is None
    assert weather.native_pressure is None
    assert weather.native_wind_speed is None
    assert weather.wind_bearing is None


def test_weather_entity_empty_measurements(mock_coordinator, mock_entry):
    """Test that entity handles empty measurements list."""
    mock_coordinator.data = {"measurements": []}
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    assert weather.native_temperature is None


def test_weather_entity_missing_variable(mock_coordinator, mock_entry):
    """Test that entity handles missing specific variable."""
    mock_coordinator.data = {
        "measurements": [
            {
                "variables": [
                    # Temperature is missing
                    {"codi": 33, "nom": "Humitat", "lectures": [{"valor": 65.0}]},
                ]
            }
        ]
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    assert weather.native_temperature is None
    assert weather.humidity == 65.0


def test_weather_entity_supported_features(mock_coordinator, mock_entry):
    """Test that weather entity supports forecast features."""
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    assert weather.supported_features & WeatherEntityFeature.FORECAST_DAILY
    assert weather.supported_features & WeatherEntityFeature.FORECAST_HOURLY


def test_weather_entity_units(mock_coordinator, mock_entry):
    """Test that weather entity has correct units."""
    from homeassistant.const import (
        UnitOfPrecipitationDepth,
        UnitOfPressure,
        UnitOfSpeed,
        UnitOfTemperature,
    )
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    assert weather.native_precipitation_unit == UnitOfPrecipitationDepth.MILLIMETERS
    assert weather.native_pressure_unit == UnitOfPressure.HPA
    assert weather.native_temperature_unit == UnitOfTemperature.CELSIUS
    assert weather.native_wind_speed_unit == UnitOfSpeed.METERS_PER_SECOND


def test_weather_entity_attribution(mock_coordinator, mock_entry):
    """Test that weather entity has attribution."""
    from custom_components.meteocat_community_edition.const import ATTRIBUTION
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    assert weather.attribution == ATTRIBUTION


def test_weather_entity_handles_none_measurements(mock_coordinator, mock_entry):
    """Test that entity handles None measurements."""
    mock_coordinator.data = {"measurements": None}
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    assert weather.native_temperature is None


def test_weather_entity_empty_lectures(mock_coordinator, mock_entry):
    """Test that entity handles variables with empty lectures."""
    mock_coordinator.data = {
        "measurements": [
            {
                "variables": [
                    {"codi": 32, "lectures": []},  # Empty lectures
                ]
            }
        ]
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    assert weather.native_temperature is None


def test_weather_entity_multiple_lectures_uses_last(mock_coordinator, mock_entry):
    """Test that entity uses last lecture when multiple are present."""
    mock_coordinator.data = {
        "measurements": [
            {
                "variables": [
                    {
                        "codi": 32,
                        "lectures": [
                            {"valor": 15.0, "data": "2025-11-24T10:00:00Z"},
                            {"valor": 16.0, "data": "2025-11-24T11:00:00Z"},
                            {"valor": 17.5, "data": "2025-11-24T12:00:00Z"},
                        ]
                    },
                ]
            }
        ]
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    # Should use last lecture
    assert weather.native_temperature == 17.5
