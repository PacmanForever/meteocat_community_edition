"""Tests for Meteocat Local weather entity night condition."""
import pytest
from unittest.mock import MagicMock, patch
from homeassistant.core import HomeAssistant
from custom_components.meteocat_community_edition.weather import MeteocatLocalWeather
from custom_components.meteocat_community_edition.const import (
    CONF_MUNICIPALITY_NAME,
)

@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    # Mock forecast data returning "sunny" (code 1)
    coordinator.data = {
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
    return coordinator

async def test_local_weather_condition_night_mode(hass: HomeAssistant, mock_coordinator):
    """Test that sunny condition becomes clear-night when it is night."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_MUNICIPALITY_NAME: "Test City",
    }
    
    weather = MeteocatLocalWeather(mock_coordinator, entry)
    weather.hass = hass
    
    # Mock _is_night to return True
    with patch.object(MeteocatLocalWeather, "_is_night", return_value=True):
        # Should be clear-night instead of sunny
        assert weather.condition == "clear-night"

async def test_local_weather_condition_day_mode(hass: HomeAssistant, mock_coordinator):
    """Test that sunny condition stays sunny when it is day."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_MUNICIPALITY_NAME: "Test City",
    }
    
    weather = MeteocatLocalWeather(mock_coordinator, entry)
    weather.hass = hass
    
    # Mock _is_night to return False
    with patch.object(MeteocatLocalWeather, "_is_night", return_value=False):
        # Should stay sunny
        assert weather.condition == "sunny"
