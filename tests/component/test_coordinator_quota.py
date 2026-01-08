"""Tests for coordinator quota handling."""
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
import pytest
from aiohttp import ClientError
from homeassistant.exceptions import ConfigEntryAuthFailed
from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator, MeteocatAPIError

@pytest.fixture
def mock_api():
    api = AsyncMock()
    return api

@pytest.fixture
def mock_entry():
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "api_key": "test_key",
        "mode": "external",
        "station_code": "X4",
        "is_forecast_daily": True,
        "is_forecast_hourly": True
    }
    entry.options = {}
    return entry

@pytest.mark.asyncio
async def test_coordinator_handles_quota_exceeded_with_previous_data(hass, mock_entry, mock_api):
    """Test handling of 429 error when previous quotes exist."""
    coordinator = MeteocatCoordinator(hass, mock_entry)
    coordinator.api = mock_api
    
    # Setup previous data
    coordinator.data = {
        "quotes": {
            "client": {"nom": "Test"},
            "plans": [{"nom": "Plan 1", "consultesRestants": 100}]
        }
    }
    
    # Mock API to raise 429
    mock_api.get_quotes.side_effect = MeteocatAPIError("429 Rate limit exceeded")
    mock_api.get_station_measurements.return_value = {}
    mock_api.get_municipal_forecast.return_value = {}
    
    # Trigger update and capture result
    result = await coordinator._async_update_data()
    
    # Check that quotes were updated to 0 remaining in the result
    assert result["quotes"]["plans"][0]["consultesRestants"] == 0

@pytest.mark.asyncio
async def test_coordinator_handles_quota_exceeded_without_previous_data(hass, mock_entry, mock_api):
    """Test handling of 429 error without previous data."""
    coordinator = MeteocatCoordinator(hass, mock_entry)
    coordinator.api = mock_api
    
    coordinator.data = {}
    
    # Mock API to raise 429
    mock_api.get_quotes.side_effect = MeteocatAPIError("429 Rate limit exceeded")
    
    result = await coordinator._async_update_data()
    
    assert result.get("quotes") is None

@pytest.mark.asyncio
async def test_coordinator_handles_generic_api_error_fetching_quotes(hass, mock_entry, mock_api):
    """Test handling of generic API error fetching quotes."""
    coordinator = MeteocatCoordinator(hass, mock_entry)
    coordinator.api = mock_api
    
    mock_api.get_quotes.side_effect = Exception("Generic error")
    
    result = await coordinator._async_update_data()
    
    assert result.get("quotes") is None

@pytest.mark.asyncio
async def test_coordinator_handles_non_429_api_error_fetching_quotes(hass, mock_entry, mock_api):
    """Test handling of non-429 API error fetching quotes."""
    coordinator = MeteocatCoordinator(hass, mock_entry)
    coordinator.api = mock_api
    
    mock_api.get_quotes.side_effect = MeteocatAPIError("500 Server Error")
    
    result = await coordinator._async_update_data()
    
    assert result.get("quotes") is None

@pytest.mark.asyncio
async def test_coordinator_fires_events(mock_entry, mock_api):
    """Test that events are fired after update."""
    from homeassistant.core import HomeAssistant
    
    # Create a mock HASS
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    hass.bus = MagicMock()
    
    coordinator = MeteocatCoordinator(hass, mock_entry)
    coordinator.api = mock_api
    
    # Mock async_get_clientsession since coordinator uses it in __init__? 
    # Actually coordinator init uses async_get_clientsession(hass).
    # Since hass is a mock, async_get_clientsession(hass) might fail if it expects real hass.
    # But wait, coordinator.__init__ calls:
    # session = async_get_clientsession(hass)
    # self.api = MeteocatAPI(..., session, ...)
    # But here I am passing mock_api, so session is not used if I overwrite coordinator.api?
    # BUT coordinator.__init__ runs BEFORE I overwrite coordinator.api.
    
    # So I need to patch async_get_clientsession
    with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"), \
         patch("custom_components.meteocat_community_edition.coordinator.dt_util") as mock_dt:
        
        coordinator = MeteocatCoordinator(hass, mock_entry)
        coordinator.api = mock_api
        
        now = datetime(2025, 1, 1, 12, 0, 0)
        mock_dt.now.return_value = now
        mock_dt.utcnow.return_value = now
        mock_dt.as_utc.side_effect = lambda x: x
        
        # Setup mock device registry
        mock_dr = MagicMock()
        mock_device = MagicMock()
        mock_device.id = "test_device_id"
        mock_dr.async_get_device.return_value = mock_device
        
        with patch("homeassistant.helpers.device_registry.async_get", return_value=mock_dr):
             await coordinator._async_update_data()
             
             # Verify event was fired
             assert hass.bus.fire.call_count >= 1
             args = hass.bus.fire.call_args[0]
             assert args[0] == "meteocat_community_edition_data_updated"
             assert args[1]["device_id"] == "test_device_id"
