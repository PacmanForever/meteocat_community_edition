"""Tests for Meteocat button."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from unittest.mock import MagicMock, AsyncMock

from custom_components.meteocat_community_edition.button import (
    MeteocatRefreshMeasurementsButton,
    MeteocatRefreshForecastButton
)
from custom_components.meteocat_community_edition.const import DOMAIN, MODE_EXTERNAL, MODE_LOCAL


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
    coordinator.async_refresh_measurements = AsyncMock()
    coordinator.async_refresh_forecast = AsyncMock()
    return coordinator


@pytest.fixture
def mock_entry_xema():
    """Create a mock config entry for XEMA mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_xema"
    entry.data = {
        "mode": MODE_EXTERNAL,
        "station_code": "YM",
        "station_name": "Granollers",
    }
    return entry


@pytest.fixture
def mock_entry_local():
    """Create a mock config entry for Municipal mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_municipal"
    entry.data = {
        "mode": MODE_LOCAL,
        "municipality_code": "081131",
        "municipality_name": "Granollers",
    }
    return entry


def test_button_entity_id_xema_mode(mock_coordinator, mock_entry_xema):
    """Test button entity_id in XEMA mode includes station code."""
    button_meas = MeteocatRefreshMeasurementsButton(
        mock_coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )
    
    assert button_meas.entity_id == "button.granollers_ym_refresh_measurements"
    
    button_forecast = MeteocatRefreshForecastButton(
        mock_coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )
    
    assert button_forecast.entity_id == "button.granollers_ym_refresh_forecast"


def test_measurements_button_fallback_entity_id_local_mode(mock_coordinator, mock_entry_local):
    """Test measurements button gets correct entity_id fallback in local mode."""
    # Although practically unused in local mode, we test the code path for coverage
    button = MeteocatRefreshMeasurementsButton(
        mock_coordinator,
        mock_entry_local,
        "Granollers",
        "Granollers",
        MODE_LOCAL
    )
    
    assert button.entity_id == "button.granollers_refresh_measurements"


@pytest.mark.asyncio
async def test_button_press_fallback_refresh(mock_entry_xema):
    """Test button press falls back to request_refresh if specialized method missing."""
    # Create simple mock coordinator without extra methods
    coordinator = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
    # Ensure specialized methods are NOT present
    # By default MagicMock will create attributes on access, but hasattr check might succeed.
    # We need to ensure hasattr(coordinator, "async_refresh_measurements") is False.
    # But MagicMock is tricky with hasattr.
    
    # We can rely on the fact that if we don't access it, it might not exist in __dict__,
    # but the code uses hasattr().
    # A cleaner way is using a spec that doesn't include it.
    
    class SimpleCoordinator:
        async_request_refresh = AsyncMock()
    
    coordinator = SimpleCoordinator()
    
    button = MeteocatRefreshMeasurementsButton(
        coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )
    
    await button.async_press()
    coordinator.async_request_refresh.assert_called_once()


def test_button_entity_id_local_mode(mock_coordinator, mock_entry_local):
    """Test button entity_id in Municipal mode without station code."""
    button = MeteocatRefreshForecastButton(
        mock_coordinator,
        mock_entry_local,
        "Granollers",
        "Granollers",
        MODE_LOCAL
    )
    
    assert button.entity_id == "button.granollers_refresh_forecast"


def test_button_device_info_xema(mock_coordinator, mock_entry_xema):
    """Test button device_info uses device_name with code in XEMA mode."""
    button = MeteocatRefreshMeasurementsButton(
        mock_coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )
    
    device_info = button._attr_device_info
    assert device_info["name"] == "Granollers YM"
    assert (DOMAIN, "test_entry_xema") in device_info["identifiers"]


def test_button_device_info_municipal(mock_coordinator, mock_entry_local):
    """Test button device_info in Municipal mode."""
    button = MeteocatRefreshForecastButton(
        mock_coordinator,
        mock_entry_local,
        "Granollers",
        "Granollers",
        MODE_LOCAL
    )
    
    device_info = button._attr_device_info
    assert device_info["name"] == "Granollers"
    assert (DOMAIN, "test_entry_municipal") in device_info["identifiers"]


def test_button_name(mock_coordinator, mock_entry_xema):
    """Test button has correct translation key."""
    button = MeteocatRefreshMeasurementsButton(
        mock_coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )
    
    assert button.translation_key == "refresh_measurements"
    assert button.has_entity_name is True


def test_button_icon(mock_coordinator, mock_entry_xema):
    """Test button has refresh icon."""
    button = MeteocatRefreshMeasurementsButton(
        mock_coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )
    
    assert button.icon == "mdi:refresh"


async def test_button_press_triggers_refresh(mock_coordinator, mock_entry_xema):
    """Test button press triggers coordinator refresh."""
    button = MeteocatRefreshMeasurementsButton(
        mock_coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )
    
    await button.async_press()
    
    assert mock_coordinator.async_refresh_measurements.called


@pytest.mark.asyncio
async def test_button_press_triggers_refresh(mock_coordinator, mock_entry_xema):
    """Test button press triggers coordinator refresh."""
    button = MeteocatRefreshMeasurementsButton(
        mock_coordinator,
        mock_entry_xema,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )
    
    await button.async_press()
    
    assert mock_coordinator.async_refresh_measurements.called
