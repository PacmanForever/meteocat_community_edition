"""Test local weather condition logic coverage."""
from unittest.mock import MagicMock, patch
import pytest
from homeassistant.const import STATE_UNKNOWN, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.components.weather import (
    ATTR_CONDITION_SUNNY,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_RAINY,
)

from custom_components.meteocat_community_edition.weather import MeteocatLocalWeather
from custom_components.meteocat_community_edition.const import (
    CONF_MUNICIPALITY_NAME,
    DOMAIN,
)

@pytest.fixture
def mock_coordinator():
    """Mock the coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "forecast": {
            "dies": [
                {
                    "variables": {
                        "estatCel": {"valor": 1},  # Sunny
                        "precipitacio": {"valor": 0},
                    }
                }
            ]
        }
    }
    return coordinator

@pytest.fixture
def mock_config_entry():
    """Mock the config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        CONF_MUNICIPALITY_NAME: "Test Municipality",
        "mapping_type": "meteocat",
        "custom_condition_mapping": {},
        "local_condition_entity": "sensor.local_condition",
    }
    return entry

async def test_local_condition_entity_numeric_state(hass: HomeAssistant, mock_coordinator, mock_config_entry):
    """Test local condition entity returning a numeric state that maps to a condition."""
    # Setup entity
    weather = MeteocatLocalWeather(mock_coordinator, mock_config_entry)
    weather.hass = hass

    # Patch _is_night to return False to ensure we get "sunny" and not "clear-night"
    with patch.object(MeteocatLocalWeather, "_is_night", return_value=False):
        # Mock sensor state "1" (Sunny in default mapping)
        hass.states.async_set("sensor.local_condition", "1")
        
        assert weather.condition == "sunny"

async def test_local_condition_entity_valid_string_state(hass: HomeAssistant, mock_coordinator, mock_config_entry):
    """Test local condition entity returning a valid condition string."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_config_entry)
    weather.hass = hass

    # Mock sensor state "rainy"
    hass.states.async_set("sensor.local_condition", "rainy")
    
    assert weather.condition == "rainy"

async def test_local_condition_entity_custom_mapping(hass: HomeAssistant, mock_coordinator, mock_config_entry):
    """Test local condition entity with custom mapping."""
    # update config for custom mapping
    mock_config_entry.data["mapping_type"] = "custom"
    mock_config_entry.data["custom_condition_mapping"] = {"100": "pouring"}
    
    weather = MeteocatLocalWeather(mock_coordinator, mock_config_entry)
    weather.hass = hass

    # Mock sensor state "100"
    hass.states.async_set("sensor.local_condition", "100")
    
    assert weather.condition == "pouring"

async def test_local_condition_entity_invalid_state_returns_none(hass: HomeAssistant, mock_coordinator, mock_config_entry):
    """Test that invalid state in condition entity returns None (blocking fallback)."""
    # Add rain sensor to prove it's NOT used
    mock_config_entry.data["sensor_rain"] = "sensor.rain_gauge"
    
    weather = MeteocatLocalWeather(mock_coordinator, mock_config_entry)
    weather.hass = hass
    weather._sensors["rain"] = "sensor.rain_gauge"

    # Local condition invalid
    hass.states.async_set("sensor.local_condition", "invalid_garbage")
    # Rain sensor active
    hass.states.async_set("sensor.rain_gauge", "5.0")
    
    # Logic returns None when parsing fails for configured entity
    assert weather.condition is None

async def test_rain_sensor_fallback_when_condition_entity_missing(hass: HomeAssistant, mock_coordinator, mock_config_entry):
    """Test rain sensor logic when condition entity is not configured."""
    # Remove condition entity
    mock_config_entry.data["local_condition_entity"] = None
    
    # Add rain sensor
    mock_config_entry.data["sensor_rain"] = "sensor.rain_gauge"
    
    weather = MeteocatLocalWeather(mock_coordinator, mock_config_entry)
    weather.hass = hass
    # Manually mimic setup
    weather._local_condition_entity = None 
    weather._sensors["rain"] = "sensor.rain_gauge"

    # Rain sensor active > 0
    hass.states.async_set("sensor.rain_gauge", "5.0")
    
    # Should fall through Step 1 and hit Step 2
    assert weather.condition == "rainy"

async def test_local_condition_entity_unknown_unavailable(hass: HomeAssistant, mock_coordinator, mock_config_entry):
    """Test local condition entity being unknown or unavailable."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_config_entry)
    weather.hass = hass

    with patch.object(MeteocatLocalWeather, "_is_night", return_value=False):
        hass.states.async_set("sensor.local_condition", STATE_UNKNOWN)
        
        # Should fall back to forecast (sunny/cloudy from mock_coordinator)
        assert weather.condition == "sunny" 

async def test_local_condition_entity_mapping_miss(hass: HomeAssistant, mock_coordinator, mock_config_entry):
    """Test local condition entity value not found in mapping."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_config_entry)
    weather.hass = hass

    # "999" is not in default map
    hass.states.async_set("sensor.local_condition", "999")
    
    assert weather.condition is None

async def test_get_sensor_value_error_handling(hass: HomeAssistant, mock_coordinator, mock_config_entry):
    """Test _get_sensor_value error cases."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_config_entry)
    weather.hass = hass
    weather._sensors["temp"] = "sensor.temp"

    # Case 1: State is not a number
    hass.states.async_set("sensor.temp", "not_a_number")
    assert weather._get_sensor_value("temp") is None

    # Case 2: Entity does not exist
    # (no state set)
    assert weather._get_sensor_value("non_existent") is None

async def test_forecast_daily_full_attributes(hass: HomeAssistant, mock_coordinator, mock_config_entry):
    """Test async_forecast_daily with all attributes to hit parsing logic."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_config_entry)
    
    # beef up the coordinator data
    mock_coordinator.data["forecast"] = {
        "dies": [
            {
                "data": "2023-10-27Z",
                "variables": {
                    "tmin": {"valor": 10.0},
                    "tmax": {"valor": 20.0},
                    "estatCel": {"valor": 1},
                    "precipitacio": {"valor": 50}, # 50% probability
                }
            }
        ]
    }
    
    forecast = await weather.async_forecast_daily()
    assert len(forecast) == 1
    item = forecast[0]
    assert item["native_templow"] == 10.0
    assert item["native_temperature"] == 20.0
    assert item["condition"] == "sunny"
    assert item["precipitation_probability"] == 50.0

async def test_forecast_daily_bad_data(hass: HomeAssistant, mock_coordinator, mock_config_entry):
    """Test async_forecast_daily with bad data types."""
    weather = MeteocatLocalWeather(mock_coordinator, mock_config_entry)
    
    mock_coordinator.data["forecast"] = {
        "dies": [
            {
                "data": "2023-10-27Z",
                "variables": {
                    "tmin": {"valor": "bad"},
                    "tmax": {"valor": "bad"},
                    "precipitacio": {"valor": "bad"},
                }
            }
        ]
    }
    
    forecast = await weather.async_forecast_daily()
    assert len(forecast) == 1
    # Should have datetime but missing other values
    assert "native_templow" not in forecast[0]