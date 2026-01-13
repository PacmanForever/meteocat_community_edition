"""Test _is_night logic in MeteocatWeather."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import pytz

from homeassistant.util import dt as dt_util
from custom_components.meteocat_community_edition.weather import MeteocatWeather
from custom_components.meteocat_community_edition.const import CONF_STATION_NAME, CONF_STATION_CODE

async def test_is_night_external_station(hass):
    """Test is_night uses station coordinates for External Station."""
    coordinator = MagicMock()
    # Mock coordinator data with station metadata
    coordinator.data = {
        "station": {
            "coordenades": {
                "latitud": 41.38, # Barcelona
                "longitud": 2.17
            }
        }
    }
    
    entry = MagicMock()
    entry.data = {
        CONF_STATION_NAME: "Bcn",
        CONF_STATION_CODE: "X1",
    }
    entry.options = {}
    entry.entry_id = "123"
    
    weather = MeteocatWeather(coordinator, entry)
    weather.hass = hass
    
    # Mock current time to be Night in Barcelona
    # Winter night: Jan 1st 2026. 22:00 UTC is definitely night everywhere in Europe
    now = datetime(2026, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
    
    with patch("homeassistant.util.dt.now", return_value=now):
        # Ensure fallback is NOT called
        with patch("homeassistant.helpers.sun.get_astral_event_date") as mock_ha_sun:
            is_night = weather._is_night()
            assert is_night is True
            mock_ha_sun.assert_not_called()

async def test_is_night_fallback(hass):
    """Test is_night falls back to HA location when no coordinates."""
    coordinator = MagicMock()
    coordinator.data = {} # No metadata
    
    entry = MagicMock()
    entry.data = {
        CONF_STATION_NAME: "Unknown",
        CONF_STATION_CODE: "X2",
    }
    entry.options = {}
    entry.entry_id = "456"
    
    weather = MeteocatWeather(coordinator, entry)
    weather.hass = hass
    
    # Mock HA based sun check needs to return valid datetimes to succeed
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=pytz.UTC) # Noon
    
    with patch("homeassistant.util.dt.now", return_value=now):
        with patch("homeassistant.helpers.sun.get_astral_event_date") as mock_global_sun:
             # We return sunset/sunrise such that it IS day
             mock_global_sun.side_effect = [
                 datetime(2026, 1, 1, 18, 0, 0, tzinfo=pytz.UTC), # Sunset
                 datetime(2026, 1, 1, 6, 0, 0, tzinfo=pytz.UTC)   # Sunrise
             ]
             
             is_night = weather._is_night()
             
             assert is_night is False
             assert mock_global_sun.call_count >= 2

async def test_is_night_local_municipality(hass):
    """Test is_night uses municipality coordinates from config entry."""
    coordinator = MagicMock()
    coordinator.data = {}
    
    entry = MagicMock()
    entry.data = {
        CONF_STATION_NAME: "Local",
        CONF_STATION_CODE: "LOC",
        "municipality_lat": 41.38,
        "municipality_lon": 2.17
    }
    entry.options = {}
    entry.entry_id = "789"
    
    weather = MeteocatWeather(coordinator, entry)
    weather.hass = hass
    
    # Noon
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
    
    with patch("homeassistant.util.dt.now", return_value=now):
        with patch("homeassistant.helpers.sun.get_astral_event_date") as mock_ha_sun:
            is_night = weather._is_night()
            assert is_night is False # Should be day
            mock_ha_sun.assert_not_called()
