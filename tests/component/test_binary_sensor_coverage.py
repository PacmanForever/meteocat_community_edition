"""Tests for binary sensor coverage."""
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.meteocat_community_edition.const import (
    CONF_MODE,
    CONF_MUNICIPALITY_CODE,
    CONF_MUNICIPALITY_NAME,
    CONF_STATION_CODE,
    CONF_STATION_NAME,
    DOMAIN,
    MODE_EXTERNAL,
    MODE_LOCAL,
)
from custom_components.meteocat_community_edition.binary_sensor import MeteocatUpdateStatusBinarySensor

from pytest_homeassistant_custom_component.common import MockConfigEntry

@pytest.fixture
def mock_coordinator(hass):
    """Mock the coordinator."""
    coordinator = MagicMock()
    coordinator.hass = hass
    coordinator.data = {}
    coordinator.last_update_success = True
    coordinator.last_successful_update_time = dt_util.utcnow()
    coordinator.enable_forecast_daily = True
    coordinator.enable_forecast_hourly = True
    return coordinator

async def test_binary_sensor_attributes_empty_measurements(hass: HomeAssistant, mock_coordinator):
    """Test attributes when measurements are empty (quota exhausted)."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_EXTERNAL,
            CONF_STATION_CODE: "X4",
            CONF_STATION_NAME: "Test Station",
        },
    )
    
    mock_coordinator.data = {
        "measurements": [],  # Empty list
        "municipality_code": None,
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator,
        entry,
        "Test Station",
        "Test Station X4",
        MODE_EXTERNAL,
        "X4",
    )
    
    assert sensor.is_on is True
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert "measurements (empty/quota exhausted)" in attrs["error"]

async def test_binary_sensor_attributes_none_measurements(hass: HomeAssistant, mock_coordinator):
    """Test attributes when measurements are None (API failed)."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_EXTERNAL,
            CONF_STATION_CODE: "X4",
            CONF_STATION_NAME: "Test Station",
        },
    )
    
    mock_coordinator.data = {
        "measurements": None,
        "municipality_code": None,
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator,
        entry,
        "Test Station",
        "Test Station X4",
        MODE_EXTERNAL,
        "X4",
    )
    
    assert sensor.is_on is True
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert "measurements (API call failed)" in attrs["error"]

async def test_binary_sensor_attributes_empty_forecast(hass: HomeAssistant, mock_coordinator):
    """Test attributes when forecast is empty (quota exhausted)."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "080193",
            CONF_MUNICIPALITY_NAME: "Barcelona",
        },
    )
    
    mock_coordinator.data = {
        "forecast": [],
        "forecast_hourly": [{"temp": 20}],
        "municipality_code": "080193",
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator,
        entry,
        "Barcelona",
        "Barcelona",
        MODE_LOCAL,
        None,
    )
    
    assert sensor.is_on is True
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert "forecast (empty/quota exhausted)" in attrs["error"]

async def test_binary_sensor_attributes_none_forecast(hass: HomeAssistant, mock_coordinator):
    """Test attributes when forecast is None (API failed)."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "080193",
            CONF_MUNICIPALITY_NAME: "Barcelona",
        },
    )
    
    mock_coordinator.data = {
        "forecast": None,
        "forecast_hourly": [{"temp": 20}],
        "municipality_code": "080193",
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator,
        entry,
        "Barcelona",
        "Barcelona",
        MODE_LOCAL,
        None,
    )
    
    assert sensor.is_on is True
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert "forecast (API call failed)" in attrs["error"]

async def test_binary_sensor_attributes_empty_forecast_hourly(hass: HomeAssistant, mock_coordinator):
    """Test attributes when hourly forecast is empty."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "080193",
            CONF_MUNICIPALITY_NAME: "Barcelona",
        },
    )
    
    mock_coordinator.data = {
        "forecast": [{"temp": 20}],
        "forecast_hourly": [],
        "municipality_code": "080193",
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator,
        entry,
        "Barcelona",
        "Barcelona",
        MODE_LOCAL,
        None,
    )
    
    assert sensor.is_on is True
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert "forecast_hourly (empty/quota exhausted)" in attrs["error"]

async def test_binary_sensor_attributes_none_forecast_hourly(hass: HomeAssistant, mock_coordinator):
    """Test attributes when hourly forecast is None."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "080193",
            CONF_MUNICIPALITY_NAME: "Barcelona",
        },
    )
    
    mock_coordinator.data = {
        "forecast": [{"temp": 20}],
        "forecast_hourly": None,
        "municipality_code": "080193",
    }
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator,
        entry,
        "Barcelona",
        "Barcelona",
        MODE_LOCAL,
        None,
    )
    
    assert sensor.is_on is True
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert "forecast_hourly (API call failed)" in attrs["error"]

async def test_binary_sensor_update_failed_but_data_ok(hass: HomeAssistant, mock_coordinator):
    """Test attributes when update failed but data checks pass (generic error)."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "080193",
            CONF_MUNICIPALITY_NAME: "Barcelona",
        },
    )
    
    mock_coordinator.data = {
        "forecast": [{"temp": 20}],
        "forecast_hourly": [{"temp": 20}],
        "municipality_code": "080193",
    }
    mock_coordinator.last_update_success = False
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator,
        entry,
        "Barcelona",
        "Barcelona",
        MODE_LOCAL,
        None,
    )
    
    assert sensor.is_on is True
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert attrs["error"] == "Update failed - check logs for details"

async def test_binary_sensor_no_coordinator_data(hass: HomeAssistant, mock_coordinator):
    """Test attributes when coordinator data is missing."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "080193",
            CONF_MUNICIPALITY_NAME: "Barcelona",
        },
    )
    
    mock_coordinator.data = None
    
    sensor = MeteocatUpdateStatusBinarySensor(
        mock_coordinator,
        entry,
        "Barcelona",
        "Barcelona",
        MODE_LOCAL,
        None,
    )
    
    assert sensor.is_on is True
    attrs = sensor.extra_state_attributes
    assert attrs["status"] == "error"
    assert attrs["error"] == "No data available - coordinator not initialized"
