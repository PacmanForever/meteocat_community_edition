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
    MeteocatLastUpdateSensor,
    MeteocatNextUpdateSensor,
    MeteocatUpdateTimeSensor,
    MeteocatAltitudeSensor,
    MeteocatLatitudeSensor,
    MeteocatLongitudeSensor,
    MeteocatMunicipalityNameSensor,
    MeteocatComarcaNameSensor,
    MeteocatProvinciaNameSensor,
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
    }
    coordinator.last_successful_update_time = datetime(2025, 11, 24, 12, 0, 0)
    coordinator.next_scheduled_update = datetime(2025, 11, 24, 20, 0, 0)  # Next update at 20:00
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
    entry.options = {}
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
    
    assert sensor.name == "Granollers Predicció Diària"
    assert sensor.native_value is not None  # El valor depèn de les dades del coordinator


def test_forecast_sensor_hourly(mock_coordinator, mock_entry):
    """Test hourly forecast sensor."""
    sensor = MeteocatForecastSensor(
        mock_coordinator,
        mock_entry,
        "Granollers YM",
        "Granollers",
        "hourly"
    )
    
    assert sensor.name == "Granollers Predicció Horària"
    # Should return current hour's value
    assert sensor.native_value is not None


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
    # Should use coordinator.next_scheduled_update
    assert sensor.native_value == datetime(2025, 11, 24, 20, 0, 0)
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
    plan_data = {"nom": "Predicció", "requests_left": 950}
    quota_sensor = MeteocatQuotaSensor(
        mock_coordinator,
        mock_entry,
        plan_data,
        "Granollers",
        "Granollers YM",
        MODE_ESTACIO,
        "YM"
    )
    
    # All diagnostic sensors should have DIAGNOSTIC category
    assert update_time_sensor._attr_entity_category == EntityCategory.DIAGNOSTIC
    assert last_sensor._attr_entity_category == EntityCategory.DIAGNOSTIC
    assert next_sensor._attr_entity_category == EntityCategory.DIAGNOSTIC
    assert quota_sensor._attr_entity_category == EntityCategory.DIAGNOSTIC


def test_altitude_sensor(mock_coordinator, mock_entry):
    """Test altitude sensor."""
    mock_coordinator.data = {
        "station": {
            "codi": "YM",
            "nom": "Barcelona",
            "altitud": 95,
        }
    }
    
    sensor = MeteocatAltitudeSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona YM",
        "YM"
    )
    
    assert sensor.native_value == 95
    assert sensor.native_unit_of_measurement == "m"
    assert sensor.icon == "mdi:elevation-rise"
    assert sensor.unique_id == f"{mock_entry.entry_id}_altitude"
    assert sensor.name == "Altitud"


def test_altitude_sensor_no_data(mock_coordinator, mock_entry):
    """Test altitude sensor with no station data."""
    mock_coordinator.data = {}
    
    sensor = MeteocatAltitudeSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona YM",
        "YM"
    )
    
    assert sensor.native_value is None


def test_latitude_sensor(mock_coordinator, mock_entry):
    """Test latitude sensor."""
    mock_coordinator.data = {
        "station": {
            "codi": "YM",
            "nom": "Barcelona",
            "coordenades": {
                "latitud": 41.3851,
                "longitud": 2.1734,
            }
        }
    }
    
    sensor = MeteocatLatitudeSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona YM",
        "YM"
    )
    
    assert sensor.native_value == 41.3851
    assert sensor.native_unit_of_measurement == "°"
    assert sensor.icon == "mdi:latitude"
    assert sensor.unique_id == f"{mock_entry.entry_id}_latitude"
    assert sensor.name == "Latitud"


def test_latitude_sensor_no_data(mock_coordinator, mock_entry):
    """Test latitude sensor with no station data."""
    mock_coordinator.data = {}
    
    sensor = MeteocatLatitudeSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona YM",
        "YM"
    )
    
    assert sensor.native_value is None


def test_longitude_sensor(mock_coordinator, mock_entry):
    """Test longitude sensor."""
    mock_coordinator.data = {
        "station": {
            "codi": "YM",
            "nom": "Barcelona",
            "coordenades": {
                "latitud": 41.3851,
                "longitud": 2.1734,
            }
        }
    }
    
    sensor = MeteocatLongitudeSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona YM",
        "YM"
    )
    
    assert sensor.native_value == 2.1734
    assert sensor.native_unit_of_measurement == "°"
    assert sensor.icon == "mdi:longitude"
    assert sensor.unique_id == f"{mock_entry.entry_id}_longitude"
    assert sensor.name == "Longitud"


