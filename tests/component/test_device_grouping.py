"""Tests for device grouping consistency."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from custom_components.meteocat_community_edition.sensor import (
    MeteocatQuotaSensor,
    MeteocatLastUpdateSensor,
    MeteocatNextUpdateSensor,
)
from custom_components.meteocat_community_edition.button import (
    MeteocatRefreshMeasurementsButton,
    MeteocatRefreshForecastButton,
)
from custom_components.meteocat_community_edition.const import DOMAIN, MODE_EXTERNAL


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {}
    coordinator.last_successful_update_time = datetime.now()
    coordinator.update_interval = timedelta(hours=8)
    return coordinator


@pytest.fixture
def mock_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        "mode": MODE_EXTERNAL,
        "station_code": "YM",
        "station_name": "Granollers",
    }
    return entry


def test_all_entities_share_same_device_identifier(mock_coordinator, mock_entry):
    """Test that all entities use the same device identifier."""
    # Create different entity types
    quota_sensor = MeteocatQuotaSensor(
        mock_coordinator,
        mock_entry,
        {"nom": "Prediccio_100", "requests_left": 950},
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL,
        "YM"
    )
    
    last_update_sensor = MeteocatLastUpdateSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL,
        "YM"
    )
    
    next_update_sensor = MeteocatNextUpdateSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL,
        "YM"
    )
    
    button_measurements = MeteocatRefreshMeasurementsButton(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )

    button_forecast = MeteocatRefreshForecastButton(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )
    
    # Extract device identifiers
    quota_identifier = list(quota_sensor._attr_device_info["identifiers"])[0]
    last_identifier = list(last_update_sensor._attr_device_info["identifiers"])[0]
    next_identifier = list(next_update_sensor._attr_device_info["identifiers"])[0]
    button_measurements_identifier = list(button_measurements._attr_device_info["identifiers"])[0]
    button_forecast_identifier = list(button_forecast._attr_device_info["identifiers"])[0]
    
    # All should be identical
    assert quota_identifier == last_identifier
    assert quota_identifier == next_identifier
    assert quota_identifier == button_measurements_identifier
    assert quota_identifier == button_forecast_identifier
    assert quota_identifier == (DOMAIN, "test_entry_id")


def test_all_entities_share_same_device_name(mock_coordinator, mock_entry):
    """Test that all entities use the same device name for grouping."""
    # Create different entity types
    quota_sensor = MeteocatQuotaSensor(
        mock_coordinator,
        mock_entry,
        {"nom": "Prediccio_100", "requests_left": 950},
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL,
        "YM"
    )
    
    last_update_sensor = MeteocatLastUpdateSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL,
        "YM"
    )
    
    next_update_sensor = MeteocatNextUpdateSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL,
        "YM"
    )
    
    button_measurements = MeteocatRefreshMeasurementsButton(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )

    button_forecast = MeteocatRefreshForecastButton(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )
    
    # All should use "Granollers YM" as device name
    assert quota_sensor._attr_device_info["name"] == "Granollers YM"
    assert last_update_sensor._attr_device_info["name"] == "Granollers YM"
    assert next_update_sensor._attr_device_info["name"] == "Granollers YM"
    assert button_measurements._attr_device_info["name"] == "Granollers YM"
    assert button_forecast._attr_device_info["name"] == "Granollers YM"


def test_entity_ids_include_station_code(mock_coordinator, mock_entry):
    """Test that entity IDs include station code for uniqueness."""
    quota_sensor = MeteocatQuotaSensor(
        mock_coordinator,
        mock_entry,
        {"nom": "Prediccio_100", "requests_left": 950},
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL,
        "YM"
    )
    
    last_update_sensor = MeteocatLastUpdateSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL,
        "YM"
    )
    
    next_update_sensor = MeteocatNextUpdateSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL,
        "YM"
    )
    
    button_measurements = MeteocatRefreshMeasurementsButton(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )

    button_forecast = MeteocatRefreshForecastButton(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_EXTERNAL
    )
    
    # All entity IDs should include station code
    assert "ym" in quota_sensor.entity_id
    assert "ym" in last_update_sensor.entity_id
    assert "ym" in next_update_sensor.entity_id
    assert "ym" in button_measurements.entity_id
    assert "ym" in button_forecast.entity_id
