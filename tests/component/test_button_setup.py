"""Tests for Meteocat button setup."""
from unittest.mock import MagicMock, AsyncMock, patch
import pytest

from homeassistant.const import Platform
from custom_components.meteocat_community_edition.button import async_setup_entry
from custom_components.meteocat_community_edition.const import DOMAIN, MODE_ESTACIO, MODE_MUNICIPI

@pytest.fixture
def mock_hass():
    """Mock Home Assistant."""
    hass = MagicMock()
    hass.data = {DOMAIN: {}}
    return hass

@pytest.fixture
def mock_coordinator():
    """Mock coordinator."""
    return MagicMock()

@pytest.fixture
def mock_entry():
    """Mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "mode": MODE_ESTACIO,
        "station_code": "YM",
        "station_name": "Granollers",
    }
    return entry

@pytest.mark.asyncio
async def test_async_setup_entry_station_mode(mock_hass, mock_coordinator, mock_entry):
    """Test setup in station mode."""
    mock_hass.data[DOMAIN][mock_entry.entry_id] = mock_coordinator
    async_add_entities = MagicMock()
    
    await async_setup_entry(mock_hass, mock_entry, async_add_entities)
    
    async_add_entities.assert_called_once()
    args = async_add_entities.call_args[0][0]
    assert len(args) == 2
    assert args[0].unique_id == "test_entry_refresh_measurements"
    assert args[1].unique_id == "test_entry_refresh_forecast"

@pytest.mark.asyncio
async def test_async_setup_entry_municipal_mode(mock_hass, mock_coordinator):
    """Test setup in municipal mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_muni"
    entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "081131",
        "municipality_name": "Granollers",
    }
    
    mock_hass.data[DOMAIN][entry.entry_id] = mock_coordinator
    async_add_entities = MagicMock()
    
    await async_setup_entry(mock_hass, entry, async_add_entities)
    
    async_add_entities.assert_called_once()
    args = async_add_entities.call_args[0][0]
    assert len(args) == 1
    assert args[0].unique_id == "test_entry_muni_refresh_forecast"
