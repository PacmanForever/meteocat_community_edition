"""Tests for Meteocat availability on error."""
import pytest
from unittest.mock import MagicMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.meteocat_community_edition.button import MeteocatRefreshForecastButton
from custom_components.meteocat_community_edition.sensor import (
    MeteocatMunicipalityNameSensor,
    MeteocatComarcaNameSensor,
    MeteocatMunicipalityLatitudeSensor,
    MeteocatMunicipalityLongitudeSensor,
    MeteocatProvinciaNameSensor,
    MeteocatStationComarcaNameSensor,
    MeteocatStationMunicipalityNameSensor,
    MeteocatStationProvinciaNameSensor,
    MeteocatLastUpdateSensor,
    MeteocatNextUpdateSensor,
    MeteocatUpdateTimeSensor,
    MeteocatNextForecastUpdateSensor,
    MeteocatLastForecastUpdateSensor,
)
from custom_components.meteocat_community_edition.const import (
    CONF_MUNICIPALITY_NAME,
    CONF_COMARCA_NAME,
    MODE_LOCAL,
    MODE_EXTERNAL,
)

@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator with failed update."""
    coordinator = MagicMock()
    coordinator.last_update_success = False
    coordinator.last_exception = UpdateFailed("API Error")
    # Mock diagnostic attributes
    coordinator.last_successful_update_time = "2023-01-01T12:00:00"
    coordinator.next_scheduled_update = "2023-01-01T13:00:00"
    coordinator.update_time_1 = "08:00"
    coordinator.update_time_2 = "20:00"
    coordinator.update_time_3 = None
    coordinator.next_forecast_update = "2023-01-01T14:00:00"
    coordinator.last_forecast_update = "2023-01-01T10:00:00"
    return coordinator

async def test_button_available_on_error(hass: HomeAssistant, mock_coordinator):
    """Test that refresh button is available even when coordinator fails."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "station_code": "X4",
    }
    
    button = MeteocatRefreshForecastButton(
        mock_coordinator, 
        entry, 
        "Test Entity", 
        "Test Device", 
        MODE_LOCAL
    )
    button.hass = hass
    
    # Should be available despite coordinator failure
    assert button.available is True

async def test_location_sensors_available_on_error(hass: HomeAssistant, mock_coordinator):
    """Test that location sensors are available even when coordinator fails."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_MUNICIPALITY_NAME: "Test City",
        CONF_COMARCA_NAME: "Test Comarca",
        "municipality_lat": 41.0,
        "municipality_lon": 2.0,
        "provincia_name": "Test Province",
        "station_municipality_name": "Station City",
        "station_provincia_name": "Station Province",
        "comarca_name": "Station Comarca",
    }
    
    # Municipality Sensor
    municipality_sensor = MeteocatMunicipalityNameSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        "08001"
    )
    municipality_sensor.hass = hass
    
    # Comarca Sensor
    comarca_sensor = MeteocatComarcaNameSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        "13"
    )
    comarca_sensor.hass = hass

    # Latitude Sensor
    lat_sensor = MeteocatMunicipalityLatitudeSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        "08001"
    )
    lat_sensor.hass = hass

    # Longitude Sensor
    lon_sensor = MeteocatMunicipalityLongitudeSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        "08001"
    )
    lon_sensor.hass = hass

    # Provincia Sensor
    prov_sensor = MeteocatProvinciaNameSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        "08001"
    )
    prov_sensor.hass = hass

    # Station Comarca Sensor
    station_comarca_sensor = MeteocatStationComarcaNameSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        "X4"
    )
    station_comarca_sensor.hass = hass

    # Station Municipality Sensor
    station_mun_sensor = MeteocatStationMunicipalityNameSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        "X4"
    )
    station_mun_sensor.hass = hass

    # Station Provincia Sensor
    station_prov_sensor = MeteocatStationProvinciaNameSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        "X4"
    )
    station_prov_sensor.hass = hass
    
    # All should be available because they use static data
    assert municipality_sensor.available is True
    assert comarca_sensor.available is True
    assert lat_sensor.available is True
    assert lon_sensor.available is True
    assert prov_sensor.available is True
    assert station_comarca_sensor.available is True
    assert station_mun_sensor.available is True
    assert station_prov_sensor.available is True

async def test_diagnostic_sensors_available_on_error(hass: HomeAssistant, mock_coordinator):
    """Test that diagnostic sensors are available even when coordinator fails."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {}
    
    # Last Update Sensor
    last_update = MeteocatLastUpdateSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        MODE_LOCAL
    )
    last_update.hass = hass
    
    # Next Update Sensor
    next_update = MeteocatNextUpdateSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        MODE_LOCAL
    )
    next_update.hass = hass
    
    # Update Time Sensor
    update_time = MeteocatUpdateTimeSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        MODE_LOCAL,
        1
    )
    update_time.hass = hass
    
    # Next Forecast Update Sensor
    next_forecast = MeteocatNextForecastUpdateSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        "X4"
    )
    next_forecast.hass = hass
    
    # Last Forecast Update Sensor
    last_forecast = MeteocatLastForecastUpdateSensor(
        mock_coordinator,
        entry,
        "Test Entity",
        "Test Device",
        "X4"
    )
    last_forecast.hass = hass
    
    # All should be available
    assert last_update.available is True
    assert next_update.available is True
    assert update_time.available is True
    assert next_forecast.available is True
    assert last_forecast.available is True
