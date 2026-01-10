"""Test weather condition fallback to hourly forecast."""
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
import pytest
from custom_components.meteocat_community_edition.weather import MeteocatLocalWeather
from custom_components.meteocat_community_edition.const import CONF_STATION_NAME, CONF_STATION_CODE, MODE_LOCAL

@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.data = {}
    return coordinator

@pytest.fixture
def mock_entry():
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {}
    entry.options = {
        # Empty options to ensure no local sensors are configured
    }
    return entry

async def test_condition_from_hourly_forecast(mock_coordinator, mock_entry):
    """Test condition comes from hourly forecast when measurements are missing."""
    # Fixed time: 2023-01-01 12:00:00 UTC
    fixed_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    with patch("homeassistant.util.dt.utcnow", return_value=fixed_now):
        mock_coordinator.data = {
            "measurements": [], # No measurements
            "forecast_hourly": {
                "dies": [
                    {
                        "data": "2023-01-01",
                        "variables": {
                            "estatCel": {
                                "valors": [
                                    {
                                        "data": "2023-01-01T12:00Z", # Match current hour
                                        "valor": 1 # Sunny
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }
        
        weather = MeteocatLocalWeather(mock_coordinator, mock_entry)
        # Condition for code 1 is 'sunny'
        assert weather.condition == "sunny"

async def test_condition_from_hourly_forecast_exceptional(mock_coordinator, mock_entry):
    """Test condition comes from hourly forecast with unknown code."""
    # Fixed time: 2023-01-01 12:00:00 UTC
    fixed_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    with patch("homeassistant.util.dt.utcnow", return_value=fixed_now):
        mock_coordinator.data = {
            "measurements": [],
            "forecast_hourly": {
                "dies": [
                    {
                        "data": "2023-01-01",
                        "variables": {
                            "estatCel": {
                                "valors": [
                                    {
                                        "data": "2023-01-01T12:00Z",
                                        "valor": 999 # Unknown
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }
        
        weather = MeteocatLocalWeather(mock_coordinator, mock_entry)
        assert weather.condition == "exceptional"
