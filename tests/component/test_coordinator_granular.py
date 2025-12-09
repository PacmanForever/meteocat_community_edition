"""Tests for granular configuration in Meteocat coordinator."""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_API_KEY

from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
from custom_components.meteocat_community_edition.const import (
    CONF_MODE,
    CONF_MUNICIPALITY_CODE,
    CONF_ENABLE_FORECAST_DAILY,
    CONF_ENABLE_FORECAST_HOURLY,
    MODE_LOCAL,
    DOMAIN,
)

@pytest.fixture
def mock_api():
    """Mock the Meteocat API."""
    api = MagicMock()
    api.get_municipal_forecast = AsyncMock(return_value={"dies": []})
    api.get_hourly_forecast = AsyncMock(return_value={"dies": []})
    api.get_quotes = AsyncMock(return_value={})
    return api

@pytest.fixture
def mock_entry():
    """Mock the config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        CONF_API_KEY: "test_key",
        CONF_MODE: MODE_LOCAL,
        CONF_MUNICIPALITY_CODE: "080193",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: True,
    }
    entry.options = {}
    return entry



@pytest.mark.asyncio
async def test_coordinator_calls_both_when_enabled(hass, mock_api, mock_entry):
    """Test coordinator calls both forecast APIs when both are enabled."""
    with patch("custom_components.meteocat_community_edition.coordinator.MeteocatAPI", return_value=mock_api):
        coordinator = MeteocatCoordinator(hass, mock_entry)
        # Mock async_get_clientsession to avoid errors
        with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"):
             await coordinator._async_update_data()
        
        mock_api.get_municipal_forecast.assert_called_once_with("080193")
        mock_api.get_hourly_forecast.assert_called_once_with("080193")

@pytest.mark.asyncio
async def test_coordinator_skips_daily_when_disabled(hass, mock_api, mock_entry):
    """Test coordinator skips daily forecast when disabled."""
    mock_entry.data[CONF_ENABLE_FORECAST_DAILY] = False
    
    with patch("custom_components.meteocat_community_edition.coordinator.MeteocatAPI", return_value=mock_api):
        coordinator = MeteocatCoordinator(hass, mock_entry)
        with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"):
            await coordinator._async_update_data()
        
        mock_api.get_municipal_forecast.assert_not_called()
        mock_api.get_hourly_forecast.assert_called_once_with("080193")

@pytest.mark.asyncio
async def test_coordinator_skips_hourly_when_disabled(hass, mock_api, mock_entry):
    """Test coordinator skips hourly forecast when disabled."""
    mock_entry.data[CONF_ENABLE_FORECAST_HOURLY] = False
    
    with patch("custom_components.meteocat_community_edition.coordinator.MeteocatAPI", return_value=mock_api):
        coordinator = MeteocatCoordinator(hass, mock_entry)
        with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"):
            await coordinator._async_update_data()
        
        mock_api.get_municipal_forecast.assert_called_once_with("080193")
        mock_api.get_hourly_forecast.assert_not_called()

@pytest.mark.asyncio
async def test_coordinator_skips_both_when_disabled(hass, mock_api, mock_entry):
    """Test coordinator skips both forecasts when disabled."""
    mock_entry.data[CONF_ENABLE_FORECAST_DAILY] = False
    mock_entry.data[CONF_ENABLE_FORECAST_HOURLY] = False
    
    with patch("custom_components.meteocat_community_edition.coordinator.MeteocatAPI", return_value=mock_api):
        coordinator = MeteocatCoordinator(hass, mock_entry)
        with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"):
            await coordinator._async_update_data()
        
        mock_api.get_municipal_forecast.assert_not_called()
        mock_api.get_hourly_forecast.assert_not_called()
