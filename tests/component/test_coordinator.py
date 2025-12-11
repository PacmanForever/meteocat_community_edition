"""Tests for Meteocat coordinator."""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
from custom_components.meteocat_community_edition.const import (
    MODE_EXTERNAL, 
    MODE_LOCAL,
    CONF_ENABLE_FORECAST_HOURLY,
)


@pytest.fixture
def mock_api():
    """Create a mock API client."""
    api = MagicMock()
    api.get_stations = AsyncMock(return_value=[
        {"codi": "YM", "nom": "Granollers", "coordenades": {"latitud": 41.6, "longitud": 2.3}}
    ])
    api.get_station_measurements = AsyncMock(return_value=[
        {
            "codi": "YM",
            "variables": [
                {"codi": 32, "lectures": [{"valor": 15.5}]},
                {"codi": 35, "lectures": [{"valor": 1013.2}]},
            ]
        }
    ])
    api.get_municipal_forecast = AsyncMock(return_value={
        "dies": [
            {"data": "2025-11-24", "variables": {"tmax": 20, "tmin": 10}}
        ]
    })
    api.get_hourly_forecast = AsyncMock(return_value={
        "dies": [
            {"data": "2025-11-24", "variables": {"tmp": [15, 16, 17]}}
        ]
    })
    api.get_quotes = AsyncMock(return_value={
        "client": {"nom": "Test Client"},
        "plans": [
            {"nom": "Prediccio_100", "requests_left": 950}
        ]
    })
    api.find_municipality_for_station = AsyncMock(return_value="081131")
    return api


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.bus = MagicMock()
    hass.bus.async_fire = AsyncMock()
    return hass


