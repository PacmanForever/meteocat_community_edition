"""Tests for Meteocat sensors."""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, AsyncMock

from custom_components.meteocat_community_edition.sensor import (
    MeteocatQuotaSensor,
    MeteocatForecastSensor,
    MeteocatUVSensor,
    MeteocatLastUpdateSensor,
    MeteocatNextUpdateSensor,
    MeteocatUpdateTimeSensor,
)
from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    MODE_ESTACIO,
    MODE_MUNICIPI,
)


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "forecast": {
            "dies": [
                {
                    "data": "2025-11-24",
                    "variables": {
                        "tmax": {"valor": 20},
                        "tmin": {"valor": 10},
                    }
                }
            ]
        },
        "forecast_hourly": {
            "dies": [
                {
                    "data": "2025-11-24",
                    "variables": {
                        "tmp": [15, 16, 17, 18],
                    }
                }
            ]
        },
        "uv_index": {
            "ine": "081131",
            "nom": "Granollers",
            "uvi": [
                {
                    "date": "2025-11-24",
                    "hours": [
                        {"hour": 12, "uvi": 5, "uvi_clouds": 4}
                    ]
                }
            ]
        }
    }
    coordinator.last_successful_update_time = datetime(2025, 11, 24, 12, 0, 0)
    coordinator.update_interval = timedelta(hours=8)
    coordinator.update_time_1 = "06:00"
    coordinator.update_time_2 = "14:00"
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
    return entry


def test_quota_sensor_normalizes_plan_names(mock_coordinator, mock_entry):
    """Test that quota sensor normalizes plan names correctly."""
    test_cases = [
        ("Prediccio_100", "Predicció", "prediccio"),
        ("Referencia_200", "Referència", "referencia"),
        ("XDDE_300", "XDDE", "xdde"),
        ("XEMA_400", "XEMA", "xema"),
    ]
    
    for plan_name, expected_display, expected_id in test_cases:
        plan_data = {"nom": plan_name, "requests_left": 950}
        
        sensor = MeteocatQuotaSensor(
            mock_coordinator,
            mock_entry,
            plan_data,
            "Granollers",
            "Granollers YM",
            MODE_ESTACIO,
            "YM"
        )
        
        display_name, plan_id = sensor._normalize_plan_name(plan_name)
        assert display_name == expected_display, f"Expected {expected_display}, got {display_name}"
        assert plan_id == expected_id, f"Expected {expected_id}, got {plan_id}"


