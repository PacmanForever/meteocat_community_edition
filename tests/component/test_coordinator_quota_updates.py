"""Tests for quota update logic in coordinator."""
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from homeassistant.util import dt as dt_util

from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator, MeteocatAuthError
from custom_components.meteocat_community_edition.const import (
    MODE_EXTERNAL,
    MODE_LOCAL,
)

# Patch device_registry globally for all tests in this file
@pytest.fixture(autouse=True)
def patch_device_registry():
    """Patch device_registry for tests that call _async_update_data."""
    mock_device = MagicMock()
    mock_device.id = "test_device_id"
    
    with patch('custom_components.meteocat_community_edition.coordinator.dr.async_get') as mock_dr:
        mock_registry = MagicMock()
        mock_registry.async_get_device.return_value = mock_device
        mock_dr.return_value = mock_registry
        yield

@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.bus = MagicMock()
    hass.bus.fire = MagicMock()
    return hass

@pytest.fixture
def mock_api():
    """Create a mock API client."""
    api = MagicMock()
    api.get_station_measurements = AsyncMock(return_value=[
        {
            "codi": "YM",
            "variables": [{"codi": 32, "lectures": [{"valor": 15.5}]}]
        }
    ])
    api.get_stations = AsyncMock(return_value=[
        {"codi": "YM", "nom": "Granollers", "coordenades": {"latitud": 41.6, "longitud": 2.3}}
    ])
    api.get_municipal_forecast = AsyncMock(return_value={
        "dies": [{"data": "2025-01-07", "variables": {"tmin": 5, "tmax": 15}}]
    })
    api.get_hourly_forecast = AsyncMock(return_value={})
    api.find_municipality_for_station = AsyncMock(return_value="081131")
    api.get_quotes = AsyncMock(return_value={
        "client": {"nom": "Test"}, 
        "plans": [{"nom": "p1", "consultesRestants": 100}]
    })
    return api

@pytest.fixture
def mock_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.data = {
        "api_key": "test_api_key",
        "mode": MODE_EXTERNAL,
        "station_code": "YM",
        # intentionally leaving out station_data to force get_stations if needed, 
        # but for these tests we might want to avoid it to simplify.
        # But coordinator calls get_stations if not present.
    }
    entry.options = {}
    return entry

@pytest.mark.asyncio
async def test_quotes_updated_when_fetching_measurements(mock_hass, mock_api, mock_entry):
    """Test that quotes are fetched when measurements are fetched, even if forecast is not."""
    coordinator = MeteocatCoordinator(mock_hass, mock_entry)
    coordinator.api = mock_api
    
    # Pre-load data with existing quotes
    coordinator.data = {
        "forecast": {"existing": "data"},
        "quotes": {"plans": [{"nom": "p1", "consultesRestants": 999}]}
    }
    
    # Configure to fetch measurements BUT skip forecast
    coordinator._force_measurements = True
    coordinator._force_forecast = False
    
    # Avoid first refresh logic
    coordinator._is_first_refresh = False
    
    # Execute update
    with patch.object(coordinator, '_should_fetch_forecast', return_value=False):
        await coordinator._async_update_data()
    
    # Verify get_quotes was called
    mock_api.get_quotes.assert_called()

@pytest.mark.asyncio
async def test_quotes_updated_when_fetching_forecast(mock_hass, mock_api, mock_entry):
    """Test that quotes are fetched when forecast is fetched."""
    coordinator = MeteocatCoordinator(mock_hass, mock_entry)
    coordinator.api = mock_api
    
    # Pre-load data with existing quotes
    coordinator.data = {
        "forecast": {"existing": "data"},
        "quotes": {"plans": [{"nom": "p1", "consultesRestants": 999}]}
    }
    
    # Configure to fetch forecast BUT skip measurements (e.g. manual forecast refresh)
    coordinator._force_measurements = False
    coordinator._force_forecast = True
    
    # Execute update
    await coordinator._async_update_data()
    
    # Verify get_quotes was called
    mock_api.get_quotes.assert_called()

@pytest.mark.asyncio
async def test_quotes_not_fetched_on_retry(mock_hass, mock_api, mock_entry):
    """Test that quotes are NOT fetched during a retry to verify existing logic is preserved."""
    coordinator = MeteocatCoordinator(mock_hass, mock_entry)
    coordinator.api = mock_api
    
    # Simulate Retry Mode
    coordinator._is_retry_update = True
    
    # Execute update
    await coordinator._async_update_data()
    
    # Verify get_quotes was NOT called
    mock_api.get_quotes.assert_not_called()
