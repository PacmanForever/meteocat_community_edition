"""Tests for MeteocatForecastCoordinator."""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from datetime import datetime

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.meteocat_community_edition.coordinator import MeteocatForecastCoordinator
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
async def test_forecast_coordinator_initialization(hass, mock_entry):
    """Test forecast coordinator initialization."""
    coordinator = MeteocatForecastCoordinator(hass, mock_entry)
    assert coordinator.municipality_code == "080193"
    assert coordinator.enable_forecast_daily is True
    assert coordinator.enable_forecast_hourly is True

@pytest.mark.asyncio
async def test_forecast_coordinator_update_success(hass, mock_api, mock_entry):
    """Test forecast coordinator successful update."""
    with patch("custom_components.meteocat_community_edition.coordinator.MeteocatAPI", return_value=mock_api):
        coordinator = MeteocatForecastCoordinator(hass, mock_entry)
        # Mock async_get_clientsession to avoid errors
        with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"):
             data = await coordinator._async_update_data()
        
        assert data["municipality_code"] == "080193"
        assert data["forecast"] is not None
        assert data["forecast_hourly"] is not None
        assert data["quotes"] is not None
        
        mock_api.get_municipal_forecast.assert_called_once_with("080193")
        mock_api.get_hourly_forecast.assert_called_once_with("080193")
        mock_api.get_quotes.assert_called_once()

@pytest.mark.asyncio
async def test_forecast_coordinator_update_daily_only(hass, mock_api, mock_entry):
    """Test forecast coordinator update with only daily forecast."""
    mock_entry.data[CONF_ENABLE_FORECAST_HOURLY] = False
    
    with patch("custom_components.meteocat_community_edition.coordinator.MeteocatAPI", return_value=mock_api):
        coordinator = MeteocatForecastCoordinator(hass, mock_entry)
        with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"):
             data = await coordinator._async_update_data()
        
        assert data["forecast"] is not None
        assert data.get("forecast_hourly") is None
        
        mock_api.get_municipal_forecast.assert_called_once_with("080193")
        mock_api.get_hourly_forecast.assert_not_called()

@pytest.mark.asyncio
async def test_forecast_coordinator_update_hourly_only(hass, mock_api, mock_entry):
    """Test forecast coordinator update with only hourly forecast."""
    mock_entry.data[CONF_ENABLE_FORECAST_DAILY] = False
    
    with patch("custom_components.meteocat_community_edition.coordinator.MeteocatAPI", return_value=mock_api):
        coordinator = MeteocatForecastCoordinator(hass, mock_entry)
        with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"):
             data = await coordinator._async_update_data()
        
        assert data.get("forecast") is None
        assert data["forecast_hourly"] is not None
        
        mock_api.get_municipal_forecast.assert_not_called()
        mock_api.get_hourly_forecast.assert_called_once_with("080193")

@pytest.mark.asyncio
async def test_forecast_coordinator_missing_critical_data(hass, mock_api, mock_entry):
    """Test forecast coordinator raises UpdateFailed when critical data is missing."""
    mock_api.get_municipal_forecast.return_value = None
    
    with patch("custom_components.meteocat_community_edition.coordinator.MeteocatAPI", return_value=mock_api):
        coordinator = MeteocatForecastCoordinator(hass, mock_entry)
        coordinator._is_first_refresh = False  # Ensure it raises
        
        with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"):
            with pytest.raises(UpdateFailed, match="Missing critical data"):
                await coordinator._async_update_data()

@pytest.mark.asyncio
async def test_forecast_coordinator_retryable_error(hass, mock_api, mock_entry):
    """Test forecast coordinator handles retryable errors."""
    from aiohttp import ClientError
    mock_api.get_municipal_forecast.side_effect = ClientError("Connection error")
    
    with patch("custom_components.meteocat_community_edition.coordinator.MeteocatAPI", return_value=mock_api):
        coordinator = MeteocatForecastCoordinator(hass, mock_entry)
        coordinator._schedule_retry_update = AsyncMock()
        
        with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession"):
            with pytest.raises(UpdateFailed, match="Temporary error"):
                await coordinator._async_update_data()
        
        coordinator._schedule_retry_update.assert_called_once()

@pytest.mark.asyncio
async def test_forecast_coordinator_scheduling(hass, mock_entry):
    """Test forecast coordinator scheduling."""
    coordinator = MeteocatForecastCoordinator(hass, mock_entry)
    
    # Mock time
    from homeassistant.util import dt as dt_util
    now = datetime(2025, 12, 10, 8, 0, 0, tzinfo=dt_util.UTC)
    with patch("custom_components.meteocat_community_edition.coordinator.dt_util.now", return_value=now):
        with patch("custom_components.meteocat_community_edition.coordinator.async_track_point_in_utc_time") as mock_track:
            coordinator._schedule_next_update()
            
            assert coordinator.next_scheduled_update is not None
            mock_track.assert_called_once()