def test_longitude_sensor_no_data(mock_coordinator, mock_entry):
    """Test longitude sensor with no station data."""
    mock_coordinator.data = {}
    
    sensor = MeteocatLongitudeSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona YM",
        "YM"
    )
    
    assert sensor.native_value is None


def test_municipality_name_sensor(mock_coordinator, mock_entry):
    """Test municipality name sensor."""
    # Configure entry for municipality mode
    mock_entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "080193",
        "municipality_name": "Barcelona",
        "comarca_name": "Barcelonès",
    }
    
    sensor = MeteocatMunicipalityNameSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona",
        "080193"
    )
    
    assert sensor.native_value == "Barcelona"
    assert sensor.icon == "mdi:city"
    assert sensor.unique_id == f"{mock_entry.entry_id}_municipality_name"
    assert sensor.name == "Municipi"


def test_municipality_name_sensor_no_data(mock_coordinator, mock_entry):
    """Test municipality name sensor with no data."""
    # Configure entry for municipality mode but without municipality_name
    mock_entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "080193",
    }
    
    sensor = MeteocatMunicipalityNameSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona",
        "080193"
    )
    
    # Should return empty string when municipality_name is not in config
    assert sensor.native_value == ""


def test_comarca_name_sensor(mock_coordinator, mock_entry):
    """Test comarca name sensor."""
    # Configure entry for municipality mode
    mock_entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "080193",
        "municipality_name": "Barcelona",
        "comarca_name": "Barcelonès",
    }
    
    sensor = MeteocatComarcaNameSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona",
        "080193"
    )
    
    assert sensor.native_value == "Barcelonès"
    assert sensor.icon == "mdi:map"
    assert sensor.unique_id == f"{mock_entry.entry_id}_comarca_name"
    assert sensor.name == "Comarca"


def test_comarca_name_sensor_no_data(mock_coordinator, mock_entry):
    """Test comarca name sensor with no data."""
    # Configure entry for municipality mode but without comarca_name
    mock_entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "080193",
    }
    
    sensor = MeteocatComarcaNameSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona",
        "080193"
    )
    
    # Should return empty string when comarca_name is not in config
    assert sensor.native_value == ""


# Tests for MODE_ESTACIO geographic sensors

def test_station_comarca_name_sensor():
    """Test station comarca name sensor."""
    from custom_components.meteocat_community_edition.sensor import MeteocatStationComarcaNameSensor
    from unittest.mock import MagicMock
    
    mock_coordinator = MagicMock()
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {
        "mode": MODE_ESTACIO,
        "station_code": "YM",
        "comarca_name": "Vallès Oriental",
    }
    mock_entry.options = {}
    
    sensor = MeteocatStationComarcaNameSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        "YM"
    )
    
    assert sensor.native_value == "Vallès Oriental"
    assert sensor.icon == "mdi:map"


def test_station_municipality_name_sensor():
    """Test station municipality name sensor."""
    from custom_components.meteocat_community_edition.sensor import MeteocatStationMunicipalityNameSensor
    from unittest.mock import MagicMock
    
    mock_coordinator = MagicMock()
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {
        "mode": MODE_ESTACIO,
        "station_code": "YM",
        "station_municipality_name": "Granollers",
    }
    mock_entry.options = {}
    
    sensor = MeteocatStationMunicipalityNameSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        "YM"
    )
    
    assert sensor.native_value == "Granollers"
    assert sensor.icon == "mdi:city"


def test_station_provincia_name_sensor():
    """Test station province name sensor."""
    from custom_components.meteocat_community_edition.sensor import MeteocatStationProvinciaNameSensor
    from unittest.mock import MagicMock
    
    mock_coordinator = MagicMock()
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {
        "mode": MODE_ESTACIO,
        "station_code": "YM",
        "station_provincia_name": "Barcelona",
    }
    mock_entry.options = {}
    
    sensor = MeteocatStationProvinciaNameSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        "YM"
    )
    
    assert sensor.native_value == "Barcelona"
    assert sensor.icon == "mdi:map-marker-radius"


# Tests for MODE_MUNICIPI coordinate and province sensors

def test_municipality_latitude_sensor():
    """Test municipality latitude sensor."""
    from custom_components.meteocat_community_edition.sensor import MeteocatMunicipalityLatitudeSensor
    from unittest.mock import MagicMock
    
    mock_coordinator = MagicMock()
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "080193",
        "municipality_lat": 41.6,
    }
    mock_entry.options = {}
    
    sensor = MeteocatMunicipalityLatitudeSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona",
        "080193"
    )
    
    assert sensor.native_value == 41.6
    assert sensor.icon == "mdi:latitude"


