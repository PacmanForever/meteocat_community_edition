"""Tests for sensor setup and conditional sensor creation."""
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest

from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    MODE_ESTACIO,
    MODE_MUNICIPI,
)
from custom_components.meteocat_community_edition.sensor import async_setup_entry


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {DOMAIN: {}}
    return hass


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "quotes": {
            "plans": [
                {"nom": "XEMA", "consums": {"disponibles": 1000}},
                {"nom": "Predicció", "consums": {"disponibles": 1000}},
                {"nom": "Referència", "consums": {"disponibles": 1000}},
                {"nom": "XDDE", "consums": {"disponibles": 1000}},
            ]
        }
    }
    return coordinator


@pytest.mark.asyncio
async def test_station_mode_creates_all_geographic_sensors_when_data_available(mock_hass, mock_coordinator):
    """Test that MODE_ESTACIO creates all geographic sensors when data is available."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "mode": MODE_ESTACIO,
        "station_code": "YM",
        "station_name": "Granollers",
        "comarca_code": "35",
        "comarca_name": "Vallès Oriental",
        "station_municipality_code": "081100",
        "station_municipality_name": "Granollers",
        "station_provincia_code": "08",
        "station_provincia_name": "Barcelona",
    }
    entry.options = {}
    
    mock_hass.data[DOMAIN][entry.entry_id] = mock_coordinator
    
    entities_added = []
    
    def mock_add_entities(entities):
        entities_added.extend(entities)
    
    await async_setup_entry(mock_hass, entry, mock_add_entities)
    
    # Verify all geographic sensors were created
    sensor_classes = [type(entity).__name__ for entity in entities_added]
    
    # Should have comarca (always), municipality (conditional), and provincia (conditional)
    assert "MeteocatStationComarcaNameSensor" in sensor_classes
    assert "MeteocatStationMunicipalityNameSensor" in sensor_classes
    assert "MeteocatStationProvinciaNameSensor" in sensor_classes
    
    # Should also have coordinate sensors
    assert "MeteocatAltitudeSensor" in sensor_classes
    assert "MeteocatLatitudeSensor" in sensor_classes
    assert "MeteocatLongitudeSensor" in sensor_classes


@pytest.mark.asyncio
async def test_station_mode_skips_municipality_when_not_available(mock_hass, mock_coordinator):
    """Test that MODE_ESTACIO doesn't create municipality sensor when data not available."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "mode": MODE_ESTACIO,
        "station_code": "YM",
        "station_name": "Granollers",
        "comarca_code": "35",
        "comarca_name": "Vallès Oriental",
        # No station_municipality_name or station_provincia_name
    }
    entry.options = {}
    
    mock_hass.data[DOMAIN][entry.entry_id] = mock_coordinator
    
    entities_added = []
    
    def mock_add_entities(entities):
        entities_added.extend(entities)
    
    await async_setup_entry(mock_hass, entry, mock_add_entities)
    
    sensor_classes = [type(entity).__name__ for entity in entities_added]
    
    # Should have comarca (always)
    assert "MeteocatStationComarcaNameSensor" in sensor_classes
    
    # Should NOT have municipality or provincia
    assert "MeteocatStationMunicipalityNameSensor" not in sensor_classes
    assert "MeteocatStationProvinciaNameSensor" not in sensor_classes


@pytest.mark.asyncio
async def test_municipality_mode_creates_all_sensors_when_data_available(mock_hass, mock_coordinator):
    """Test that MODE_MUNICIPI creates all sensors when data is available."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "080193",
        "municipality_name": "Barcelona",
        "comarca_code": "13",
        "comarca_name": "Barcelonès",
        "municipality_lat": 41.3851,
        "municipality_lon": 2.1734,
        "provincia_code": "08",
        "provincia_name": "Barcelona",
    }
    entry.options = {}
    
    mock_hass.data[DOMAIN][entry.entry_id] = mock_coordinator
    
    entities_added = []
    
    def mock_add_entities(entities):
        entities_added.extend(entities)
    
    await async_setup_entry(mock_hass, entry, mock_add_entities)
    
    sensor_classes = [type(entity).__name__ for entity in entities_added]
    
    # Should have municipality and comarca (always)
    assert "MeteocatMunicipalityNameSensor" in sensor_classes
    assert "MeteocatComarcaNameSensor" in sensor_classes
    
    # Should have coordinates (conditional)
    assert "MeteocatMunicipalityLatitudeSensor" in sensor_classes
    assert "MeteocatMunicipalityLongitudeSensor" in sensor_classes
    
    # Should have provincia (conditional)
    assert "MeteocatProvinciaNameSensor" in sensor_classes


@pytest.mark.asyncio
async def test_municipality_mode_skips_coordinates_when_not_available(mock_hass, mock_coordinator):
    """Test that MODE_MUNICIPI doesn't create coordinate sensors when data not available."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "080193",
        "municipality_name": "Barcelona",
        "comarca_code": "13",
        "comarca_name": "Barcelonès",
        # No municipality_lat, municipality_lon, or provincia_name
    }
    entry.options = {}
    
    mock_hass.data[DOMAIN][entry.entry_id] = mock_coordinator
    
    entities_added = []
    
    def mock_add_entities(entities):
        entities_added.extend(entities)
    
    await async_setup_entry(mock_hass, entry, mock_add_entities)
    
    sensor_classes = [type(entity).__name__ for entity in entities_added]
    
    # Should have municipality and comarca (always)
    assert "MeteocatMunicipalityNameSensor" in sensor_classes
    assert "MeteocatComarcaNameSensor" in sensor_classes
    
    # Should NOT have coordinates or provincia
    assert "MeteocatMunicipalityLatitudeSensor" not in sensor_classes
    assert "MeteocatMunicipalityLongitudeSensor" not in sensor_classes
    assert "MeteocatProvinciaNameSensor" not in sensor_classes


@pytest.mark.asyncio
async def test_municipality_mode_creates_lat_without_lon(mock_hass, mock_coordinator):
    """Test that latitude sensor is created even if longitude is missing."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "mode": MODE_MUNICIPI,
        "municipality_code": "080193",
        "municipality_name": "Barcelona",
        "comarca_code": "13",
        "comarca_name": "Barcelonès",
        "municipality_lat": 41.3851,
        # No municipality_lon
    }
    entry.options = {}
    
    mock_hass.data[DOMAIN][entry.entry_id] = mock_coordinator
    
    entities_added = []
    
    def mock_add_entities(entities):
        entities_added.extend(entities)
    
    await async_setup_entry(mock_hass, entry, mock_add_entities)
    
    sensor_classes = [type(entity).__name__ for entity in entities_added]
    
    # Should have latitude
    assert "MeteocatMunicipalityLatitudeSensor" in sensor_classes
    
    # Should NOT have longitude
    assert "MeteocatMunicipalityLongitudeSensor" not in sensor_classes