def test_quota_sensor_entity_id_xema_mode(mock_coordinator, mock_entry):
    """Test quota sensor entity_id in XEMA mode."""
    plan_data = {"nom": "Prediccio_100", "requests_left": 950}
    
    sensor = MeteocatQuotaSensor(
        mock_coordinator,
        mock_entry,
        plan_data,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    assert sensor.entity_id == "sensor.granollers_ym_quota_prediccio"


def test_quota_sensor_entity_id_municipal_mode(mock_coordinator, mock_entry):
    """Test quota sensor entity_id in Municipal mode."""
    plan_data = {"nom": "Prediccio_100", "requests_left": 950}
    mock_entry.data["mode"] = MODE_MUNICIPI
    
    sensor = MeteocatQuotaSensor(
        mock_coordinator,
        mock_entry,
        plan_data,
        "Granollers",
        "Granollers",
        MODE_MUNICIPI,
        None
    )
    
    assert sensor.entity_id == "sensor.granollers_quota_prediccio"


def test_quota_sensor_device_info(mock_coordinator, mock_entry):
    """Test that quota sensor uses device_name in device_info."""
    plan_data = {"nom": "Prediccio_100", "requests_left": 950}
    
    sensor = MeteocatQuotaSensor(
        mock_coordinator,
        mock_entry,
        plan_data,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    device_info = sensor._attr_device_info
    assert device_info["name"] == "Granollers YM"
    assert (DOMAIN, "test_entry_id") in device_info["identifiers"]


def test_forecast_sensor_daily(mock_coordinator, mock_entry):
    """Test daily forecast sensor."""
    sensor = MeteocatForecastSensor(
        mock_coordinator,
        mock_entry,
        "Granollers YM",
        "Granollers",
        "daily"
    )
    
    assert sensor.name == "Temperatura màxima"
    assert sensor.native_value == 20


def test_forecast_sensor_hourly(mock_coordinator, mock_entry):
    """Test hourly forecast sensor."""
    sensor = MeteocatForecastSensor(
        mock_coordinator,
        mock_entry,
        "Granollers YM",
        "Granollers",
        "hourly"
    )
    
    assert sensor.name == "Temperatura"
    # Should return current hour's value
    assert sensor.native_value is not None


def test_uv_sensor(mock_coordinator, mock_entry):
    """Test UV index sensor."""
    sensor = MeteocatUVSensor(
        mock_coordinator,
        mock_entry,
        "Granollers YM",
        "Granollers"
    )
    
    assert sensor.name == "Granollers Predicció Índex UV"
    # Should return number of days with UV forecast
    assert sensor.native_value == "1 dies"


def test_last_update_sensor(mock_coordinator, mock_entry):
    """Test last update timestamp sensor."""
    sensor = MeteocatLastUpdateSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    assert sensor.name == "Última actualització"
    assert sensor.native_value == datetime(2025, 11, 24, 12, 0, 0)
    assert sensor.entity_id == "sensor.granollers_ym_last_update"


def test_next_update_sensor(mock_coordinator, mock_entry):
    """Test next update timestamp sensor."""
    sensor = MeteocatNextUpdateSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    assert sensor.name == "Pròxima actualització"
    # Should be last_update + interval
    expected = datetime(2025, 11, 24, 12, 0, 0) + timedelta(hours=8)
    assert sensor.native_value == expected
    assert sensor.entity_id == "sensor.granollers_ym_next_update"


def test_timestamp_sensors_device_info(mock_coordinator, mock_entry):
    """Test that timestamp sensors use device_name in device_info."""
    last_sensor = MeteocatLastUpdateSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    next_sensor = MeteocatNextUpdateSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    assert last_sensor._attr_device_info["name"] == "Granollers YM"
    assert next_sensor._attr_device_info["name"] == "Granollers YM"


def test_forecast_sensor_device_info(mock_coordinator, mock_entry):
    """Test that forecast sensor uses device_name in device_info."""
    sensor = MeteocatForecastSensor(
        mock_coordinator,
        mock_entry,
        "Granollers YM",
        "Granollers",
        "daily"
    )
    
    assert sensor._attr_device_info["name"] == "Granollers YM"


def test_uv_sensor_device_info(mock_coordinator, mock_entry):
    """Test that UV sensor uses device_name in device_info."""
    sensor = MeteocatUVSensor(
        mock_coordinator,
        mock_entry,
        "Granollers YM",
        "Granollers"
    )
    
    assert sensor.name == "Granollers Predicció Índex UV"
    assert sensor._attr_device_info["name"] == "Granollers YM"


def test_uv_sensor_no_data(mock_coordinator, mock_entry):
    """Test UV sensor when no UV data is available."""
    mock_coordinator.data = {}
    sensor = MeteocatUVSensor(
        mock_coordinator,
        mock_entry,
        "Granollers YM",
        "Granollers"
    )
    
    assert sensor.native_value == "0 dies"
    assert sensor.extra_state_attributes == {}


def test_uv_sensor_empty_uvi_array(mock_coordinator, mock_entry):
    """Test UV sensor when uvi array is empty."""
    mock_coordinator.data = {
        "uv_index": {
            "ine": "081131",
            "nom": "Granollers",
            "uvi": []
        }
    }
    sensor = MeteocatUVSensor(
        mock_coordinator,
        mock_entry,
        "Granollers YM",
        "Granollers"
    )
    
    assert sensor.native_value == "0 dies"


def test_uv_sensor_multiple_days(mock_coordinator, mock_entry):
    """Test UV sensor with multiple days of data."""
    mock_coordinator.data = {
        "uv_index": {
            "ine": "081131",
            "nom": "Granollers",
            "uvi": [
                {"date": "2025-11-24", "hours": [{"hour": 12, "uvi": 5}]},
                {"date": "2025-11-25", "hours": [{"hour": 12, "uvi": 6}]},
                {"date": "2025-11-26", "hours": [{"hour": 12, "uvi": 4}]}
            ]
        }
    }
    sensor = MeteocatUVSensor(
        mock_coordinator,
        mock_entry,
        "Granollers YM",
        "Granollers"
    )
    
    assert sensor.native_value == "3 dies"


def test_update_time_sensor_time_1_xema_mode(mock_coordinator, mock_entry):
    """Test update time sensor 1 in XEMA mode."""
    sensor = MeteocatUpdateTimeSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        1,
        "YM"
    )
    
    # Check entity_id includes station code
    assert sensor.entity_id == "sensor.granollers_ym_update_time_1"
    
    # Check name
    assert sensor._attr_name == "Hora d'actualització 1"
    
    # Check value comes from coordinator
    assert sensor.native_value == "06:00"
    
    # Check device_info
    assert sensor._attr_device_info["name"] == "Granollers YM"
    assert (DOMAIN, "test_entry_id") in sensor._attr_device_info["identifiers"]
    
    # Check icon
    assert sensor.icon == "mdi:clock-time-four-outline"


def test_update_time_sensor_time_2_xema_mode(mock_coordinator, mock_entry):
    """Test update time sensor 2 in XEMA mode."""
    sensor = MeteocatUpdateTimeSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        2,
        "YM"
    )
    
    # Check entity_id includes station code
    assert sensor.entity_id == "sensor.granollers_ym_update_time_2"
    
    # Check name
    assert sensor._attr_name == "Hora d'actualització 2"
    
    # Check value comes from coordinator
    assert sensor.native_value == "14:00"