def test_municipality_longitude_sensor():
    """Test municipality longitude sensor."""
    from custom_components.meteocat_community_edition.sensor import MeteocatMunicipalityLongitudeSensor
    from unittest.mock import MagicMock
    
    mock_coordinator = MagicMock()
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "080193",
        "municipality_lon": 2.3,
    }
    mock_entry.options = {}
    
    sensor = MeteocatMunicipalityLongitudeSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona",
        "080193"
    )
    
    assert sensor.native_value == 2.3
    assert sensor.icon == "mdi:longitude"


def test_municipality_provincia_name_sensor():
    """Test municipality province name sensor."""
    from custom_components.meteocat_community_edition.sensor import MeteocatProvinciaNameSensor
    from unittest.mock import MagicMock
    
    mock_coordinator = MagicMock()
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "080193",
        "provincia_name": "Barcelona",
    }
    mock_entry.options = {}
    
    sensor = MeteocatProvinciaNameSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona",
        "080193"
    )
    
    assert sensor.native_value == "Barcelona"
    assert sensor.icon == "mdi:map-marker-radius"


def test_coordinate_sensors_read_from_entry_data_cache():
    """Test that coordinate sensors read from entry.data._station_data when coordinator.data is empty."""
    from custom_components.meteocat_community_edition.sensor import (
        MeteocatLatitudeSensor,
        MeteocatLongitudeSensor,
        MeteocatAltitudeSensor,
    )
    from unittest.mock import MagicMock
    
    mock_coordinator = MagicMock()
    mock_coordinator.data = {}  # Empty data (quota exhausted scenario)
    
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {
        "mode": MODE_ESTACIO,
        "station_code": "YM",
        "_station_data": {
            "coordenades": {
                "latitud": 41.6126,
                "longitud": 2.2615,
            },
            "altitud": 95,
        }
    }
    mock_entry.options = {}
    
    # Test latitude sensor
    lat_sensor = MeteocatLatitudeSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        "YM"
    )
    assert lat_sensor.native_value == 41.6126
    
    # Test longitude sensor
    lon_sensor = MeteocatLongitudeSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        "YM"
    )
    assert lon_sensor.native_value == 2.2615
    
    # Test altitude sensor
    alt_sensor = MeteocatAltitudeSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        "YM"
    )
    assert alt_sensor.native_value == 95


def test_coordinate_sensors_prefer_coordinator_data_over_cache():
    """Test that coordinate sensors prefer coordinator.data over entry.data cache when available."""
    from custom_components.meteocat_community_edition.sensor import (
        MeteocatLatitudeSensor,
        MeteocatLongitudeSensor,
        MeteocatAltitudeSensor,
    )
    from unittest.mock import MagicMock
    
    mock_coordinator = MagicMock()
    mock_coordinator.data = {
        "station": {
            "codi": "YM",
            "coordenades": {
                "latitud": 41.9999,  # Different from cache
                "longitud": 2.9999,
            },
            "altitud": 999,
        }
    }
    
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {
        "mode": MODE_ESTACIO,
        "station_code": "YM",
        "_station_data": {
            "coordenades": {
                "latitud": 41.6126,  # Old cached value
                "longitud": 2.2615,
            },
            "altitud": 95,
        }
    }
    mock_entry.options = {}
    
    # Sensors should use coordinator.data (fresh data) not cache
    lat_sensor = MeteocatLatitudeSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        "YM"
    )
    assert lat_sensor.native_value == 41.9999
    
    lon_sensor = MeteocatLongitudeSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        "YM"
    )
    assert lon_sensor.native_value == 2.9999
    
    alt_sensor = MeteocatAltitudeSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers YM",
        "YM"
    )
    assert alt_sensor.native_value == 999


def test_municipality_provincia_name_sensor_no_data():
    """Test municipality province name sensor with no data."""
    from custom_components.meteocat_community_edition.sensor import MeteocatProvinciaNameSensor
    from unittest.mock import MagicMock
    
    mock_coordinator = MagicMock()
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "080193",
        # No provincia_name
    }
    mock_entry.options = {}
    
    sensor = MeteocatProvinciaNameSensor(
        mock_coordinator,
        mock_entry,
        "Barcelona",
        "Barcelona",
        "080193"
    )
    
    # Should return empty string when provincia_name is not in config
    assert sensor.native_value == ""
    assert sensor.icon == "mdi:map-marker-radius"
