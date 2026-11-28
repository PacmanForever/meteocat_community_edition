"""Test binary sensor setup for different modes."""
import pytest
from unittest.mock import MagicMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.meteocat_community_edition.binary_sensor import (
    MeteocatCalculatedConditionBinarySensor,
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


async def test_binary_sensor_setup_adds_only_conditions_with_configured_sources(
    hass: HomeAssistant, mock_coordinator
):
    """Test local condition entities are created only when their inputs are configured."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "080193",
            CONF_MUNICIPALITY_NAME: "Barcelona",
            "sensor_temperature": "sensor.temperature",
            "sensor_humidity": "sensor.humidity",
        },
    )
    entry.add_to_hass(hass)
    hass.data[DOMAIN] = {entry.entry_id: mock_coordinator}
    mock_add_entities = MagicMock()

    await async_setup_entry(hass, entry, mock_add_entities)

    entities = mock_add_entities.call_args[0][0]
    conditions = [
        entity
        for entity in entities
        if isinstance(entity, MeteocatCalculatedConditionBinarySensor)
    ]
    assert {entity._condition for entity in conditions} == {"freezing", "muggy"}


async def test_binary_sensor_setup_local_muggy_with_configured_dew_point(
    hass: HomeAssistant, mock_coordinator
):
    """Create muggy when only a direct dew point source is configured."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_LOCAL,
            CONF_MUNICIPALITY_CODE: "080193",
            CONF_MUNICIPALITY_NAME: "Barcelona",
            "sensor_dew_point": "sensor.dew_point",
        },
    )
    entry.add_to_hass(hass)
    hass.data[DOMAIN] = {entry.entry_id: mock_coordinator}
    mock_add_entities = MagicMock()

    await async_setup_entry(hass, entry, mock_add_entities)

    conditions = [
        entity
        for entity in mock_add_entities.call_args[0][0]
        if isinstance(entity, MeteocatCalculatedConditionBinarySensor)
    ]
    assert {entity._condition for entity in conditions} == {"muggy"}


async def test_binary_sensor_setup_external_muggy_needs_no_wind(
    hass: HomeAssistant, mock_coordinator
):
    """Create external muggy when XEMA temperature and humidity are available."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MODE: MODE_EXTERNAL,
            CONF_STATION_CODE: "X4",
            CONF_STATION_NAME: "Test Station",
        },
    )
    entry.add_to_hass(hass)
    mock_coordinator.data = {
        "measurements": [
            {
                "variables": [
                    {"codi": 32, "lectures": [{"valor": 25}]},
                    {"codi": 33, "lectures": [{"valor": 70}]},
                ]
            }
        ]
    }
    hass.data[DOMAIN] = {entry.entry_id: mock_coordinator}
    mock_add_entities = MagicMock()

    await async_setup_entry(hass, entry, mock_add_entities)

    conditions = [
        entity
        for entity in mock_add_entities.call_args[0][0]
        if isinstance(entity, MeteocatCalculatedConditionBinarySensor)
    ]
    assert {entity._condition for entity in conditions} == {"freezing", "muggy"}
    muggy_sensor = next(
        entity for entity in conditions if entity._condition == "muggy"
    )
    assert muggy_sensor.available is True
    assert muggy_sensor.is_on is True
