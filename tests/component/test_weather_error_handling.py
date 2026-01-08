"""Test weather entity error handling to improve coverage."""
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import pytest
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    CONF_MODE,
    MODE_EXTERNAL,
    CONF_STATION_CODE,
    CONF_STATION_NAME,
    CONF_ENABLE_FORECAST_DAILY,
    CONF_ENABLE_FORECAST_HOURLY,
)
from custom_components.meteocat_community_edition.weather import MeteocatWeather
from pytest_homeassistant_custom_component.common import MockConfigEntry

@pytest.fixture
def mock_coordinator():
    """Mock the coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "measurements": [],
        "forecast": {},
        "forecast_hourly": {},
        "station": {
            "coordenades": {
                "latitud": 41.3851,
                "longitud": 2.1734
            }
        }
    }
    return coordinator

@pytest.fixture
def mock_entry():
    """Mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_EXTERNAL,
            CONF_STATION_CODE: "X4",
            CONF_STATION_NAME: "Barcelona - Raval",
            CONF_ENABLE_FORECAST_DAILY: True,
            CONF_ENABLE_FORECAST_HOURLY: True,
        }
    )

async def test_weather_malformed_measurements(hass: HomeAssistant, mock_coordinator, mock_entry):
    """Test weather entity handles malformed measurements gracefully."""
    entity = MeteocatWeather(mock_coordinator, mock_entry)
    entity.hass = hass

    # Test malformed wind speed
    mock_coordinator.data["measurements"] = [{
        "variables": [
            {
                "codi": 30,  # Wind Speed
                "lectures": [{"valor": "invalid"}]
            }
        ]
    }]
    assert entity.native_wind_speed is None

    # Test malformed temperature
    mock_coordinator.data["measurements"] = [{
        "variables": [
            {
                "codi": 32,  # Temp
                "lectures": [{"valor": "invalid"}]
            }
        ]
    }]
    assert entity.native_temperature is None

    # Test malformed humidity
    mock_coordinator.data["measurements"] = [{
        "variables": [
            {
                "codi": 33,  # Humidity
                "lectures": [{"valor": "not_a_number"}]
            }
        ]
    }]
    assert entity.humidity is None

    # Test malformed pressure
    mock_coordinator.data["measurements"] = [{
        "variables": [
            {
                "codi": 34,  # Pressure
                "lectures": [{"valor": []}] # weird type
            }
        ]
    }]
    assert entity.native_pressure is None

    # Test malformed wind bearing
    mock_coordinator.data["measurements"] = [{
        "variables": [
            {
                "codi": 31,  # Wind Bearing
                "lectures": [{"valor": "N"}] # expecting number
            }
        ]
    }]
    assert entity.wind_bearing is None

async def test_weather_is_night_error(hass: HomeAssistant, mock_coordinator, mock_entry):
    """Test is_night handles calculation errors."""
    entity = MeteocatWeather(mock_coordinator, mock_entry)
    entity.hass = hass
    
    # Force an exception in get_astral_event_date
    mock_coordinator.data["station"] = {"coordenades": {"latitud": 41.0, "longitud": 2.0}}
    
    with patch("homeassistant.helpers.sun.get_astral_event_date", side_effect=Exception("Astral error")):
        assert entity._is_night() is False

async def test_forecast_malformed_data(hass: HomeAssistant, mock_coordinator, mock_entry):
    """Test forecast methods handle malformed data."""
    entity = MeteocatWeather(mock_coordinator, mock_entry)
    entity.hass = hass

    # Test malformed hourly forecast
    mock_coordinator.data["forecast_hourly"] = {
        "dies": [
            {
                "variables": {
                    "temp": {
                        "valors": [{"data": "2023-01-01T00:00Z", "valor": "bad_temp"}]
                    },
                    "precipitacio": {
                        "valors": [{"data": "2023-01-01T00:00Z", "valor": "bad_precip"}]
                    }
                }
            }
        ]
    }
    hourly = await entity.async_forecast_hourly()
    assert len(hourly) == 1
    # Should skip native_temperature and precipitation due to error, but include item
    assert "native_temperature" not in hourly[0]
    assert "native_precipitation" not in hourly[0]

    # Test malformed daily forecast
    mock_coordinator.data["forecast"] = {
        "dies": [
            {
                "data": "2023-01-01",
                "variables": {
                    "tmin": {"valor": "bad_min"},
                    "tmax": {"valor": "bad_max"},
                    "precipitacio": {"valor": "bad_prob"}
                }
            }
        ]
    }
    daily = await entity.async_forecast_daily()
    assert len(daily) == 1
    assert "native_templow" not in daily[0]
    assert "native_temperature" not in daily[0]
    assert "precipitation_probability" not in daily[0]

