"""Tests for unknown condition fallback logic."""
import sys
import os
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from custom_components.meteocat_community_edition.weather import MeteocatWeather
from custom_components.meteocat_community_edition.sensor import MeteocatForecastSensor
from custom_components.meteocat_community_edition.const import MODE_EXTERNAL

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

def test_weather_condition_fallback_exceptional(mock_coordinator, mock_entry):
    """Test that weather entity falls back to 'exceptional' for unknown codes."""
    # Setup data with an unknown condition code 999
    mock_coordinator.data = {
        "measurements": [
            {
                "variables": [
                    {
                        "codi": 35, # Estat del cel
                        "lectures": [{"valor": 999, "data": "2025-01-01T12:00:00Z"}]
                    }
                ]
            }
        ]
    }
    
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    # Before the change this would be "cloudy"
    # Now it should be "exceptional"
    assert weather.condition == "exceptional"

def test_sensor_forecast_fallback_exceptional(mock_coordinator, mock_entry):
    """Test that forecast sensor falls back to 'exceptional' for unknown codes."""
    # Setup forecast data with unknown code
    mock_coordinator.data = {
        "forecast_hourly": {
            "dies": [
                {
                    "variables": {
                        "estatCel": {
                            "valors": [
                                {"valor": 999, "data": "2025-01-01T12:00Z"}
                            ]
                        }
                    }
                }
            ]
        }
    }
    
    sensor = MeteocatForecastSensor(mock_coordinator, mock_entry, "Forecast", "hourly", "YM")
    
    # We need to simulate the property access which involves parsing the forecast
    # The sensor's native_value is usually the condition count, but we want to check attributes
    
    # Actually, MeteocatForecastSensor exposes attributes.forecast via the property `extra_state_attributes`
    # However, for the sensor, let's look at how it parses.
    
    # Wait, the sensor in `sensor.py` (line 680 approx) builds the forecast list.
    # Let's verify _get_forecast_hourly returns 'exceptional' in the condition field.
    
    forecasts = sensor._get_forecast_hourly()
    assert len(forecasts) > 0
    item = forecasts[0]
    
    assert item["condition"] == "exceptional"

@pytest.mark.asyncio
async def test_weather_forecast_fallback_exceptional_async(mock_coordinator, mock_entry):
    mock_coordinator.data = {
        "forecast_hourly": {
            "dies": [
                {
                    "variables": {
                        "estatCel": {
                            "valors": [
                                {"valor": 999, "data": "2025-01-01T12:00Z"}
                            ]
                        }
                    }
                }
            ]
        }
    }
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    forecasts = await weather.async_forecast_hourly()
    
    assert len(forecasts) > 0
    assert forecasts[0]["condition"] == "exceptional"
