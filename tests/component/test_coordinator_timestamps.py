"""Tests for last update timestamp logic."""
import sys
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from homeassistant.util import dt as dt_util

from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
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
            "variables": [
                {"codi": 32, "lectures": [{"valor": 15.5}]},
            ]
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
    api.get_quotes = AsyncMock(return_value={})
    return api


@pytest.fixture
def mock_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.data = {
        "api_key": "test_api_key",
        "mode": MODE_EXTERNAL,
        "station_code": "YM",
        # intentionally leaving out station_data to trigger get_stations call
    }
    entry.options = {}
    return entry


@pytest.mark.asyncio
async def test_last_measurements_update_only_on_measurements_fetch(mock_hass, mock_api, mock_entry):
    """Test that last_measurements_update only updates when measurements are fetched."""
    coordinator = MeteocatCoordinator(mock_hass, mock_entry)
    coordinator.api = mock_api
    
    # Pre-populate data to pass critical fields check
    coordinator.data = {
        "forecast": {"dummy": "data"},
        "quotes": {"plans": []}
    }
    
    # 1. Simulate Fetch Measurements ONLY (e.g. forced via button)
    coordinator._force_measurements = True
    coordinator._force_forecast = False
    
    # Mock time
    now = datetime(2025, 1, 7, 12, 0, 0)
    with patch("homeassistant.util.dt.utcnow", return_value=now),          patch("homeassistant.util.dt.now", return_value=now):
        await coordinator._async_update_data()
        
    assert coordinator.last_measurements_update == now
    assert coordinator.last_forecast_update is None
    
    # 2. Simulate Fetch Forecast ONLY (e.g. forced via button)
    coordinator._force_measurements = False
    coordinator._force_forecast = True
    
    later = datetime(2025, 1, 7, 13, 0, 0)
    with patch("homeassistant.util.dt.utcnow", return_value=later),          patch("homeassistant.util.dt.now", return_value=later):
        await coordinator._async_update_data()
    
    # Measurements update time should NOT have changed
    assert coordinator.last_measurements_update == now
    # Forecast update time should be the new time
    assert coordinator.last_forecast_update == later


@pytest.mark.asyncio
async def test_last_measurements_update_skipped_on_forecast_only(mock_hass, mock_api, mock_entry):
    """Test standard update loop where forecast might be skipped."""
    coordinator = MeteocatCoordinator(mock_hass, mock_entry)
    coordinator.api = mock_api
    coordinator._is_first_refresh = False  # Skip first refresh logic
    
    # Pre-populate data so that skipping forecast doesn't raise error
    coordinator.data = {
        "forecast": {"dummy": "data"},
        "quotes": {"plans": []}
    }
    
    # Setup: Measurements fetched, Forecast skipped (default external behavior if hour matches)
    # We need to simulate _should_fetch_forecast return False
    with patch.object(coordinator, '_should_fetch_forecast', return_value=False):
        now = datetime(2025, 1, 7, 12, 0, 0)
        with patch("homeassistant.util.dt.utcnow", return_value=now),              patch("homeassistant.util.dt.now", return_value=now):
            await coordinator._async_update_data()
            
        assert coordinator.last_measurements_update == now
        assert coordinator.last_forecast_update is None
        
    # Setup: Measurements fetched + Forecast fetched
    with patch.object(coordinator, '_should_fetch_forecast', return_value=True):
        later = datetime(2025, 1, 7, 13, 0, 0)
        with patch("homeassistant.util.dt.utcnow", return_value=later),              patch("homeassistant.util.dt.now", return_value=later):
            await coordinator._async_update_data()
            
        assert coordinator.last_measurements_update == later
        assert coordinator.last_forecast_update == later
