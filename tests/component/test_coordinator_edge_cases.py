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
    MODE_LOCAL,
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
    """Test coordinator initialization handles None options without mutating the entry."""
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
    assert coordinator.entry.options is None
    assert coordinator.update_time_1 == "06:00"
    assert coordinator.update_time_2 == "14:00"
    assert coordinator.update_time_3 == ""

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


async def test_coordinator_uses_station_municipality_code_for_external_mode(hass: HomeAssistant):
    """External mode should derive municipality_code from station_municipality_code when needed."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_EXTERNAL,
            CONF_API_KEY: "test_key",
            CONF_STATION_CODE: "X4",
            "station_municipality_code": "08123",
        },
    )

    coordinator = MeteocatCoordinator(hass, entry)

    assert coordinator.municipality_code == "08123"


async def test_coordinator_none_forecast_flags_use_defaults(hass: HomeAssistant):
    """None forecast flags should be normalized to defaults."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_API_KEY: "test_key",
            "municipality_code": "08123",
            "enable_forecast_daily": None,
            "enable_forecast_hourly": None,
        },
        options={},
    )

    coordinator = MeteocatCoordinator(hass, entry)

    assert coordinator.enable_forecast_daily is True
    assert coordinator.enable_forecast_hourly is False


def test_get_next_scheduled_time_rolls_to_tomorrow(hass: HomeAssistant):
    """Next scheduled time should roll over to tomorrow after the last update slot."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_API_KEY: "test_key",
            "municipality_code": "08123",
            CONF_UPDATE_TIME_1: "06:00",
            CONF_UPDATE_TIME_2: "14:00",
        },
        options={"update_time_3": "20:00"},
    )
    coordinator = MeteocatCoordinator(hass, entry)
    now = dt_util.as_local(datetime(2025, 11, 24, 22, 30, 0))

    next_time = coordinator._get_next_scheduled_time(now)

    assert next_time is not None
    assert next_time.date().isoformat() == "2025-11-25"
    assert next_time.hour == 6
    assert next_time.minute == 0


def test_should_fetch_forecast_ignores_invalid_time_strings(hass: HomeAssistant):
    """Invalid time strings should be ignored instead of breaking forecast scheduling."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_API_KEY: "test_key",
            "municipality_code": "08123",
            CONF_UPDATE_TIME_1: "bad-time",
            CONF_UPDATE_TIME_2: "14:00",
        },
    )
    coordinator = MeteocatCoordinator(hass, entry)
    coordinator._is_first_refresh = False
    coordinator.data = {"forecast": {"dies": []}}

    with patch("custom_components.meteocat_community_edition.coordinator.dt_util.now") as mock_now:
        mock_now.return_value = dt_util.as_local(datetime(2025, 11, 24, 9, 0, 0))
        assert coordinator._should_fetch_forecast() is False


def test_fire_events_handles_device_registry_errors():
    """Event firing should continue even if the device registry lookup fails."""
    hass = MagicMock()
    hass.bus = MagicMock()
    hass.bus.fire = MagicMock()
    entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="entry_fire_events",
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_API_KEY: "test_key",
            "municipality_code": "08123",
        },
    )
    coordinator = MeteocatCoordinator(hass, entry)
    coordinator._previous_next_update = None
    current_next_update = dt_util.as_local(datetime(2025, 11, 24, 14, 0, 0))

    with patch(
        "custom_components.meteocat_community_edition.coordinator.dr.async_get",
        side_effect=AttributeError("boom"),
    ):
        coordinator._fire_events(current_next_update)

    assert hass.bus.fire.call_count == 2

