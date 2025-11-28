"""Tests for quota exhausted setup tolerance.

This test suite validates that the integration can complete setup even when
API quotas are exhausted, allowing data to be fetched on next scheduled update.

Test Coverage:
- MODE_ESTACIO setup with exhausted quotas
- MODE_MUNICIPI setup with exhausted quotas
- First refresh tolerates missing data
- Subsequent updates fail if data missing
- _is_first_refresh flag management

Last Updated: 2025-11-27
"""
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
from custom_components.meteocat_community_edition.const import (
    CONF_API_KEY,
    CONF_MODE,
    CONF_STATION_CODE,
    CONF_MUNICIPALITY_CODE,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    MODE_ESTACIO,
    MODE_MUNICIPI,
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
def mock_entry_estacio():
    """Create a mock config entry for ESTACIO mode."""
    entry = MagicMock()
    entry.entry_id = "test_estacio_entry"
    entry.data = {
        CONF_API_KEY: "test_api_key",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
        CONF_UPDATE_TIME_1: "06:00",
        CONF_UPDATE_TIME_2: "14:00",
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_entry_municipi():
    """Create a mock config entry for MUNICIPI mode."""
    entry = MagicMock()
    entry.entry_id = "test_municipi_entry"
    entry.data = {
        CONF_API_KEY: "test_api_key",
        CONF_MODE: MODE_MUNICIPI,
        CONF_MUNICIPALITY_CODE: "080193",
        CONF_UPDATE_TIME_1: "06:00",
        CONF_UPDATE_TIME_2: "14:00",
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_api_quota_exhausted():
    """Create a mock API with exhausted quotas (returns None for all data)."""
    api = MagicMock()
    api.get_stations = AsyncMock(return_value=[])
    api.get_station_measurements = AsyncMock(return_value=None)
    api.get_municipal_forecast = AsyncMock(return_value=None)
    api.get_hourly_forecast = AsyncMock(return_value=None)
    api.get_quotes = AsyncMock(return_value=None)
    api.find_municipality_for_station = AsyncMock(return_value=None)
    return api


@pytest.fixture
def mock_device_registry():
    """Mock device registry."""
    with patch('custom_components.meteocat_community_edition.coordinator.dr.async_get') as mock_dr:
        mock_registry = MagicMock()
        mock_dr.return_value = mock_registry
        yield mock_registry


# ============================================================================
# ESTACIO MODE - QUOTA EXHAUSTED SETUP
# ============================================================================

@pytest.mark.asyncio
async def test_estacio_first_refresh_tolerates_missing_measurements(
    mock_hass, mock_entry_estacio, mock_api_quota_exhausted, mock_device_registry
):
    """Test that ESTACIO mode first refresh allows setup even if measurements missing."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api_quota_exhausted
        
        # Verify _is_first_refresh is True initially
        assert coordinator._is_first_refresh is True
        
        # First refresh should NOT raise error even with missing measurements
        data = await coordinator._async_update_data()
        
        # Should return data structure but with None values
        assert data is not None
        assert data.get("measurements") is None
        
        # _is_first_refresh should now be False
        assert coordinator._is_first_refresh is False


@pytest.mark.asyncio
async def test_estacio_subsequent_update_fails_without_measurements(
    mock_hass, mock_entry_estacio, mock_api_quota_exhausted, mock_device_registry
):
    """Test that ESTACIO mode subsequent updates fail if measurements still missing."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = mock_api_quota_exhausted
        
        # First refresh - should succeed
        await coordinator._async_update_data()
        assert coordinator._is_first_refresh is False
        
        # Second update - should fail now
        from homeassistant.helpers.update_coordinator import UpdateFailed
        with pytest.raises(UpdateFailed, match="Missing critical data: measurements"):
            await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_estacio_first_refresh_tolerates_missing_forecasts(
    mock_hass, mock_entry_estacio, mock_device_registry
):
    """Test that ESTACIO mode tolerates missing forecasts on first refresh."""
    # API with measurements but no forecasts (quota exhausted for Predicció plan)
    api = MagicMock()
    api.get_stations = AsyncMock(return_value=[
        {"codi": "YM", "coordenades": {"latitud": 41.54, "longitud": 2.28}, "altitud": 150}
    ])
    api.get_station_measurements = AsyncMock(return_value=[{"codi": "YM", "variables": []}])
    api.get_municipal_forecast = AsyncMock(return_value=None)
    api.get_hourly_forecast = AsyncMock(return_value=None)
    api.get_quotes = AsyncMock(return_value=None)
    api.find_municipality_for_station = AsyncMock(return_value="081131")
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = api
        
        # First refresh should succeed even without forecasts
        data = await coordinator._async_update_data()
        
        assert data is not None
        assert data.get("measurements") is not None
        assert data.get("forecast") is None
        assert data.get("forecast_hourly") is None


# ============================================================================
# MUNICIPI MODE - QUOTA EXHAUSTED SETUP
# ============================================================================

@pytest.mark.asyncio
async def test_municipi_first_refresh_tolerates_missing_forecasts(
    mock_hass, mock_entry_municipi, mock_api_quota_exhausted, mock_device_registry
):
    """Test that MUNICIPI mode first refresh allows setup even if forecasts missing."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_municipi)
        coordinator.api = mock_api_quota_exhausted
        
        # Verify _is_first_refresh is True initially
        assert coordinator._is_first_refresh is True
        
        # First refresh should NOT raise error even with missing forecasts
        data = await coordinator._async_update_data()
        
        # Should return data structure but with None values
        assert data is not None
        assert data.get("forecast") is None
        assert data.get("forecast_hourly") is None
        
        # _is_first_refresh should now be False
        assert coordinator._is_first_refresh is False


@pytest.mark.asyncio
async def test_municipi_subsequent_update_fails_without_forecasts(
    mock_hass, mock_entry_municipi, mock_api_quota_exhausted, mock_device_registry
):
    """Test that MUNICIPI mode subsequent updates fail if forecasts still missing."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_municipi)
        coordinator.api = mock_api_quota_exhausted
        
        # First refresh - should succeed
        await coordinator._async_update_data()
        assert coordinator._is_first_refresh is False
        
        # Second update - should fail now
        from homeassistant.helpers.update_coordinator import UpdateFailed
        with pytest.raises(UpdateFailed, match="Missing critical data: forecast, forecast_hourly"):
            await coordinator._async_update_data()


# ============================================================================
# FLAG MANAGEMENT
# ============================================================================

@pytest.mark.asyncio
async def test_is_first_refresh_flag_resets_after_successful_update(
    mock_hass, mock_entry_estacio, mock_device_registry
):
    """Test that _is_first_refresh flag is reset after first successful update."""
    api = MagicMock()
    api.get_stations = AsyncMock(return_value=[
        {"codi": "YM", "coordenades": {"latitud": 41.54, "longitud": 2.28}, "altitud": 150}
    ])
    api.get_station_measurements = AsyncMock(return_value=[{"codi": "YM", "variables": []}])
    api.get_municipal_forecast = AsyncMock(return_value={"dies": []})
    api.get_hourly_forecast = AsyncMock(return_value={"dies": []})
    api.get_quotes = AsyncMock(return_value={"plans": []})
    api.find_municipality_for_station = AsyncMock(return_value="081131")
    
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
        coordinator.api = api
        
        # Initially True
        assert coordinator._is_first_refresh is True
        
        # First update
        await coordinator._async_update_data()
        
        # Should be False now
        assert coordinator._is_first_refresh is False
        
        # Second update
        await coordinator._async_update_data()
        
        # Should still be False
        assert coordinator._is_first_refresh is False


@pytest.mark.asyncio
async def test_is_first_refresh_flag_resets_even_with_missing_data(
    mock_hass, mock_entry_municipi, mock_api_quota_exhausted, mock_device_registry
):
    """Test that _is_first_refresh flag is reset even when data is missing on first refresh."""
    with patch('custom_components.meteocat_community_edition.coordinator.async_get_clientsession'):
        coordinator = MeteocatCoordinator(mock_hass, mock_entry_municipi)
        coordinator.api = mock_api_quota_exhausted
        
        assert coordinator._is_first_refresh is True
        
        # First refresh with missing data
        await coordinator._async_update_data()
        
        # Flag should be reset
        assert coordinator._is_first_refresh is False
