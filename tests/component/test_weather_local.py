"""Tests for Meteocat Local weather entity."""
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
    CONF_SENSOR_RAIN,
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
def mock_entry():
    """Create a mock config entry for local mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_local"
    entry.data = {
        CONF_MODE: MODE_LOCAL,
        CONF_MUNICIPALITY_NAME: "Abrera",
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
        CONF_SENSOR_PRESSURE: "sensor.pres",
        CONF_SENSOR_WIND_SPEED: "sensor.wind",
        CONF_SENSOR_WIND_BEARING: "sensor.bearing",
        CONF_SENSOR_RAIN: "sensor.rain_intensity",
        CONF_SENSOR_VISIBILITY: "sensor.visibility",
        CONF_SENSOR_UV_INDEX: "sensor.uv",
    }
    return entry

def test_local_weather_initialization(mock_coordinator, mock_entry):
    """Test local weather entity initialization."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_entry)
    
    assert weather.name == "Abrera"
    assert weather.unique_id == "test_entry_local_weather_local"
    assert weather.entity_id == "weather.abrera_local"
    
    assert weather.device_info["model"] == "Estació Local"
    assert weather.attribution == "Estació local + Predicció Meteocat"

def test_local_weather_sensors(mock_coordinator, mock_entry):
    def test_local_weather_ozone_extra_state(mock_coordinator, mock_entry):
        """Test that ozone is present in extra_state_attributes and is serializable."""
        weather = MeteocatLocalWeather(mock_coordinator, mock_entry)
        weather.hass = MagicMock()
        # Mock sensor states
        def get_state(entity_id):
            state = MagicMock()
            if entity_id == "sensor.ozone":
                state.state = "123.4"
            else:
                state.state = "0"
            return state
        # Patch _sensors to include ozone
        weather._sensors["ozone"] = "sensor.ozone"
        weather.hass.states.get.side_effect = get_state
        attrs = weather.extra_state_attributes
        assert "ozone" in attrs
        assert attrs["ozone"] == 123.4
        # Simulate JSON serialization (should not raise)
        import json
        try:
            json.dumps(attrs)
        except Exception as e:
            pytest.fail(f"ozone attribute not serializable: {e}")
    """Test reading from local sensors."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_entry)
    weather.hass = MagicMock()
    
    # Mock sensor states
    def get_state(entity_id):
        state = MagicMock()
        if entity_id == "sensor.temp":
            state.state = "20.5"
        elif entity_id == "sensor.hum":
            state.state = "60"
        elif entity_id == "sensor.pres":
            state.state = "1015"
        elif entity_id == "sensor.wind":
            state.state = "10"
        elif entity_id == "sensor.bearing":
            state.state = "180"
        elif entity_id == "sensor.rain_intensity":
            state.state = "0"
        elif entity_id == "sensor.visibility":
            state.state = "10000"
        elif entity_id == "sensor.uv":
            state.state = "5"
        else:
            return None
        return state
        
    weather.hass.states.get.side_effect = get_state
    
    assert weather.native_temperature == 20.5
    assert weather.humidity == 60
    assert weather.native_pressure == 1015
    assert weather.native_wind_speed == 10
    assert weather.wind_bearing == 180
    assert weather.native_precipitation == 0
    assert weather.native_visibility == 10000
    assert weather.uv_index == 5
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
def mock_entry():
    """Create a mock config entry for local mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_local"
    entry.data = {
        CONF_MODE: MODE_LOCAL,
        CONF_MUNICIPALITY_NAME: "Abrera",
        CONF_SENSOR_TEMPERATURE: "sensor.temp",
        CONF_SENSOR_HUMIDITY: "sensor.hum",
        CONF_SENSOR_PRESSURE: "sensor.pres",
        CONF_SENSOR_WIND_SPEED: "sensor.wind",
        CONF_SENSOR_WIND_BEARING: "sensor.bearing",
        CONF_SENSOR_RAIN: "sensor.rain_intensity",
    }
    return entry