def test_update_time_sensor_municipal_mode(mock_coordinator):
    """Test update time sensors in Municipal mode."""
    entry = MagicMock()
    entry.entry_id = "test_entry_municipal"
    entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "081131",
        "municipality_name": "Granollers",
    }
    
    sensor_1 = MeteocatUpdateTimeSensor(
        mock_coordinator,
        entry,
        "Granollers",
        "Granollers",
        MODE_MUNICIPI,
        1,
        None
    )
    
    sensor_2 = MeteocatUpdateTimeSensor(
        mock_coordinator,
        entry,
        "Granollers",
        "Granollers",
        MODE_MUNICIPI,
        2,
        None
    )
    
    # Check entity_ids do NOT include station code
    assert sensor_1.entity_id == "sensor.granollers_update_time_1"
    assert sensor_2.entity_id == "sensor.granollers_update_time_2"
    
    # Check values
    assert sensor_1.native_value == "06:00"
    assert sensor_2.native_value == "14:00"


def test_update_time_sensor_unique_id(mock_coordinator, mock_entry):
    """Test update time sensors have unique IDs."""
    sensor_1 = MeteocatUpdateTimeSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        1,
        "YM"
    )
    
    sensor_2 = MeteocatUpdateTimeSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        2,
        "YM"
    )
    
    # Should have different unique IDs
    assert sensor_1._attr_unique_id == "test_entry_id_update_time_1"
    assert sensor_2._attr_unique_id == "test_entry_id_update_time_2"
    assert sensor_1._attr_unique_id != sensor_2._attr_unique_id


def test_diagnostic_sensors_entity_category(mock_coordinator, mock_entry):
    """Test all diagnostic sensors have correct entity category."""
    from homeassistant.helpers.entity import EntityCategory
    
    # Update time sensor
    update_time_sensor = MeteocatUpdateTimeSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        1,
        "YM"
    )
    
    # Timestamp sensors (last and next update)
    last_sensor = MeteocatLastUpdateSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    next_sensor = MeteocatNextUpdateSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    # Quota sensor
    quota_sensor = MeteocatQuotaSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        "Predicció",
        MODE_ESTACIO,
        "YM"
    )
    
    # All diagnostic sensors should have DIAGNOSTIC category
    assert update_time_sensor._attr_entity_category == EntityCategory.DIAGNOSTIC
    assert last_sensor._attr_entity_category == EntityCategory.DIAGNOSTIC
    assert next_sensor._attr_entity_category == EntityCategory.DIAGNOSTIC
    assert quota_sensor._attr_entity_category == EntityCategory.DIAGNOSTIC
