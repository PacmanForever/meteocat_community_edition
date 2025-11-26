"""Tests for re-authentication flow."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ConfigEntryAuthFailed

from custom_components.meteocat_community_edition.api import MeteocatAuthError
from custom_components.meteocat_community_edition.const import (
    CONF_API_KEY,
    CONF_MODE,
    CONF_STATION_CODE,
    DOMAIN,
    MODE_ESTACIO,
)


@pytest.fixture
def mock_entry_estacio():
    """Create a mock config entry for station mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        CONF_API_KEY: "test_api_key",
        CONF_MODE: MODE_ESTACIO,
        CONF_STATION_CODE: "YM",
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {DOMAIN: {}}
    hass.config_entries = MagicMock()
    hass.config_entries.async_update_entry = AsyncMock()
    hass.config_entries.async_reload = AsyncMock()
    return hass


@pytest.mark.asyncio
async def test_coordinator_raises_auth_failed_on_401(mock_hass, mock_entry_estacio):
    """Test that coordinator raises ConfigEntryAuthFailed on 401 error."""
    from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
    
    # Create coordinator
    coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
    
    # Mock API to raise auth error
    with patch.object(coordinator.api, "get_station_measurements", side_effect=MeteocatAuthError("401 error")):
        with pytest.raises(ConfigEntryAuthFailed) as exc_info:
            await coordinator._async_update_data()
        
        assert "Authentication failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_coordinator_raises_auth_failed_on_403(mock_hass, mock_entry_estacio):
    """Test that coordinator raises ConfigEntryAuthFailed on 403 error."""
    from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
    
    coordinator = MeteocatCoordinator(mock_hass, mock_entry_estacio)
    
    with patch.object(coordinator.api, "get_station_measurements", side_effect=MeteocatAuthError("403 error")):
        with pytest.raises(ConfigEntryAuthFailed) as exc_info:
            await coordinator._async_update_data()
        
        assert "Authentication failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_reauth_flow_validates_new_api_key(mock_hass):
    """Test that reauth flow validates new API key."""
    from custom_components.meteocat_community_edition.config_flow import MeteocatOptionsFlow
    
    # Create mock config entry
    mock_entry = MagicMock()
    mock_entry.data = {
        CONF_API_KEY: "old_key",
        CONF_MODE: MODE_ESTACIO,
    }
    
    flow = MeteocatOptionsFlow(mock_entry)
    flow.hass = mock_hass
    
    # Mock API validation success
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api_class:
        mock_api = AsyncMock()
        mock_api.get_comarques = AsyncMock(return_value=[{"codi": "01", "nom": "Test"}])
        mock_api_class.return_value = mock_api
        
        result = await flow.async_step_reauth_confirm({CONF_API_KEY: "new_valid_key"})
        
        assert result["type"] == "abort"
        assert result["reason"] == "reauth_successful"
        
        # Verify config entry was updated
        mock_hass.config_entries.async_update_entry.assert_called_once()
        call_args = mock_hass.config_entries.async_update_entry.call_args
        assert call_args[1]["data"][CONF_API_KEY] == "new_valid_key"


@pytest.mark.asyncio
async def test_reauth_flow_rejects_invalid_api_key(mock_hass):
    """Test that reauth flow rejects invalid API key."""
    from custom_components.meteocat_community_edition.config_flow import MeteocatOptionsFlow
    from custom_components.meteocat_community_edition.api import MeteocatAPIError
    
    mock_entry = MagicMock()
    mock_entry.data = {
        CONF_API_KEY: "old_key",
        CONF_MODE: MODE_ESTACIO,
    }
    
    flow = MeteocatOptionsFlow(mock_entry)
    flow.hass = mock_hass
    
    # Mock API validation failure
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api_class:
        mock_api = AsyncMock()
        mock_api.get_comarques = AsyncMock(side_effect=MeteocatAPIError("Invalid key"))
        mock_api_class.return_value = mock_api
        
        result = await flow.async_step_reauth_confirm({CONF_API_KEY: "invalid_key"})
        
        assert result["type"] == "form"
        assert result["errors"]["base"] == "invalid_auth"


@pytest.mark.asyncio
async def test_reauth_flow_triggers_reload(mock_hass):
    """Test that successful reauth triggers config entry reload."""
    from custom_components.meteocat_community_edition.config_flow import MeteocatOptionsFlow
    
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {CONF_API_KEY: "old_key"}
    
    flow = MeteocatOptionsFlow(mock_entry)
    flow.hass = mock_hass
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api_class:
        mock_api = AsyncMock()
        mock_api.get_comarques = AsyncMock(return_value=[{"codi": "01"}])
        mock_api_class.return_value = mock_api
        
        await flow.async_step_reauth_confirm({CONF_API_KEY: "new_key"})
        
        # Verify reload was called
        mock_hass.config_entries.async_reload.assert_called_once_with("test_entry")