def test_local_weather_initialization(mock_coordinator, mock_entry):
    """Test local weather entity initialization."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_entry)
    
    assert weather.name == "Abrera"
    assert weather.unique_id == "test_entry_local_weather_local"
    assert weather.entity_id == "weather.abrera_local"
    
    assert weather.device_info["model"] == "Estació Local"
    assert weather.attribution == "Estació local + Predicció Meteocat"

def test_local_weather_sensors(mock_coordinator, mock_entry):
    """Test reading from local sensors."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_entry)
    weather.hass = MagicMock()
    
    # Mock sensor states
    def get_state(entity_id):
        state = MagicMock()
        if entity_id == "sensor.temp":
            state.state = "20.5"
        elif entity_id == "sensor.hum":
            state.state = "60"
        elif entity_id == "sensor.pres":
            state.state = "1015"
        elif entity_id == "sensor.wind":
            state.state = "10"
        elif entity_id == "sensor.bearing":
            state.state = "180"
        elif entity_id == "sensor.rain_intensity":
            state.state = "0"
        else:
            return None
        return state
        
    weather.hass.states.get.side_effect = get_state
    
    assert weather.native_temperature == 20.5
    assert weather.humidity == 60.0
    assert weather.native_pressure == 1015.0
    assert weather.native_wind_speed == 10.0
    assert weather.wind_bearing == 180.0
    assert weather.native_precipitation == 0.0

def test_local_weather_condition_rain(mock_coordinator, mock_entry):
    """Test condition logic with rain sensor."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_entry)
    weather.hass = MagicMock()
    
    # Case 1: Rain sensor > 0 -> Should be rainy
    def get_state_raining(entity_id):
        state = MagicMock()
        if entity_id == "sensor.rain_intensity":
            state.state = "2.5"
        else:
            return None
        return state
        
    weather.hass.states.get.side_effect = get_state_raining
    assert weather.condition == "rainy"
    
    # Case 2: Rain sensor = 0 -> Should use forecast (Sunny)
    def get_state_not_raining(entity_id):
        state = MagicMock()
        if entity_id == "sensor.rain_intensity":
            state.state = "0"
        else:
            return None
        return state
        
    weather.hass.states.get.side_effect = get_state_not_raining
    # Mock _is_night to return False so sunny stays sunny
    with patch.object(weather, '_is_night', return_value=False):
        assert weather.condition == "sunny"

    # Case 3: Rain sensor unavailable -> Should use forecast
    def get_state_unavailable(entity_id):
        return None
        
    weather.hass.states.get.side_effect = get_state_unavailable
    with patch.object(weather, '_is_night', return_value=False):
        assert weather.condition == "sunny"


def test_local_weather_missing_sensors(mock_coordinator, mock_entry):
    """Test behavior when sensors are missing or unavailable."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_entry)
    weather.hass = MagicMock()
    
    # Mock sensor states returning None or unavailable
    def get_state(entity_id):
        if entity_id == "sensor.temp":
            state = MagicMock()
            state.state = "unavailable"
            return state
        return None
        
    weather.hass.states.get.side_effect = get_state
    
    assert weather.native_temperature is None
    assert weather.humidity is None  # Not in get_state, returns None

@pytest.mark.asyncio
async def test_local_weather_forecast(mock_coordinator, mock_entry):
    """Test forecast retrieval."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_entry)
    
    # Test daily forecast
    forecast = await weather.async_forecast_daily()
    assert forecast is not None
    assert len(forecast) == 1
    assert forecast[0]["datetime"] == "2025-11-24"
    assert forecast[0]["native_temperature"] == 22
    assert forecast[0]["native_templow"] == 12
    assert forecast[0]["condition"] == "sunny"

def test_local_weather_extra_state_attributes_all_sensors(mock_coordinator, mock_entry):
    """Test that all configured sensors are present in extra_state_attributes."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_entry)
    weather.hass = MagicMock()
    # Patch _sensors to include all possible keys
    weather._sensors = {
        "ozone": "sensor.ozone",
        "pressure": "sensor.pres",
        "wind_speed": "sensor.wind",
        "wind_bearing": "sensor.bearing",
        "wind_gust": "sensor.gust",
        "rain": "sensor.rain_intensity",
        "visibility": "sensor.visibility",
        "uv_index": "sensor.uv",
        "cloud_coverage": "sensor.cloud",
        "dew_point": "sensor.dew",
        "apparent_temp": "sensor.apparent",
    }
    # Mock sensor states
    def get_state(entity_id):
        state = MagicMock()
        state.state = "42"
        return state
    weather.hass.states.get.side_effect = get_state
    attrs = weather.extra_state_attributes
    expected_keys = [
        "ozone", "pressure", "wind_speed", "wind_bearing", "wind_gust", "rain", "visibility", "uv_index", "cloud_coverage", "dew_point", "apparent_temperature"
    ]
    for key in expected_keys:
        assert key in attrs
        assert attrs[key] == 42.0
