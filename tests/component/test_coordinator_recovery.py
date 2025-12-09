"""Test coordinator recovery from failures."""
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_STATION_CODE,
    CONF_MODE,
    MODE_EXTERNAL,
)
from custom_components.meteocat_community_edition.coordinator import MeteocatLegacyCoordinator

@pytest.fixture
def mock_api():
    """Mock the MeteocatAPI."""
    api = AsyncMock()
    api.get_station_measurements.return_value = {
        "temperature": 20,
        "humidity": 50,
    }
    api.get_municipal_forecast.return_value = {
        "days": []
    }
    api.get_hourly_forecast.return_value = {
        "hours": []
    }
    api.get_quotes.return_value = {
        "plans": [
            {"nom": "Quota", "consultesRestants": 100, "maxConsultes": 1000}
        ]
    }
    api.find_municipality_for_station.return_value = "080193"
    api.get_stations.return_value = [{"codi": "X4", "nom": "Barcelona"}]
    return api

async def test_coordinator_recovery_from_failure(hass: HomeAssistant, mock_api):
    """Test that coordinator recovers from initial failure and populates data."""
    
    entry = MagicMock()
    entry.data = {
        CONF_API_KEY: "test_key",
        CONF_STATION_CODE: "X4",
        CONF_MODE: MODE_EXTERNAL,
    }
    entry.options = {}
    entry.entry_id = "test_entry"
    
    # Mock config_entries.async_update_entry
    hass.config_entries = MagicMock()
    hass.config_entries.async_update_entry = MagicMock()
    
    coordinator = MeteocatLegacyCoordinator(hass, entry)
    coordinator.api = mock_api
    
    # 1. Simulate first update failure (Network Error)
    # We simulate what happens when _async_update_data catches an error
    # It sets data to None/partial and logs warning if first refresh
    
    # Mock api to raise error
    mock_api.get_station_measurements.side_effect = Exception("Network Error")
    mock_api.get_quotes.side_effect = Exception("Network Error")
    
    # Mock time to be 10:00 (not an update time)
    with patch("homeassistant.util.dt.now", return_value=datetime(2025, 12, 9, 10, 0, 0, tzinfo=dt_util.UTC)):
        # Run first refresh
        # Note: async_config_entry_first_refresh calls _async_refresh
        # We call _async_update_data directly to simulate the internal logic
        
        # But wait, _async_update_data catches exceptions from gather tasks
        # So it returns data with Nones
        
        data = await coordinator._async_update_data()
        
        assert data["measurements"] is None
        assert data["quotes"] is None
        assert coordinator._is_first_refresh is False # It should be set to False even if partial failure?
        # Wait, looking at code:
        # if missing_data:
        #   if _is_first_refresh: warning
        #   else: raise UpdateFailed
        # self._is_first_refresh = False
        
        # So if missing_data is true (it is), and it's first refresh:
        # It logs warning.
        # It sets _is_first_refresh = False.
        # It returns data.
        
        assert coordinator.last_update_success is True # Because it didn't raise
        
        # 2. Simulate Manual Update (Success)
        mock_api.get_station_measurements.side_effect = None
        mock_api.get_quotes.side_effect = None
        
        # Force manual update (not update hour)
        # _should_fetch_forecast should return False because forecast is present (it succeeded in first run)
        
        # Verify data has forecast (it succeeded in first run)
        assert data.get("forecast") is not None
        
        # Set coordinator.data to the result of first run
        coordinator.async_set_updated_data(data)
        
        # Run update again
        data2 = await coordinator._async_update_data()
        
        # Verify quotes are fetched (even though forecast wasn't fetched)
        assert data2["quotes"] is not None
        assert data2["quotes"]["plans"][0]["consultesRestants"] == 100
        
        # Verify forecast is NOT fetched (because it was present)
        # We can check if get_municipal_forecast was called again
        # It was called once in first run. Should not be called in second run.
        assert mock_api.get_municipal_forecast.call_count == 1
        
        assert mock_api.get_quotes.call_count == 2 # Called in first run (failed) and second run (success)
