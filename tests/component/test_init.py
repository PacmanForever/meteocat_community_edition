"""Tests for Meteocat __init__.py setup and unload."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from homeassistant.const import Platform

from custom_components.meteocat_community_edition import (
    async_setup_entry,
    async_update_options,
    async_unload_entry,
    PLATFORMS,
)
from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    MODE_EXTERNAL,
    MODE_LOCAL,
    CONF_MODE,
    CONF_API_KEY,
    CONF_STATION_CODE,
    CONF_MUNICIPALITY_CODE,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.config_entries.async_reload = AsyncMock()
    return hass


@pytest.fixture
def mock_entry_estacio():
    """Create a mock config entry for MODE_EXTERNAL."""
    entry = MagicMock()
    entry.entry_id = "test_entry_estacio"
    entry.data = {
        CONF_API_KEY: "test_api_key",
        CONF_MODE: MODE_EXTERNAL,
        CONF_STATION_CODE: "YM",
    }
    entry.options = {}
    entry.add_update_listener = MagicMock(return_value=MagicMock())
    entry.async_on_unload = MagicMock()
    return entry


@pytest.fixture
def mock_entry_municipi():
    """Create a mock config entry for MODE_LOCAL."""
    entry = MagicMock()
    entry.entry_id = "test_entry_municipi"
    entry.data = {
        CONF_API_KEY: "test_api_key",
        CONF_MODE: MODE_LOCAL,
        CONF_MUNICIPALITY_CODE: "081131",
    }
    entry.options = {}
    entry.add_update_listener = MagicMock(return_value=MagicMock())
    entry.async_on_unload = MagicMock()
    return entry


@pytest.mark.asyncio
async def test_async_setup_entry_external_mode(mock_hass, mock_entry_estacio):
    """Test setup entry for MODE_EXTERNAL loads all platforms."""
    with patch('custom_components.meteocat_community_edition.MeteocatLegacyCoordinator') as mock_coordinator_class:
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator_class.return_value = mock_coordinator
        
        result = await async_setup_entry(mock_hass, mock_entry_estacio)
        
        # Should return True
        assert result is True
        
        # Should create coordinator
        mock_coordinator_class.assert_called_once_with(mock_hass, mock_entry_estacio)
        
        # Should do first refresh
        mock_coordinator.async_config_entry_first_refresh.assert_called_once()
        
        # Should store coordinator in hass.data
        assert DOMAIN in mock_hass.data
        assert mock_entry_estacio.entry_id in mock_hass.data[DOMAIN]
        assert mock_hass.data[DOMAIN][mock_entry_estacio.entry_id] == mock_coordinator
        
        # Should load all platforms (weather, sensor, button)
        mock_hass.config_entries.async_forward_entry_setups.assert_called_once()
        call_args = mock_hass.config_entries.async_forward_entry_setups.call_args
        assert call_args[0][0] == mock_entry_estacio
        platforms = call_args[0][1]
        assert Platform.WEATHER in platforms
        assert Platform.SENSOR in platforms
        assert Platform.BUTTON in platforms
        
        # Should register update listener
        mock_entry_estacio.add_update_listener.assert_called_once()
        mock_entry_estacio.async_on_unload.assert_called_once()


@pytest.mark.asyncio
async def test_async_setup_entry_local_mode(mock_hass, mock_entry_municipi):
    """Test setup entry for MODE_LOCAL loads all platforms including weather."""
    with patch('custom_components.meteocat_community_edition.MeteocatForecastCoordinator') as mock_coordinator_class:
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator_class.return_value = mock_coordinator
        
        result = await async_setup_entry(mock_hass, mock_entry_municipi)
        
        # Should return True
        assert result is True
        
        # Should load all platforms including weather
        mock_hass.config_entries.async_forward_entry_setups.assert_called_once()
        call_args = mock_hass.config_entries.async_forward_entry_setups.call_args
        platforms = call_args[0][1]
        assert Platform.WEATHER in platforms
        assert Platform.SENSOR in platforms
        assert Platform.BUTTON in platforms
        assert Platform.BINARY_SENSOR in platforms
        assert len(platforms) == 4


@pytest.mark.asyncio
async def test_async_setup_entry_stores_coordinator(mock_hass, mock_entry_estacio):
    """Test that setup entry stores coordinator in hass.data."""
    with patch('custom_components.meteocat_community_edition.MeteocatLegacyCoordinator') as mock_coordinator_class:
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator_class.return_value = mock_coordinator
        
        await async_setup_entry(mock_hass, mock_entry_estacio)
        
        # Verify coordinator is stored with correct structure
        assert DOMAIN in mock_hass.data
        assert isinstance(mock_hass.data[DOMAIN], dict)
        assert mock_entry_estacio.entry_id in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_update_options(mock_hass, mock_entry_estacio):
    """Test that update options triggers entry reload."""
    await async_update_options(mock_hass, mock_entry_estacio)
    
    # Should reload the entry
    mock_hass.config_entries.async_reload.assert_called_once_with(mock_entry_estacio.entry_id)


@pytest.mark.asyncio
async def test_async_unload_entry_external_mode(mock_hass, mock_entry_estacio):
    """Test unload entry for MODE_EXTERNAL unloads all platforms."""
    # Setup: add coordinator to hass.data
    mock_coordinator = MagicMock()
    mock_coordinator.async_shutdown = AsyncMock()
    mock_hass.data[DOMAIN] = {mock_entry_estacio.entry_id: mock_coordinator}
    
    result = await async_unload_entry(mock_hass, mock_entry_estacio)
    
    # Should return True (unload successful)
    assert result is True
    
    # Should unload all platforms
    mock_hass.config_entries.async_unload_platforms.assert_called_once()
    call_args = mock_hass.config_entries.async_unload_platforms.call_args
    assert call_args[0][0] == mock_entry_estacio
    platforms = call_args[0][1]
    assert Platform.WEATHER in platforms
    assert Platform.SENSOR in platforms
    assert Platform.BUTTON in platforms
    
    # Should remove coordinator from hass.data
    assert mock_entry_estacio.entry_id not in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_unload_entry_local_mode(mock_hass, mock_entry_municipi):
    """Test unload entry for MODE_LOCAL unloads all platforms."""
    # Setup: add coordinator to hass.data
    mock_coordinator = MagicMock()
    mock_coordinator.async_shutdown = AsyncMock()
    mock_hass.data[DOMAIN] = {mock_entry_municipi.entry_id: mock_coordinator}
    
    result = await async_unload_entry(mock_hass, mock_entry_municipi)
    
    # Should return True
    assert result is True
    
    # Should unload only sensor, button, and binary_sensor platforms
    call_args = mock_hass.config_entries.async_unload_platforms.call_args
    platforms = call_args[0][1]
    assert Platform.WEATHER not in platforms
    assert Platform.SENSOR in platforms
    assert Platform.BUTTON in platforms
    assert Platform.BINARY_SENSOR in platforms
    assert len(platforms) == 3


@pytest.mark.asyncio
async def test_async_unload_entry_failed_unload(mock_hass, mock_entry_estacio):
    """Test unload entry when platform unload fails."""
    # Setup: add coordinator to hass.data
    mock_coordinator = MagicMock()
    mock_coordinator.async_shutdown = AsyncMock()
    mock_hass.data[DOMAIN] = {mock_entry_estacio.entry_id: mock_coordinator}
    
    # Make unload fail
    mock_hass.config_entries.async_unload_platforms.return_value = False
    
    result = await async_unload_entry(mock_hass, mock_entry_estacio)
    
    # Should return False
    assert result is False
    
    # Coordinator should NOT be removed from hass.data
    assert mock_entry_estacio.entry_id in mock_hass.data[DOMAIN]
    assert mock_hass.data[DOMAIN][mock_entry_estacio.entry_id] == mock_coordinator


@pytest.mark.asyncio
async def test_platforms_constant():
    """Test that PLATFORMS constant contains expected platforms."""
    assert Platform.WEATHER in PLATFORMS
    assert Platform.SENSOR in PLATFORMS
    assert Platform.BUTTON in PLATFORMS
    assert Platform.BINARY_SENSOR in PLATFORMS
    assert len(PLATFORMS) == 4


@pytest.mark.asyncio
async def test_async_setup_entry_default_mode(mock_hass):
    """Test setup entry defaults to MODE_EXTERNAL if mode not specified."""
    # Entry without CONF_MODE
    entry = MagicMock()
    entry.entry_id = "test_entry_no_mode"
    entry.data = {
        CONF_API_KEY: "test_api_key",
        CONF_STATION_CODE: "YM",
    }
    entry.options = {}
    entry.add_update_listener = MagicMock(return_value=MagicMock())
    entry.async_on_unload = MagicMock()
    
    with patch('custom_components.meteocat_community_edition.MeteocatLegacyCoordinator') as mock_coordinator_class:
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator_class.return_value = mock_coordinator
        
        result = await async_setup_entry(mock_hass, entry)
        
        # Should default to ESTACIO mode and load all platforms
        assert result is True
        call_args = mock_hass.config_entries.async_forward_entry_setups.call_args
        platforms = call_args[0][1]
        assert Platform.WEATHER in platforms


@pytest.mark.asyncio
async def test_async_setup_entry_multiple_entries(mock_hass, mock_entry_estacio, mock_entry_municipi):
    """Test setup multiple entries stores both coordinators."""
    with patch('custom_components.meteocat_community_edition.MeteocatLegacyCoordinator') as mock_legacy_class, \
         patch('custom_components.meteocat_community_edition.MeteocatForecastCoordinator') as mock_forecast_class:
        
        mock_coordinator_1 = MagicMock()
        mock_coordinator_1.async_config_entry_first_refresh = AsyncMock()
        mock_legacy_class.return_value = mock_coordinator_1
        
        mock_coordinator_2 = MagicMock()
        mock_coordinator_2.async_config_entry_first_refresh = AsyncMock()
        mock_forecast_class.return_value = mock_coordinator_2
        
        # Setup first entry
        await async_setup_entry(mock_hass, mock_entry_estacio)
        
        # Setup second entry
        await async_setup_entry(mock_hass, mock_entry_municipi)
        
        # Both coordinators should be stored
        assert mock_entry_estacio.entry_id in mock_hass.data[DOMAIN]
        assert mock_entry_municipi.entry_id in mock_hass.data[DOMAIN]
        assert mock_hass.data[DOMAIN][mock_entry_estacio.entry_id] == mock_coordinator_1
        assert mock_hass.data[DOMAIN][mock_entry_municipi.entry_id] == mock_coordinator_2
