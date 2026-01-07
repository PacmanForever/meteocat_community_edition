"""Tests for Meteocat weather entity setup."""
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.meteocat_community_edition.weather import async_setup_entry
from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    CONF_MODE,
    CONF_STATION_NAME,
    CONF_MUNICIPALITY_NAME,
    MODE_EXTERNAL,
    MODE_LOCAL,
)

@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {DOMAIN: {}}
    return hass

@pytest.fixture
def mock_entry():
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = {
        CONF_MODE: MODE_EXTERNAL,
        CONF_STATION_NAME: "Test Station",
    }
    entry.options = {}
    return entry

@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    return coordinator

@pytest.mark.asyncio
async def test_async_setup_entry_external_mode(mock_hass, mock_entry, mock_coordinator):
    """Test setup entry in station mode."""
    mock_hass.data[DOMAIN][mock_entry.entry_id] = mock_coordinator
    async_add_entities = MagicMock()

    await async_setup_entry(mock_hass, mock_entry, async_add_entities)

    assert async_add_entities.called
    args = async_add_entities.call_args[0][0]
    assert len(args) == 1
    assert args[0].unique_id == "test_entry_id_weather"

@pytest.mark.asyncio
async def test_async_setup_entry_local_mode(mock_hass, mock_entry, mock_coordinator):
    """Test setup entry in local mode."""
    mock_entry.data[CONF_MODE] = MODE_LOCAL
    mock_entry.data[CONF_MUNICIPALITY_NAME] = "Abrera"
    mock_hass.data[DOMAIN][mock_entry.entry_id] = mock_coordinator
    async_add_entities = MagicMock()

    await async_setup_entry(mock_hass, mock_entry, async_add_entities)

    assert async_add_entities.called
    args = async_add_entities.call_args[0][0]
    assert len(args) == 1
    assert args[0].unique_id == "test_entry_id_weather_local"
