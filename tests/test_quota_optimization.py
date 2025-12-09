"""Tests for quota optimization and call counting."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator, MODE_ESTACIO
from custom_components.meteocat_community_edition.const import CONF_API_KEY, CONF_MODE, CONF_STATION_CODE, MODE_MUNICIPI, CONF_MUNICIPALITY_CODE

@pytest.fixture
def mock_hass():
    hass = MagicMock()
    hass.data = {}
    hass.config_entries = MagicMock()
    
    # Mock async_update_entry to update the entry.data in place
    def update_entry(entry, data):
        entry.data = data
        return True
        
    hass.config_entries.async_update_entry.side_effect = update_entry
    return hass

@pytest.fixture
def mock_entry():
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_API_KEY: "test_key",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
        # Initially empty cache
    }
    entry.options = {}
    return entry

@pytest.fixture
def mock_api():
    api = MagicMock()
    api.get_stations = AsyncMock(return_value=[
        {"codi": "YM", "nom": "Granollers", "coordenades": {"latitud": 41.6, "longitud": 2.3}}
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
    api.get_quotes = AsyncMock(return_value={
        "client": {"nom": "Test"},
        "plans": [{"nom": "Prediccio_100", "requests_left": 950}]
    })
    return api

@pytest.mark.asyncio
async def test_quota_optimization_call_counts(mock_hass, mock_entry, mock_api):
    """Test that API calls are optimized and data is persisted correctly."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get'):
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry)
        coordinator.api = mock_api
        
        # Enable both forecasts
        coordinator.enable_forecast_daily = True
        coordinator.enable_forecast_hourly = True
        
        # --- First Update (Cold Cache) ---
        await coordinator._async_update_data()
        
        # Verify calls for first update (should be 6)
        # 1. Measurements
        # 2. Stations (cache miss)
        # 3. Municipality (cache miss)
        # 4. Forecast Daily
        # 5. Forecast Hourly
        # 6. Quotes
        assert mock_api.get_station_measurements.call_count == 1
        assert mock_api.get_stations.call_count == 1
        assert mock_api.find_municipality_for_station.call_count == 1
        assert mock_api.get_municipal_forecast.call_count == 1
        assert mock_api.get_hourly_forecast.call_count == 1
        assert mock_api.get_quotes.call_count == 1
        
        # Verify data was saved to entry.data
        assert "_station_data" in mock_entry.data
        assert "station_municipality_code" in mock_entry.data
        
        # Verify async_update_entry was called (at least once)
        assert mock_hass.config_entries.async_update_entry.called
        
        # --- Second Update (Warm Cache) ---
        # Reset mocks to count calls for the second update only
        mock_api.reset_mock()
        
        # We reuse the same coordinator instance to simulate runtime behavior
        # But crucially, the coordinator reads from self.entry.data or self.station_data
        # The fix ensures self.entry.data is updated via the mock side_effect
        
        await coordinator._async_update_data()
        
        # Verify calls for second update (should be 4)
        # 1. Measurements
        # 2. Stations (SHOULD NOT BE CALLED - cache hit)
        # 3. Municipality (SHOULD NOT BE CALLED - cache hit)
        # 4. Forecast Daily
        # 5. Forecast Hourly
        # 6. Quotes
        assert mock_api.get_station_measurements.call_count == 1
        assert mock_api.get_stations.call_count == 0
        assert mock_api.find_municipality_for_station.call_count == 0
        assert mock_api.get_municipal_forecast.call_count == 1
        assert mock_api.get_hourly_forecast.call_count == 1
        assert mock_api.get_quotes.call_count == 1

@pytest.mark.asyncio
async def test_atomic_config_entry_update(mock_hass, mock_entry, mock_api):
    """Test that config entry updates are consolidated into a single call."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get'):
        
        coordinator = MeteocatCoordinator(mock_hass, mock_entry)
        coordinator.api = mock_api
        
        # Reset the mock to clear any calls from init
        mock_hass.config_entries.async_update_entry.reset_mock()
        
        await coordinator._async_update_data()
        
        # Verify async_update_entry was called exactly ONCE
        # This confirms the atomic update fix
        assert mock_hass.config_entries.async_update_entry.call_count == 1
        
        # Verify the content of the update
        call_args = mock_hass.config_entries.async_update_entry.call_args
        updated_data = call_args[1]['data']
        
        assert "_station_data" in updated_data
        assert "station_municipality_code" in updated_data

@pytest.mark.asyncio
async def test_municipal_mode_stability(mock_hass, mock_api):
    """Test that Municipal mode is stable and does not trigger extra calls."""
    # Create entry for Municipal mode
    entry = MagicMock()
    entry.entry_id = "test_entry_muni"
    entry.data = {
        CONF_API_KEY: "test_key",
        CONF_MODE: MODE_MUNICIPI,
        CONF_MUNICIPALITY_CODE: "081131", # Granollers
    }
    entry.options = {}
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'), \
         patch('custom_components.meteocat_community_edition.coordinator.dr.async_get'):
        
        coordinator = MeteocatCoordinator(mock_hass, entry)
        coordinator.api = mock_api
        
        # Enable both forecasts
        coordinator.enable_forecast_daily = True
        coordinator.enable_forecast_hourly = True
        
        # Reset mocks
        mock_api.reset_mock()
        mock_hass.config_entries.async_update_entry.reset_mock()
        
        # --- Update ---
        await coordinator._async_update_data()
        
        # Verify calls for Municipal mode (should be 3)
        # 1. Forecast Daily
        # 2. Forecast Hourly
        # 3. Quotes
        # NO Measurements, NO Stations, NO Find Municipality
        assert mock_api.get_municipal_forecast.call_count == 1
        assert mock_api.get_hourly_forecast.call_count == 1
        assert mock_api.get_quotes.call_count == 1
        
        assert mock_api.get_station_measurements.call_count == 0
        assert mock_api.get_stations.call_count == 0
        assert mock_api.find_municipality_for_station.call_count == 0
        
        # Verify NO config entry updates occurred
        assert mock_hass.config_entries.async_update_entry.call_count == 0
