"""Tests for station data persistence across HA restarts."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
from custom_components.meteocat_community_edition.const import (
    CONF_API_KEY,
    CONF_MODE,
    CONF_STATION_CODE,
    MODE_ESTACIO,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    hass.config_entries = MagicMock()
    hass.config_entries.async_update_entry = MagicMock()
    return hass


@pytest.fixture
def mock_entry_without_station_data():
    """Create a mock config entry without cached station data."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_API_KEY: "test_key",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_entry_with_station_data():
    """Create a mock config entry with cached station data."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_API_KEY: "test_key",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
        "_station_data": {
            "codi": "YM",
            "nom": "Barcelona",
            "altitud": 95,
            "coordenades": {
                "latitud": 41.3851,
                "longitud": 2.1734,
            }
        }
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_api():
    """Create a mock API client."""
    api = MagicMock()
    api.get_stations = AsyncMock(return_value=[
        {
            "codi": "YM",
            "nom": "Barcelona",
            "altitud": 95,
            "coordenades": {
                "latitud": 41.3851,
                "longitud": 2.1734,
            }
        }
    ])
    api.get_station_measurements = AsyncMock(return_value=[
        {"codi": "YM", "variables": [{"codi": 32, "lectures": [{"valor": 15.5}]}]}
    ])
    api.find_municipality_for_station = AsyncMock(return_value="081131")
    api.get_municipal_forecast = AsyncMock(return_value={
        "dies": [{"data": "2025-11-26", "variables": {"tmax": 20}}]
    })
    api.get_hourly_forecast = AsyncMock(return_value={
        "dies": [{"data": "2025-11-26", "variables": {"tmp": [15]}}]
    })
    api.get_uv_index = AsyncMock(return_value={
        "ine": "081131", "uvi": [{"date": "2025-11-26", "hours": [{"hour": 12, "uvi": 5}]}]
    })
    api.get_quotes = AsyncMock(return_value={
        "client": {"nom": "Test"},
        "plans": [{"nom": "Prediccio_100", "requests_left": 950}]
    })
    return api


@pytest.mark.asyncio
async def test_station_data_loaded_from_cache(mock_hass, mock_entry_with_station_data, mock_api):
    """Test that station data is loaded from entry.data cache on init."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_with_station_data)
        coordinator.api = mock_api
        
        # Verify station data was loaded from cache
        assert coordinator.station_data is not None
        assert coordinator.station_data["codi"] == "YM"
        assert coordinator.station_data["altitud"] == 95
        assert coordinator.station_data["coordenades"]["latitud"] == 41.3851
        assert coordinator.station_data["coordenades"]["longitud"] == 2.1734


@pytest.mark.asyncio
async def test_station_data_fetched_when_not_cached(mock_hass, mock_entry_without_station_data, mock_api):
    """Test that station data is fetched from API when not in cache."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get'):
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_without_station_data)
        coordinator.api = mock_api
        
        # Initially empty
        assert coordinator.station_data == {}
        
        # First update should fetch station data
        await coordinator._async_update_data()
        
        # Verify API was called
        mock_api.get_stations.assert_called_once()
        
        # Verify station data was populated
        assert coordinator.station_data["codi"] == "YM"
        assert coordinator.station_data["altitud"] == 95


@pytest.mark.asyncio
async def test_station_data_saved_to_entry_data(mock_hass, mock_entry_without_station_data, mock_api):
    """Test that fetched station data is saved to entry.data for persistence."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get'):
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_without_station_data)
        coordinator.api = mock_api
        
        # First update fetches and saves station data
        await coordinator._async_update_data()
        
        # Verify async_update_entry was called to save station data
        mock_hass.config_entries.async_update_entry.assert_called_once()
        
        # Get the call arguments
        call_args = mock_hass.config_entries.async_update_entry.call_args
        updated_data = call_args[1]["data"]
        
        # Verify station data was saved
        assert "_station_data" in updated_data
        assert updated_data["_station_data"]["codi"] == "YM"
        assert updated_data["_station_data"]["altitud"] == 95
        assert updated_data["_station_data"]["coordenades"]["latitud"] == 41.3851


@pytest.mark.asyncio
async def test_station_data_not_refetched_when_cached(mock_hass, mock_entry_with_station_data, mock_api):
    """Test that station data is NOT refetched from API when already cached."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get'):
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_with_station_data)
        coordinator.api = mock_api
        
        # Update should NOT call get_stations since data is cached
        await coordinator._async_update_data()
        
        # Verify get_stations was NOT called
        mock_api.get_stations.assert_not_called()
        
        # Verify station data is still available
        assert coordinator.station_data["codi"] == "YM"


@pytest.mark.asyncio
async def test_station_data_persistence_saves_api_quota(mock_hass, mock_entry_with_station_data, mock_entry_without_station_data, mock_api):
    """Test that caching station data saves 1 API call per HA restart."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get'):
        
        # WITHOUT cache - calls get_stations
        coordinator_no_cache = MeteocatCoordinator(mock_hass, mock_entry_without_station_data)
        coordinator_no_cache.api = mock_api
        await coordinator_no_cache._async_update_data()
        
        calls_without_cache = mock_api.get_stations.call_count
        
        # Reset mock
        mock_api.get_stations.reset_mock()
        
        # WITH cache - does NOT call get_stations
        coordinator_with_cache = MeteocatCoordinator(mock_hass, mock_entry_with_station_data)
        coordinator_with_cache.api = mock_api
        await coordinator_with_cache._async_update_data()
        
        calls_with_cache = mock_api.get_stations.call_count
        
        # Verify quota savings: 1 less call when cached
        assert calls_without_cache == 1
        assert calls_with_cache == 0
