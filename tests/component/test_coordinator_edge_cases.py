"""Extended tests for coordinator coverage."""
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util

from custom_components.meteocat_community_edition.api import MeteocatAPI, MeteocatAPIError, MeteocatAuthError
from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    CONF_MODE,
    CONF_API_KEY,
    MODE_EXTERNAL,
    CONF_STATION_CODE,
    CONF_STATION_NAME,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
)
from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
from pytest_homeassistant_custom_component.common import MockConfigEntry

@pytest.fixture
def mock_api():
    """Mock the API."""
    api = MagicMock(spec=MeteocatAPI)
    api.get_station_measurements = AsyncMock(return_value=[{"variables": []}])
    api.get_municipal_forecast = AsyncMock(return_value={"dies": []})
    api.get_hourly_forecast = AsyncMock(return_value={"dies": []})
    api.get_quotes = AsyncMock(return_value={"client": {}, "plans": []})
    return api

async def test_coordinator_init_missing_key(hass: HomeAssistant):
    """Test coordinator initialization with missing API key raises error."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_MODE: MODE_EXTERNAL} # Missing API Key
    )
    with pytest.raises(ValueError, match="missing API key"):
        MeteocatCoordinator(hass, entry)

async def test_coordinator_init_options_none(hass: HomeAssistant):
    """Test coordinator initialization handles None options (using MagicMock to bypass immutable check)."""
    # Use MagicMock because MockConfigEntry prevents direct attribute assignment
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.title = "Test Entry"
    entry.data = {
        CONF_MODE: MODE_EXTERNAL,
        CONF_API_KEY: "test_key"
    }
    entry.options = None
    
    coordinator = MeteocatCoordinator(hass, entry)
    assert coordinator.entry.options == {}

async def test_coordinator_429_quota_exceeded(hass: HomeAssistant, mock_api):
    """Test handling of 429 error during quotes fetch."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_EXTERNAL,
            CONF_API_KEY: "test_key",
            CONF_STATION_CODE: "X4"
        }
    )
    coordinator = MeteocatCoordinator(hass, entry)
    coordinator.api = mock_api
    
    # Setup previous quotes
    coordinator.data = {
        "quotes": {
            "client": {"nom": "Test"},
            "plans": [{"nom": "p1", "consultesRestants": 100}]
        }
    }
    
    # Mock quota error
    mock_api.get_quotes.side_effect = MeteocatAPIError("Rate limit exceeded 429")
    
    # Run update
    new_data = await coordinator._async_update_data()
    
    # Check that remaining requests are effectively zeroed out
    assert new_data["quotes"]["plans"][0]["consultesRestants"] == 0

async def test_coordinator_generic_quote_error(hass: HomeAssistant, mock_api):
    """Test generic error during quotes fetch preserves old quotes."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_EXTERNAL,
            CONF_API_KEY: "test_key",
            CONF_STATION_CODE: "X4"
        }
    )
    coordinator = MeteocatCoordinator(hass, entry)
    coordinator.api = mock_api
    
    old_quotes = {"foo": "bar"}
    coordinator.data = {"quotes": old_quotes}
    
    mock_api.get_quotes.side_effect = Exception("Generic error")
    
    new_data = await coordinator._async_update_data()
    
    assert new_data["quotes"] == old_quotes

async def test_schedule_next_update_failure(hass: HomeAssistant):
    """Test _schedule_next_update fails gracefully if no times valid."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_EXTERNAL,
            CONF_API_KEY: "test_key",
            # Invalid or past times theoretically handled, but let's try to simulate failure logic
        }
    )
    coordinator = MeteocatCoordinator(hass, entry)
    
    # Mock mode to something that uses update times logic but fails? 
    # Actually, EXTERNAL uses hardcoded +1 hour. LOCAL uses update times.
    coordinator.mode = "MODE_LOCAL" 
    coordinator.update_time_1 = ""
    coordinator.update_time_2 = ""
    coordinator.update_time_3 = ""
    
    with patch("custom_components.meteocat_community_edition.coordinator._LOGGER") as mock_logger:
        coordinator._schedule_next_update()
        mock_logger.warning.assert_called_with("Could not calculate next update time. Automatic updates disabled.")
        assert coordinator.next_scheduled_update is None

async def test_coordinator_partial_fetch_errors(hass: HomeAssistant, mock_api):
    """Test partial fetch errors are logged but don't crash if retry not needed."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_EXTERNAL,
            CONF_API_KEY: "test_key",
            CONF_STATION_CODE: "X4"
        }
    )
    coordinator = MeteocatCoordinator(hass, entry)
    coordinator.api = mock_api
    
    # measurements fail with non-retryable error
    mock_api.get_station_measurements.side_effect = MeteocatAPIError("400 Bad Request")
    
    # forecast succeeds
    mock_api.get_municipal_forecast.return_value = {"dies": []}
    
    # This should raise UpdateFailed because measurements are critical
    # Ensure it's not first refresh, otherwise it just logs warning
    coordinator._is_first_refresh = False
    with pytest.raises(UpdateFailed, match="Missing critical data: measurements"):
        await coordinator._async_update_data()
        
    # Verify data state (on local data because call failed)
    # Actually, the method raises exception, so return value is lost. 
    # But inside the exception block, if we were checking side effects...
    # The coordinator.data is NOT updated if exception is raised.
    pass

