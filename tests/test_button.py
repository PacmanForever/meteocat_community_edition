"""Tests for Meteocat button."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, AsyncMock

from custom_components.meteocat_community_edition.button import MeteocatRefreshButton
from custom_components.meteocat_community_edition.const import DOMAIN, MODE_ESTACIO, MODE_MUNICIPI


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
    return coordinator


@pytest.fixture
def mock_entry_xema():
    """Create a mock config entry for XEMA mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_xema"
    entry.data = {
        "mode": MODE_ESTACIO,
        "station_code": "YM",
        "station_name": "Granollers",
    }
    return entry


@pytest.fixture
def mock_entry_municipal():
    """Create a mock config entry for Municipal mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_municipal"
    entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "081131",
        "municipality_name": "Granollers",
    }
    return entry


def test_button_entity_id_xema_mode(mock_coordinator, mock_entry_xema):
    """Test button entity_id in XEMA mode includes station code."""
    button = MeteocatRefreshButton(
        mock_coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO
    )
    
    assert button.entity_id == "button.granollers_ym_refresh"


def test_button_entity_id_municipal_mode(mock_coordinator, mock_entry_municipal):
    """Test button entity_id in Municipal mode without station code."""
    button = MeteocatRefreshButton(
        mock_coordinator,
        mock_entry_municipal,
        "Granollers",
        "Granollers",
        MODE_MUNICIPI
    )
    
    assert button.entity_id == "button.granollers_refresh"


def test_button_device_info_xema(mock_coordinator, mock_entry_xema):
    """Test button device_info uses device_name with code in XEMA mode."""
    button = MeteocatRefreshButton(
        mock_coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO
    )
    
    device_info = button._attr_device_info
    assert device_info["name"] == "Granollers YM"
    assert (DOMAIN, "test_entry_xema") in device_info["identifiers"]


def test_button_device_info_municipal(mock_coordinator, mock_entry_municipal):
    """Test button device_info in Municipal mode."""
    button = MeteocatRefreshButton(
        mock_coordinator,
        mock_entry_municipal,
        "Granollers",
        "Granollers",
        MODE_MUNICIPI
    )
    
    device_info = button._attr_device_info
    assert device_info["name"] == "Granollers"
    assert (DOMAIN, "test_entry_municipal") in device_info["identifiers"]


def test_button_name(mock_coordinator, mock_entry_xema):
    """Test button has correct name."""
    button = MeteocatRefreshButton(
        mock_coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO
    )
    
    assert button.name == "Actualitzar dades"


def test_button_icon(mock_coordinator, mock_entry_xema):
    """Test button has refresh icon."""
    button = MeteocatRefreshButton(
        mock_coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO
    )
    
    assert button.icon == "mdi:refresh"


@pytest.mark.asyncio
async def test_button_press_triggers_refresh(mock_coordinator, mock_entry_xema):
    """Test button press triggers coordinator refresh."""
    button = MeteocatRefreshButton(
        mock_coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO
    )
    
    await button.async_press()
    
    mock_coordinator.async_request_refresh.assert_called_once()
