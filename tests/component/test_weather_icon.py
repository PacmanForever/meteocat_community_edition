"""Tests for Meteocat weather icon logic."""
from unittest.mock import MagicMock, patch
import pytest
from custom_components.meteocat_community_edition.weather import MeteocatWeather
from custom_components.meteocat_community_edition.const import MODE_EXTERNAL

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
                    # Sky state (codi 35) = 2 (Partly cloudy)
                    {"codi": 35, "nom": "Estat cel", "lectures": [{"valor": 2, "data": "2025-11-24T12:00:00Z"}]},
                ],
            }
        ],
        "station": {
            "coordenades": {"latitud": 41.6, "longitud": 2.3}
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
    }
    return entry

def test_weather_icon_partlycloudy_day(mock_coordinator, mock_entry):
    """Test icon is None (default) for partly cloudy during day."""
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    with patch.object(MeteocatWeather, '_is_night', return_value=False):
        assert weather.condition == "partlycloudy"
        assert weather.icon is None

def test_weather_icon_sunny_night(mock_coordinator, mock_entry):
    """Test condition becomes clear-night for sunny during night."""
    # Change to sunny (1)
    mock_coordinator.data["measurements"][0]["variables"][0]["lectures"][0]["valor"] = 1
    weather = MeteocatWeather(mock_coordinator, mock_entry)
    
    with patch.object(MeteocatWeather, '_is_night', return_value=True):
        assert weather.condition == "clear-night"
        # Icon should be None (default for clear-night is correct)
        assert weather.icon is None
