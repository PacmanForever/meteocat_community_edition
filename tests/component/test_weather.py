"""Tests for Meteocat weather entity."""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from homeassistant.components.weather import WeatherEntityFeature
from homeassistant.const import SUN_EVENT_SUNSET, SUN_EVENT_SUNRISE

from custom_components.meteocat_community_edition.weather import MeteocatWeather, MeteocatLocalWeather
from custom_components.meteocat_community_edition.const import DOMAIN, MODE_EXTERNAL, MODE_LOCAL


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
        "mode": MODE_EXTERNAL,
        "station_code": "YM",
        "station_name": "Granollers",
        "enable_forecast_daily": True,
        "enable_forecast_hourly": True,
    }
    return entry


@pytest.fixture
def mock_local_entry():
    """Create a mock config entry for local mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_local_weather"
    entry.data = {
        "mode": MODE_LOCAL,
        "municipality_name": "Barcelona",
        "municipality_lat": 41.3851,
        "municipality_lon": 2.1734,
        "enable_forecast_daily": True,
        "enable_forecast_hourly": False,
        "local_condition_entity": "weather.home_weather_station",
        "mapping_type": "meteocat",
    }
    return entry


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.config.latitude = 41.3851
    hass.config.longitude = 2.1734
    hass.states.get.return_value = MagicMock(state="sunny")
    return hass


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
    # 5.5 m/s * 3.6 = 19.8 km/h
    assert wind_speed == 19.8


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
    # Enable hourly forecast in config
    mock_entry.data["enable_forecast_hourly"] = True
    
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
    assert weather.native_wind_speed_unit == UnitOfSpeed.KILOMETERS_PER_HOUR


def test_weather_entity_attribution(mock_coordinator, mock_entry):
    """Test that weather entity has attribution."""
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    assert weather.attribution == "Estació Granollers (externa) + Predicció Meteocat"


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


def test_weather_entity_native_temperature_error_handling(mock_coordinator, mock_entry):
    """Test native_temperature error handling."""
    # Test invalid valor type
    mock_coordinator.data = {
        "measurements": [
            {
                "variables": [
                    {"codi": 32, "lectures": [{"valor": "invalid", "data": "2025-11-24T12:00:00Z"}]},
                ]
            }
        ]
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    assert weather.native_temperature is None


def test_weather_entity_native_pressure_error_cases(mock_coordinator, mock_entry):
    """Test native_pressure error cases."""
    # Test measurements not list
    mock_coordinator.data = {"measurements": "not_a_list"}
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    assert weather.native_pressure is None
    
    # Test empty measurements list
    mock_coordinator.data = {"measurements": []}
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    assert weather.native_pressure is None


def test_weather_entity_wind_bearing_error_cases(mock_coordinator, mock_entry):
    """Test wind_bearing error cases."""
    # Test measurements not list
    mock_coordinator.data = {"measurements": "not_a_list"}
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    assert weather.wind_bearing is None
    
    # Test empty measurements list
    mock_coordinator.data = {"measurements": []}
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    assert weather.wind_bearing is None


def test_weather_entity_condition_error_cases(mock_coordinator, mock_entry):
    """Test condition property error cases."""
    # Test missing measurements
    mock_coordinator.data = {}
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    assert weather.condition is None
    
    # Test measurements not list
    mock_coordinator.data = {"measurements": "not_a_list"}
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    assert weather.condition is None
    
    # Test empty measurements
    mock_coordinator.data = {"measurements": []}
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    assert weather.condition is None


def test_weather_entity_condition_local_mode(mock_coordinator, mock_entry):
    """Test condition property in local mode (forecast fallback)."""
    # Set up local mode data with proper forecast structure
    mock_coordinator.data = {
        "measurements": [],  # No measurements
        "forecast": {
            "dies": [
                {
                    "data": "2025-11-24",
                    "variables": {
                        "estatCel": {"valor": 1},  # Sunny
                    }
                }
            ]
        }
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    # Set mode to local by modifying the entry data
    mock_entry.data["mode"] = MODE_LOCAL
    condition = weather.condition
    assert condition == "sunny"


def test_weather_entity_condition_local_mode_missing_forecast(mock_coordinator, mock_entry):
    """Test condition property when forecast is missing."""
    mock_coordinator.data = {
        "measurements": [],  # No measurements
        "forecast": None
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    assert weather.condition is None


def test_weather_entity_condition_local_mode_empty_forecast(mock_coordinator, mock_entry):
    """Test condition property when forecast has no days."""
    mock_coordinator.data = {
        "measurements": [],  # No measurements
        "forecast": {"dies": []}
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    assert weather.condition is None


def test_weather_entity_is_night_error_handling(mock_coordinator, mock_entry, mock_hass):
    """Test _is_night method error handling."""
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    weather.hass = mock_hass
    
    # Test with exception in sun calculation
    with patch('homeassistant.helpers.sun.get_astral_event_date', side_effect=Exception("Sun error")):
        result = weather._is_night()
        assert result is False


@pytest.mark.asyncio
async def test_weather_entity_async_forecast_hourly_missing_data(mock_coordinator, mock_entry):
    """Test async_forecast_hourly with missing data."""
    mock_coordinator.data = {}
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    result = await weather.async_forecast_hourly()
    assert result is None


@pytest.mark.asyncio
async def test_weather_entity_async_forecast_hourly_error_handling(mock_coordinator, mock_entry):
    """Test async_forecast_hourly error handling."""
    # Test with invalid temperature data - proper structure
    mock_coordinator.data = {
        "forecast_hourly": {
            "dies": [
                {
                    "data": "2025-11-24",
                    "variables": {
                        "temperatura": {"valors": [
                            {"data": "2025-11-24T10:00:00", "valor": "invalid"},
                            {"data": "2025-11-24T11:00:00", "valor": 16}
                        ]},  # Invalid first value
                        "estatCel": {"valors": [
                            {"data": "2025-11-24T10:00:00", "valor": 1},
                            {"data": "2025-11-24T11:00:00", "valor": 2}
                        ]},
                        "precipitacio": {"valors": [
                            {"data": "2025-11-24T10:00:00", "valor": 0},
                            {"data": "2025-11-24T11:00:00", "valor": 1}
                        ]},
                    }
                }
            ]
        }
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    result = await weather.async_forecast_hourly()
    assert result is not None
    assert len(result) > 0


@pytest.mark.asyncio
async def test_weather_entity_async_forecast_daily_missing_data(mock_coordinator, mock_entry):
    """Test async_forecast_daily with missing data."""
    mock_coordinator.data = {}
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    result = await weather.async_forecast_daily()
    assert result is None


@pytest.mark.asyncio
async def test_weather_entity_async_forecast_daily_error_handling(mock_coordinator, mock_entry):
    """Test async_forecast_daily error handling."""
    # Test with invalid temperature data
    mock_coordinator.data = {
        "forecast": {
            "dies": [
                {
                    "data": "2025-11-24",
                    "variables": {
                        "tmin": {"valor": "invalid"},
                        "tmax": {"valor": 20},
                        "estatCel": {"valor": 1},
                        "probPrecip": {"valor": 10},
                    }
                }
            ]
        }
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    result = await weather.async_forecast_daily()
    assert result is not None
    assert len(result) == 1


def test_local_weather_entity_initialization(mock_coordinator, mock_local_entry, mock_hass):
    """Test local weather entity initialization."""
    with patch('homeassistant.helpers.event.async_track_state_change_event'):
        weather = MeteocatLocalWeather(mock_coordinator, mock_local_entry)
        weather.hass = mock_hass
        
        assert weather.name == "Barcelona"
        assert weather.unique_id == "test_entry_local_weather_weather_local"
        assert weather.entity_id == "weather.barcelona_local"


def test_local_weather_condition_from_entity(mock_coordinator, mock_local_entry, mock_hass):
    """Test local weather condition from configured entity."""
    with patch('homeassistant.helpers.event.async_track_state_change_event'):
        weather = MeteocatLocalWeather(mock_coordinator, mock_local_entry)
        weather.hass = mock_hass
        
        with patch.object(weather, '_is_night', return_value=False):
            condition = weather.condition
            assert condition == "sunny"


def test_local_weather_condition_from_forecast(mock_coordinator, mock_local_entry, mock_hass):
    """Test local weather condition from forecast."""
    # Mock unavailable entity state
    mock_hass.states.get.return_value = MagicMock(state="unavailable")
    
    # Set up forecast data
    mock_coordinator.data = {
        "forecast": {
            "dies": [
                {
                    "data": "2025-11-24",
                    "variables": {
                        "estatCel": {"valor": 1},  # Sunny
                    }
                }
            ]
        }
    }
    
    with patch('homeassistant.helpers.event.async_track_state_change_event'):
        weather = MeteocatLocalWeather(mock_coordinator, mock_local_entry)
        weather.hass = mock_hass
        
        # Mock no rain sensor
        with patch.object(weather, '_get_sensor_value', return_value=None), \
             patch.object(weather, '_is_night', return_value=False):
            condition = weather.condition
            assert condition == "sunny"


def test_local_weather_condition_night_mode(mock_coordinator, mock_local_entry, mock_hass):
    """Test local weather condition converts sunny to clear-night."""
    # Mock unavailable entity state
    mock_hass.states.get.return_value = MagicMock(state="unavailable")
    
    # Set up forecast data with sunny
    mock_coordinator.data = {
        "forecast": {
            "dies": [
                {
                    "data": "2025-11-24",
                    "variables": {
                        "estatCel": {"valor": 1},  # Sunny
                    }
                }
            ]
        }
    }
    
    with patch('homeassistant.helpers.event.async_track_state_change_event'):
        weather = MeteocatLocalWeather(mock_coordinator, mock_local_entry)
        weather.hass = mock_hass
        
        # Mock no rain sensor and night time
        with patch.object(weather, '_get_sensor_value', return_value=None), \
             patch.object(weather, '_is_night', return_value=True):
            condition = weather.condition
            assert condition == "clear-night"


def test_local_weather_native_pressure_from_sensor(mock_coordinator, mock_local_entry, mock_hass):
    """Test local weather gets pressure from sensor."""
    with patch('homeassistant.helpers.event.async_track_state_change_event'):
        weather = MeteocatLocalWeather(mock_coordinator, mock_local_entry)
        weather.hass = mock_hass
        
        with patch.object(weather, '_get_sensor_value', return_value=1013.25):
            pressure = weather.native_pressure
            assert pressure == 1013.25


def test_local_weather_is_night_calculations(mock_coordinator, mock_local_entry, mock_hass):
    """Test _is_night method calls sun helper correctly (when no coords available)."""
    
    # Remove coordinates to force fallback to HA location
    mock_local_entry.data.pop("municipality_lat", None)
    mock_local_entry.data.pop("municipality_lon", None)

    with patch('homeassistant.helpers.event.async_track_state_change_event'):
        weather = MeteocatLocalWeather(mock_coordinator, mock_local_entry)
        weather.hass = mock_hass
        
        # Should use hass.config coordinates implied by signature (hass, event, date)
        with patch('homeassistant.helpers.sun.get_astral_event_date') as mock_get_event:
            mock_get_event.return_value = None  # Simulate missing sun data
            result = weather._is_night()
            assert result is False
            
            # Verify it was called with strictly 3 arguments: hass, event, date
            # And called twice (sunset, sunrise)
            assert mock_get_event.call_count == 2
            
            # Check calls
            # We don't know exact date (today), so we check arguments structure
            # args[0] are positional args
            
            args0 = mock_get_event.call_args_list[0]
            args1 = mock_get_event.call_args_list[1]
            
            # Assert call 1 (Sunset)
            assert args0[0][0] == mock_hass
            assert args0[0][1] == SUN_EVENT_SUNSET
            assert len(args0[0]) == 3 # Ensure no extra args like lat/lon passed
            
            # Assert call 2 (Sunrise)
            assert args1[0][0] == mock_hass
            assert args1[0][1] == SUN_EVENT_SUNRISE
            assert len(args1[0]) == 3


def test_weather_entity_is_night_calculations(mock_coordinator, mock_entry, mock_hass):
    """Test _is_night method calls sun helper correctly for regular weather entity."""
    
    # Setup coordinates in the mock data (which would previously trigger the lat/lon path)
    # We remove them to force fallback
    mock_coordinator.data = {
        "station": {
            "coordenades": {}  # Empty coordinates
        },
        "measurements": [
            {
                "variables": []
            }
        ]
    }

    weather = MeteocatWeather(mock_coordinator, mock_entry)
    weather.hass = mock_hass
    
    # Should use hass.config coordinates implied by signature (hass, event, date)
    # The fix removed usage of custom coordinates
    with patch('homeassistant.helpers.sun.get_astral_event_date') as mock_get_event:
        mock_get_event.return_value = None  # Simulate missing sun data
        result = weather._is_night()
        assert result is False
        
        # Verify it was called with strictly 3 arguments: hass, event, date
        assert mock_get_event.call_count == 2
        
        args0 = mock_get_event.call_args_list[0]
        args1 = mock_get_event.call_args_list[1]
        
        # Assert call 1 (Sunset)
        assert args0[0][0] == mock_hass
        assert args0[0][1] == SUN_EVENT_SUNSET
        assert len(args0[0]) == 3 # Ensure lat/lon were NOT passed
        
        # Assert call 2 (Sunrise)
        assert args1[0][0] == mock_hass
        assert args1[0][1] == SUN_EVENT_SUNRISE
        assert len(args1[0]) == 3

