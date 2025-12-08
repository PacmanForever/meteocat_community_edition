"""Tests for Meteocat quota estimation sensors."""
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from custom_components.meteocat_community_edition.sensor import (
    MeteocatEstimatedDaysRemainingSensor,
)
from custom_components.meteocat_community_edition.const import (
    MODE_ESTACIO,
    MODE_MUNICIPI,
)

# Disable socket blocking for this file if pytest-socket is installed
try:
    import pytest_socket
    def pytest_configure(config):
        config.option.disable_socket = False
except ImportError:
    pass

@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "quotes": {
            "plans": [
                {"nom": "Predicció", "consultesRestants": 1000},
                {"nom": "XEMA", "consultesRestants": 500},
                {"nom": "Quota", "consultesRestants": 200},
            ]
        }
    }
    # Default configuration: 2 updates per day
    coordinator.update_time_1 = "08:00"
    coordinator.update_time_2 = "20:00"
    coordinator.update_time_3 = None
    
    # Default forecast configuration
    coordinator.enable_forecast_daily = True
    coordinator.enable_forecast_hourly = True
    
    return coordinator

@pytest.fixture
def mock_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        "mode": MODE_ESTACIO,
        "station_code": "YM",
        "station_name": "Granollers",
    }
    entry.options = {}
    return entry

def test_days_remaining_sensor_init(mock_coordinator, mock_entry):
    """Test initialization of the days remaining sensor."""
    plan_data = {"nom": "Predicció", "peticions_disponibles": 1000}
    
    sensor = MeteocatEstimatedDaysRemainingSensor(
        mock_coordinator,
        mock_entry,
        plan_data,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    assert sensor.name == "Dies disponibles Predicció"
    assert sensor.unique_id == "test_entry_id_quota_dies_estimats_prediccio"
    assert sensor.entity_id == "sensor.granollers_ym_quota_dies_estimats_prediccio"
    assert sensor.native_unit_of_measurement == "dies"
    assert sensor.icon == "mdi:calendar-clock"

def test_days_remaining_calculation_prediccio_2_updates(mock_coordinator, mock_entry):
    """Test calculation for Predicció plan with 2 updates/day."""
    # Setup: 2 updates/day, Predicció (Daily + Hourly = 2 calls/update)
    # Total daily consumption = 2 updates * 2 calls = 4 calls/day
    # Available = 1000
    # Expected days = 1000 / 4 = 250.0
    
    plan_data = {"nom": "Predicció", "peticions_disponibles": 1000}
    mock_coordinator.data = {
        "quotes": {
            "plans": [
                {"nom": "Predicció", "consultesRestants": 1000}
            ]
        }
    }
    
    sensor = MeteocatEstimatedDaysRemainingSensor(
        mock_coordinator,
        mock_entry,
        plan_data,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    assert sensor.native_value == 250.0

def test_days_remaining_calculation_prediccio_3_updates(mock_coordinator, mock_entry):
    """Test calculation for Predicció plan with 3 updates/day."""
    # Setup: 3 updates/day
    mock_coordinator.update_time_3 = "14:00"
    
    # Predicció (Daily + Hourly = 2 calls/update)
    # Total daily consumption = 3 updates * 2 calls = 6 calls/day
    # Available = 1000
    # Expected days = 1000 / 6 = 166.66... -> 166.7
    
    plan_data = {"nom": "Predicció", "peticions_disponibles": 1000}
    mock_coordinator.data = {
        "quotes": {
            "plans": [
                {"nom": "Predicció", "consultesRestants": 1000}
            ]
        }
    }
    
    sensor = MeteocatEstimatedDaysRemainingSensor(
        mock_coordinator,
        mock_entry,
        plan_data,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    assert sensor.native_value == 166.7

def test_days_remaining_calculation_xema_1_update(mock_coordinator, mock_entry):
    """Test calculation for XEMA plan with 1 update/day."""
    # Setup: 1 update/day
    mock_coordinator.update_time_2 = None
    mock_coordinator.update_time_3 = None
    
    # XEMA (1 call/update)
    # Total daily consumption = 1 update * 1 call = 1 call/day
    # Available = 500
    # Expected days = 500 / 1 = 500.0
    
    plan_data = {"nom": "XEMA", "peticions_disponibles": 500}
    mock_coordinator.data = {
        "quotes": {
            "plans": [
                {"nom": "XEMA", "consultesRestants": 500}
            ]
        }
    }
    
    sensor = MeteocatEstimatedDaysRemainingSensor(
        mock_coordinator,
        mock_entry,
        plan_data,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    assert sensor.native_value == 500.0

def test_days_remaining_calculation_quota_generic(mock_coordinator, mock_entry):
    """Test calculation for generic Quota plan."""
    # Setup: 2 updates/day
    # Quota (1 call/update)
    # Total daily consumption = 2 updates * 1 call = 2 calls/day
    # Available = 200
    # Expected days = 200 / 2 = 100.0
    
    plan_data = {"nom": "Quota", "peticions_disponibles": 200}
    mock_coordinator.data = {
        "quotes": {
            "plans": [
                {"nom": "Quota", "consultesRestants": 200}
            ]
        }
    }
    
    sensor = MeteocatEstimatedDaysRemainingSensor(
        mock_coordinator,
        mock_entry,
        plan_data,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    assert sensor.native_value == 100.0

def test_days_remaining_infinite(mock_coordinator, mock_entry):
    """Test calculation when consumption is 0 (infinite days)."""
    # Setup: 0 updates/day (shouldn't happen normally but possible config)
    mock_coordinator.update_time_1 = None
    mock_coordinator.update_time_2 = None
    mock_coordinator.update_time_3 = None
    
    plan_data = {"nom": "Predicció", "peticions_disponibles": 1000}
    mock_coordinator.data = {
        "quotes": {
            "plans": [
                {"nom": "Predicció", "consultesRestants": 1000}
            ]
        }
    }
    
    sensor = MeteocatEstimatedDaysRemainingSensor(
        mock_coordinator,
        mock_entry,
        plan_data,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    assert sensor.native_value == 9999

def test_days_remaining_no_data(mock_coordinator, mock_entry):
    """Test calculation when data is missing."""
    mock_coordinator.data = {}
    
    plan_data = {"nom": "Predicció", "peticions_disponibles": 1000}
    
    sensor = MeteocatEstimatedDaysRemainingSensor(
        mock_coordinator,
        mock_entry,
        plan_data,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    assert sensor.native_value is None

def test_days_remaining_plan_not_found(mock_coordinator, mock_entry):
    """Test calculation when plan is not in coordinator data."""
    # Coordinator has Predicció, XEMA, Quota
    plan_data = {"nom": "NonExistentPlan", "peticions_disponibles": 1000}
    
    sensor = MeteocatEstimatedDaysRemainingSensor(
        mock_coordinator,
        mock_entry,
        plan_data,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    assert sensor.native_value is None