@pytest.fixture
def mock_entry_xema():
    """Create a mock config entry for XEMA mode."""
    entry = MagicMock()
    entry.data = {
        "api_key": "test_api_key",
        "mode": MODE_EXTERNAL,
        "station_code": "YM",
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_entry_local():
    """Create a mock config entry for Municipal mode."""
    entry = MagicMock()
    entry.data = {
        "api_key": "test_api_key",
        "mode": MODE_LOCAL,
        "municipality_code": "081131",
        CONF_ENABLE_FORECAST_HOURLY: True,  # Enable hourly forecast for test
    }
    entry.options = {}
    return entry


@pytest.mark.asyncio
async def test_coordinator_xema_mode_update(mock_hass, mock_api, mock_entry_xema):
    """Test coordinator update in XEMA mode."""
    coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
    coordinator.api = mock_api
    
    data = await coordinator._async_update_data()
    
    assert data is not None
    assert "measurements" in data
    assert "forecast" in data
    assert "quotes" in data
    assert coordinator.last_successful_update_time is not None
    assert isinstance(coordinator.last_successful_update_time, datetime)


@pytest.mark.asyncio
async def test_coordinator_local_mode_update(mock_hass, mock_api, mock_entry_local):
    """Test coordinator update in Municipal mode."""
    coordinator = MeteocatCoordinator(mock_hass, mock_entry_local)
    coordinator.api = mock_api
    
    data = await coordinator._async_update_data()
    
    assert data is not None
    assert "forecast" in data
    assert "forecast_hourly" in data
    assert "quotes" in data
    # Municipal mode doesn't use station data - should be None
    assert data.get("station") is None


@pytest.mark.asyncio
async def test_coordinator_calculates_next_update(mock_hass, mock_api, mock_entry_xema):
    """Test that coordinator calculates next update interval."""
    coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
    coordinator.api = mock_api
    
    await coordinator._async_update_data()
    
    # update_interval is now None (polling disabled)
    # Updates are scheduled via _schedule_next_update()
    assert coordinator.update_interval is None
    # Verify last update time was recorded
    assert coordinator.last_successful_update_time is not None


@pytest.mark.asyncio
async def test_coordinator_handles_api_error(mock_hass, mock_api, mock_entry_xema):
    """Test coordinator handles API errors gracefully."""
    from custom_components.meteocat_community_edition.api import MeteocatAPIError
    
    mock_api.get_station_measurements.side_effect = MeteocatAPIError("API Error")
    
    coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
    coordinator.api = mock_api
    
    # First refresh tolerates missing data (quota exhausted scenario)
    data = await coordinator._async_update_data()
    assert coordinator._is_first_refresh is False
    
    # Second update should raise UpdateFailed when critical data fails
    with pytest.raises(Exception):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_quotes_fetched_after_other_apis(mock_hass, mock_api, mock_entry_xema):
    """Test that quotes are fetched after other API calls."""
    call_order = []
    
    async def track_get_station_measurements(*args, **kwargs):
        call_order.append("measurements")
        return [{"codi": "YM", "variables": []}]
    
    async def track_get_quotes(*args, **kwargs):
        call_order.append("quotes")
        return {"client": {"nom": "Test"}, "plans": []}
    
    mock_api.get_station_measurements = track_get_station_measurements
    mock_api.get_quotes = track_get_quotes
    
    coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
    coordinator.api = mock_api
    
    await coordinator._async_update_data()
    
    # Quotes should be called after measurements
    assert "measurements" in call_order
    assert "quotes" in call_order
    assert call_order.index("quotes") > call_order.index("measurements")


@pytest.mark.asyncio
async def test_coordinator_handles_missing_quotes(mock_hass, mock_api, mock_entry_xema):
    """Test coordinator handles missing quotes gracefully."""
    mock_api.get_quotes.side_effect = Exception("Quotes API error")
    
    coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
    coordinator.api = mock_api
    
    data = await coordinator._async_update_data()
    
    # Should still return data, but quotes should be None
    assert data is not None
    assert data["quotes"] is None


@pytest.mark.asyncio
async def test_coordinator_finds_municipality_for_station(mock_hass, mock_api, mock_entry_xema):
    """Test coordinator finds municipality code for station."""
    coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
    coordinator.api = mock_api
    
    await coordinator._async_update_data()
    
    assert coordinator.municipality_code == "081131"
    assert coordinator.station_data is not None
    assert coordinator.station_data["codi"] == "YM"


@pytest.mark.asyncio
async def test_coordinator_handles_quota_exceeded(mock_hass, mock_api, mock_entry_xema):
    """Test coordinator handles 429 Quota Exceeded error."""
    from custom_components.meteocat_community_edition.api import MeteocatAPIError
    
    # Setup initial state with valid quotes
    coordinator = MeteocatCoordinator(mock_hass, mock_entry_xema)
    coordinator.api = mock_api
    coordinator.data = {
        "quotes": {
            "client": {"nom": "Test Client"},
            "plans": [
                {"nom": "Prediccio_100", "consultesRestants": 100, "maxConsultes": 1000}
            ]
        }
    }
    
    # Mock API to raise 429 error
    mock_api.get_quotes.side_effect = MeteocatAPIError("Rate limit exceeded (429)")
    
    # Run update
    data = await coordinator._async_update_data()
    
    # Verify quotes are updated to 0
    assert data["quotes"] is not None
    assert data["quotes"]["plans"][0]["consultesRestants"] == 0
    assert data["quotes"]["plans"][0]["maxConsultes"] == 1000  # Should preserve other fields


@pytest.mark.asyncio
async def test_coordinator_empty_api_key(mock_hass, mock_api):
    """Test coordinator initialization with empty API key."""
    # Create entry with empty API key
    entry = MagicMock()
    entry.data = {
        "api_key": "",  # Empty API key
        "mode": MODE_EXTERNAL,
        "station_code": "YM",
        "update_times": ["08:00", "14:00", "20:00"],
        "enable_forecast_hourly": True,
        "enable_forecast_daily": True,
        "api_base_url": "https://api.meteo.cat",
    }
    entry.options = {}
    
    # Should raise ValueError for missing API key
    with pytest.raises(ValueError, match="is missing API key"):
        MeteocatCoordinator(mock_hass, entry)


@pytest.mark.asyncio
async def test_coordinator_none_api_key(mock_hass, mock_api):
    """Test coordinator initialization with None API key."""
    # Create entry with None API key
    entry = MagicMock()
    entry.data = {
        "api_key": None,  # None API key
        "mode": MODE_EXTERNAL,
        "station_code": "YM",
        "update_times": ["08:00", "14:00", "20:00"],
        "enable_forecast_hourly": True,
        "enable_forecast_daily": True,
        "api_base_url": "https://api.meteo.cat",
    }
    entry.options = {}
    
    # Should raise ValueError for missing API key
    with pytest.raises(ValueError, match="is missing API key"):
        MeteocatCoordinator(mock_hass, entry)


@pytest.mark.asyncio
async def test_coordinator_schedule_next_update_external_mode_midnight(mock_hass, mock_api):
    """Test _schedule_next_update for external mode around midnight."""
    entry = MagicMock()
    entry.data = {
        "api_key": "test_key",
        "mode": MODE_EXTERNAL,
        "station_code": "YM",
        "update_times": ["08:00", "14:00", "20:00"],
        "enable_forecast_hourly": True,
        "enable_forecast_daily": True,
        "api_base_url": "https://api.meteo.cat",
    }
    entry.options = {}
    
    coordinator = MeteocatCoordinator(mock_hass, entry)
    
    # Mock current time to be just after midnight (timezone-aware)
    with patch('homeassistant.util.dt.now') as mock_now:
        from homeassistant.util import dt as dt_util
        mock_now.return_value = dt_util.as_local(datetime(2025, 11, 24, 0, 5, 0))  # 00:05
        
        # Call schedule method
        coordinator._schedule_next_update()
        
        # Should have scheduled something
        assert coordinator._scheduled_update_remover is not None


@pytest.mark.asyncio
async def test_coordinator_schedule_next_update_local_mode(mock_hass, mock_api):
    """Test _schedule_next_update for local mode."""
    entry = MagicMock()
    entry.data = {
        "api_key": "test_key",
        "mode": MODE_LOCAL,
        "station_code": "08019",  # Barcelona municipality code
        "update_times": ["08:00", "14:00", "20:00"],
        "enable_forecast_hourly": False,
        "enable_forecast_daily": True,
        "api_base_url": "https://api.meteo.cat",
    }
    entry.options = {}
    
    coordinator = MeteocatCoordinator(mock_hass, entry)
    
    # Mock current time (timezone-aware)
    with patch('homeassistant.util.dt.now') as mock_now:
        from homeassistant.util import dt as dt_util
        mock_now.return_value = dt_util.as_local(datetime(2025, 11, 24, 10, 0, 0))  # 10:00
        
        # Call schedule method
        coordinator._schedule_next_update()
        
        # Should have scheduled something
        assert coordinator._scheduled_update_remover is not None


@pytest.mark.asyncio
async def test_coordinator_async_update_data_api_errors(mock_hass, mock_api):
    """Test _async_update_data with various API errors."""
    entry = MagicMock()
    entry.data = {
        "api_key": "test_key",
        "mode": MODE_EXTERNAL,
        "station_code": "YM",
        "update_times": ["08:00", "14:00", "20:00"],
        "enable_forecast_hourly": True,
        "enable_forecast_daily": True,
        "api_base_url": "https://api.meteo.cat",
    }
    entry.options = {}
    
    coordinator = MeteocatCoordinator(mock_hass, entry)
    coordinator.api = mock_api
    
    # Mock successful API calls to avoid actual network calls
    mock_api.get_stations = AsyncMock(return_value=[])
    mock_api.get_station_measurements = AsyncMock(return_value=[])
    mock_api.get_quotes = AsyncMock(return_value={"plans": []})
    
    # Test with get_station_measurements failing
    mock_api.get_station_measurements.side_effect = Exception("Network error")
    
    data = await coordinator._async_update_data()
    
    # Should return partial data with measurements as None
    assert data is not None
    assert "measurements" in data
    assert data["measurements"] is None


@pytest.mark.asyncio
async def test_coordinator_handles_forecast_disabled(mock_hass, mock_api):
    """Test coordinator when forecast features are disabled."""
    entry = MagicMock()
    entry.data = {
        "api_key": "test_key",
        "mode": MODE_EXTERNAL,
        "station_code": "YM",
        "update_times": ["08:00", "14:00", "20:00"],
        "enable_forecast_hourly": False,
        "enable_forecast_daily": False,
        "api_base_url": "https://api.meteo.cat",
    }
    entry.options = {}
    
    coordinator = MeteocatCoordinator(mock_hass, entry)
    coordinator.api = mock_api
    
    # Mock API calls to avoid actual network calls
    mock_api.get_stations = AsyncMock(return_value=[])
    mock_api.get_station_measurements = AsyncMock(return_value=[])
    mock_api.get_quotes = AsyncMock(return_value={"plans": []})
    
    data = await coordinator._async_update_data()
    
    # Should not call forecast APIs
    mock_api.get_municipal_forecast.assert_not_called()
    mock_api.get_hourly_forecast.assert_not_called()
    
    assert data is not None
