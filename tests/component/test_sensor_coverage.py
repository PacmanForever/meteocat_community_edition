"""Coverage tests for sensor setup and missing branches."""
import pytest
from unittest.mock import MagicMock, patch, call
from homeassistant.helpers.entity_registry import async_get
from custom_components.meteocat_community_edition.sensor import async_setup_entry
from custom_components.meteocat_community_edition.const import DOMAIN, MODE_LOCAL, MODE_EXTERNAL, CONF_MODE

async def test_async_setup_entry_local_mode_coverage(hass):
    """Test async_setup_entry coverage for local mode conditions."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_MODE: MODE_LOCAL,
        "municipality_name": "Test Muni",
        "provincia_name": "Test Prov",
        "municipality_lat": 41.0,
        "municipality_lon": 2.0
    }
    
    coordinator = MagicMock()
    coordinator.enable_forecast_hourly = True
    coordinator.enable_forecast_daily = True
    coordinator.update_time_3 = "20:00"
    coordinator.data = {
        "quotes": {
            "plans": [
                {"nom": "referencia"}, # Ignored
                {"nom": "xema"}, # Ignored for local
                {"nom": "prediccio"} # Used
            ]
        }
    }
    
    hass.data[DOMAIN] = {entry.entry_id: coordinator}
    async_add_entities = MagicMock()
    
    with patch("custom_components.meteocat_community_edition.sensor.er.async_get", return_value=MagicMock()) as mock_er:
        mock_registry = mock_er.return_value
        mock_registry.entities = {}
        
        await async_setup_entry(hass, entry, async_add_entities)
        
        assert async_add_entities.called
        entities = async_add_entities.call_args[0][0]
        # Check if various sensors are added based on conditions
        # We expect: forecast (2), muni (2), prov (1), lat/lon (2), quota (1+1), updates (4+1)
        assert len(entities) > 10 

async def test_async_setup_entry_external_mode_coverage(hass):
    """Test async_setup_entry coverage for external mode conditions."""
    entry = MagicMock()
    entry.entry_id = "test_entry_ext"
    entry.data = {
        CONF_MODE: MODE_EXTERNAL,
        "station_name": "Station X",
        "station_municipality_name": "Muni X",
        "station_provincia_name": "Prov X"
    }
    
    coordinator = MagicMock()
    coordinator.enable_forecast_hourly = False
    coordinator.enable_forecast_daily = False # Not added in external
    coordinator.update_time_3 = None
    coordinator.data = {}
    
    hass.data[DOMAIN] = {entry.entry_id: coordinator}
    async_add_entities = MagicMock()
    
    with patch("custom_components.meteocat_community_edition.sensor.er.async_get", return_value=MagicMock()):
        await async_setup_entry(hass, entry, async_add_entities)
        
        assert async_add_entities.called
        entities = async_add_entities.call_args[0][0]
        # Check XEMA sensors
        xema_count = len([e for e in entities if hasattr(e, "_variable_code")])
        assert xema_count > 0

async def test_async_setup_entry_registry_error_handling(hass):
    """Test registry error handling block."""
    entry = MagicMock()
    entry.entry_id = "test_entry_err"
    entry.data = {CONF_MODE: MODE_LOCAL}
    
    coordinator = MagicMock()
    coordinator.data = {}
    hass.data[DOMAIN] = {entry.entry_id: coordinator}
    async_add_entities = MagicMock()
    
    # Mock registry raising exception
    with patch("custom_components.meteocat_community_edition.sensor.er.async_get", side_effect=Exception("Registry Error")):
        await async_setup_entry(hass, entry, async_add_entities)
        # Should proceed to add entities despite warning
        assert async_add_entities.called

async def test_async_setup_registry_enable_entities(hass):
    """Test forcing enable of disabled entities."""
    entry = MagicMock()
    entry.entry_id = "test_entry_enable"
    entry.data = {CONF_MODE: MODE_LOCAL}
    
    coordinator = MagicMock()
    coordinator.data = {}
    hass.data[DOMAIN] = {entry.entry_id: coordinator}
    async_add_entities = MagicMock()
    
    mock_entity = MagicMock()
    mock_entity.config_entry_id = entry.entry_id
    mock_entity.disabled = True
    mock_entity.unique_id = "some_unique_id_municipality_name"
    mock_entity.entity_id = "sensor.test"
    
    mock_registry = MagicMock()
    mock_registry.entities = {"sensor.test": mock_entity}
    mock_registry.async_update_entity = MagicMock()
    
    with patch("custom_components.meteocat_community_edition.sensor.er.async_get", return_value=mock_registry):
        await async_setup_entry(hass, entry, async_add_entities)
        
        mock_registry.async_update_entity.assert_called_with("sensor.test", disabled_by=None)
