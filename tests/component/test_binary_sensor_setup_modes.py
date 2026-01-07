"""Test binary sensor setup for different modes."""
import pytest
from unittest.mock import MagicMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.meteocat_community_edition.binary_sensor import (
    async_setup_entry,
)
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
from pytest_homeassistant_custom_component.common import MockConfigEntry

@pytest.fixture
def mock_coordinator():
    """Mock the coordinator."""
    coordinator = MagicMock()
    return coordinator

async def test_binary_sensor_setup_external(hass: HomeAssistant, mock_coordinator):
    """Test setup with external mode."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_EXTERNAL,
            CONF_STATION_CODE: "X4",
            CONF_STATION_NAME: "Test Station",
        },
    )
    entry.add_to_hass(hass)
    
    hass.data[DOMAIN] = {entry.entry_id: mock_coordinator}
    
    mock_add_entities = MagicMock()
    
    await async_setup_entry(hass, entry, mock_add_entities)
    
    assert mock_add_entities.call_count == 1
    args = mock_add_entities.call_args[0][0]
    assert len(args) == 1
    entity = args[0]
    assert entity._mode == MODE_EXTERNAL
    assert entity._attr_name == "Última actualització correcte"

async def test_binary_sensor_setup_local(hass: HomeAssistant, mock_coordinator):
    """Test setup with local mode."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "080193",
            CONF_MUNICIPALITY_NAME: "Barcelona",
        },
    )
    entry.add_to_hass(hass)
    
    hass.data[DOMAIN] = {entry.entry_id: mock_coordinator}
    
    mock_add_entities = MagicMock()
    
    await async_setup_entry(hass, entry, mock_add_entities)
    
    assert mock_add_entities.call_count == 1
    args = mock_add_entities.call_args[0][0]
    assert len(args) == 1
    entity = args[0]
    assert entity._mode == MODE_LOCAL
    # Check that for local, name is just municipality name
    assert entity._attr_name == "Última actualització correcte"
