"""Tests for Meteocat Local weather entity updates."""
import pytest
from unittest.mock import MagicMock, patch, ANY
from homeassistant.core import HomeAssistant
from custom_components.meteocat_community_edition.weather import MeteocatLocalWeather
from custom_components.meteocat_community_edition.const import (
    CONF_SENSOR_TEMPERATURE,
    CONF_MUNICIPALITY_NAME,
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
                        "estatCel": {"valor": 1},
                    }
                }
            ]
        }
    }
    return coordinator

async def test_local_weather_subscribes_to_sensors(hass: HomeAssistant, mock_coordinator):
    """Test that the entity subscribes to sensor updates."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_MUNICIPALITY_NAME: "Test City",
        CONF_SENSOR_TEMPERATURE: "sensor.test_temp",
    }
    
    weather = MeteocatLocalWeather(mock_coordinator, entry)
    weather.hass = hass
    weather.entity_id = "weather.test_local"
    
    # Mock async_track_state_change_event
    with patch("homeassistant.helpers.event.async_track_state_change_event") as mock_track, \
         patch("custom_components.meteocat_community_edition.weather.async_track_sunrise"), \
         patch("custom_components.meteocat_community_edition.weather.async_track_sunset"):
        # We need to mock super().async_added_to_hass() behavior or just let it run if it's safe
        # Since SingleCoordinatorWeatherEntity.async_added_to_hass calls super which is CoordinatorEntity...
        # It might try to connect to coordinator.
        
        # Let's just mock the import inside the method if possible, or patch the module
        with patch("custom_components.meteocat_community_edition.weather.SingleCoordinatorWeatherEntity.async_added_to_hass"):
            await weather.async_added_to_hass()
            
            # Verify it was called with the correct sensor
            # Note: The list order might vary if we had multiple sensors, but here we have one
            args, _ = mock_track.call_args
            assert args[0] == hass
            assert "sensor.test_temp" in args[1]
