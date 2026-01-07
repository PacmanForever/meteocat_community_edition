"""Tests to ensure 100% coverage in sensor.py."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    CONF_STATION_CODE,
    CONF_MUNICIPALITY_CODE,
    MODE_EXTERNAL,
)
from custom_components.meteocat_community_edition.coordinator import MeteocatCoordinator
from custom_components.meteocat_community_edition.sensor import (
    MeteocatQuotaSensor,
    MeteocatXemaSensor,
    MeteocatForecastSensor,
    SENSOR_TYPES,
)

MOCK_CONFIG_DATA_EXTERNAL_MODE = {
    CONF_API_KEY: "test_api_key",
    CONF_STATION_CODE: "UD",
    CONF_MUNICIPALITY_CODE: "080193",
    "mode": MODE_EXTERNAL,
}

@pytest.fixture
def mock_coordinator_full(hass):
    """Return a mocked coordinator with full data structure."""
    coordinator = MagicMock(spec=MeteocatCoordinator)
    coordinator.hass = hass
    coordinator.data = {
        "quotes": {
            "plans": [
                {
                    "nom": "prediccio",
                    "consultesRestants": 500,
                    "maxConsultes": 1000,
                    "consultesRealitzades": 500,
                    "periode": "mensual"
                }
            ]
        },
        "measurements": [
            {
                "codi": "UD",
                "variables": [
                    {
                        "codi": 32, # Temp
                        "lectures": [{"valor": 20.5}]
                    }
                ]
            }
        ],
        "forecast": {
            "dies": [
                {
                    "data": "2023-10-27Z",
                    "variables": {
                        "tmin": {"valor": "10.0"},
                        "tmax": {"valor": "20.0"},
                        "estatCel": {"valor": 1},
                        "precipitacio": {"valor": "5.0"}
                    }
                }
            ]
        },
        "forecast_hourly": {
            "dies": [
                {
                    "data": "2023-10-27Z",
                    "variables": {
                        "temp": {"valors": [{"data": "2023-10-27T00:00Z", "valor": "15.0"}]},
                        "estatCel": {"valors": [{"data": "2023-10-27T00:00Z", "valor": 1}]},
                        "precipitacio": {"valors": [{"data": "2023-10-27T00:00Z", "valor": "0.0"}]}
                    }
                }
            ]
        }
    }
    return coordinator

async def test_quota_sensor_edge_cases(hass, mock_coordinator_full):
    """Test edge cases for MeteocatQuotaSensor."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = MOCK_CONFIG_DATA_EXTERNAL_MODE
    
    plan_data = {"nom": "prediccio"}
    
    sensor = MeteocatQuotaSensor(
        mock_coordinator_full, 
        entry, 
        plan_data, 
        "Entity Name", 
        "Device Name", 
        MODE_EXTERNAL, 
        "UD"
    )
    
    # 1. Native value when quotes is None
    mock_coordinator_full.data["quotes"] = None
    assert sensor.native_value is None
    
    # 2. Native value when quotes is not dict
    mock_coordinator_full.data["quotes"] = []
    assert sensor.native_value is None
    
    # 3. Native value when plan not found
    mock_coordinator_full.data["quotes"] = {"plans": [{"nom": "other"}]}
    assert sensor.native_value is None
    
    # 4. Attributes when quotes is None
    mock_coordinator_full.data["quotes"] = None
    assert sensor.extra_state_attributes == {}
    
    # 5. Attributes when quotes is not dict
    mock_coordinator_full.data["quotes"] = []
    assert sensor.extra_state_attributes == {}
    
    # 6. Attributes when plan not found
    mock_coordinator_full.data["quotes"] = {"plans": [{"nom": "other"}]}
    assert sensor.extra_state_attributes == {}
    
    # 7. Icon logic
    mock_coordinator_full.data["quotes"] = {"plans": [{"nom": "prediccio", "consultesRestants": 0}]}
    assert sensor.icon == "mdi:alert-circle"

    mock_coordinator_full.data["quotes"] = {"plans": [{"nom": "prediccio", "consultesRestants": 99}]}
    assert sensor.icon == "mdi:alert"

    mock_coordinator_full.data["quotes"] = {"plans": [{"nom": "prediccio", "consultesRestants": 500}]}
    assert sensor.icon == "mdi:counter"

async def test_xema_sensor_edge_cases(hass, mock_coordinator_full):
    """Test edge cases for MeteocatXemaSensor."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {CONF_STATION_CODE: "UD"}
    
    # Variable code 32 is Temperature
    sensor = MeteocatXemaSensor(mock_coordinator_full, entry, "Temperature", 32)
    
    # 1. Missing measurements
    mock_coordinator_full.data["measurements"] = None
    assert sensor.native_value is None
    
    # 2. Measurements not list
    mock_coordinator_full.data["measurements"] = {}
    assert sensor.native_value is None
    
    # 3. Variable not found
    mock_coordinator_full.data["measurements"] = [{"codi": "UD", "variables": []}]
    assert sensor.native_value is None
    
    # 4. Lectures empty
    mock_coordinator_full.data["measurements"] = [{"codi": "UD", "variables": [{"codi": 32, "lectures": []}]}]
    assert sensor.native_value is None

    # 5. Lectures found
    mock_coordinator_full.data["measurements"] = [{"codi": "UD", "variables": [{"codi": 32, "lectures": [{"valor": 12.3}]}]}]
    assert sensor.native_value == 12.3

async def test_forecast_sensor_hourly_edge_cases(hass, mock_coordinator_full):
    """Test edge cases for MeteocatForecastSensor (hourly)."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    
    sensor = MeteocatForecastSensor(
        mock_coordinator_full, 
        entry, 
        "Device Name", 
        "Entity Name", 
        "hourly"
    )
    
    # 1. Native value (hours count) - missing data
    mock_coordinator_full.data["forecast_hourly"] = None
    assert sensor.native_value == "0 hores"
    
    # 2. Native value - no dies
    mock_coordinator_full.data["forecast_hourly"] = {"dies": []}
    assert sensor.native_value == "0 hores"
    
    # 3. Attributes - missing data
    mock_coordinator_full.data["forecast_hourly"] = None
    assert sensor.extra_state_attributes == {}
    
    # 4. _get_forecast_hourly - bad values
    mock_coordinator_full.data["forecast_hourly"] = {
        "dies": [
            {
                "variables": {
                    "temp": {"valors": [{"data": "T1", "valor": "bad"}]},
                    "precipitacio": {"valors": [{"data": "T1", "valor": "bad"}]},
                }
            }
        ]
    }
    forecast = sensor.extra_state_attributes["forecast_ha"]
    # Should catch ValueError and omit bad fields
    assert len(forecast) == 1
    assert "temperature" not in forecast[0]
    assert "precipitation" not in forecast[0]
    
    # 5. _get_forecast_hourly - missing fields
    mock_coordinator_full.data["forecast_hourly"] = {"dies": [{"variables": {}}]}
    forecast = sensor.extra_state_attributes["forecast_ha"]
    assert len(forecast) == 0

async def test_forecast_sensor_daily_edge_cases(hass, mock_coordinator_full):
    """Test edge cases for MeteocatForecastSensor (daily)."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    
    sensor = MeteocatForecastSensor(
        mock_coordinator_full, 
        entry, 
        "Device Name", 
        "Entity Name", 
        "daily"
    )
    
    # 1. Native value (days count) - missing data
    mock_coordinator_full.data["forecast"] = None
    assert sensor.native_value == "0 dies"
    
    # 2. Native value - no dies
    mock_coordinator_full.data["forecast"] = {"dies": []}
    assert sensor.native_value == "0 dies"
    
    # 3. Attributes - missing data
    mock_coordinator_full.data["forecast"] = None
    assert sensor.extra_state_attributes == {}
    
    # 4. _get_forecast_daily - bad values
    mock_coordinator_full.data["forecast"] = {
        "dies": [
            {
                "data": "D1",
                "variables": {
                    "tmin": {"valor": "bad"},
                    "tmax": {"valor": "bad"},
                    "precipitacio": {"valor": "bad"},
                    # estatCal missing, or without valor
                    "estatCel": {}
                }
            }
        ]
    }
    forecast = sensor.extra_state_attributes["forecast_ha"]
    # Should catch ValueError and omit bad fields
    assert len(forecast) == 1
    assert "templow" not in forecast[0]
    assert "temperature" not in forecast[0]
    assert "precipitation" not in forecast[0]
    assert "condition" not in forecast[0]

    # 5. _get_forecast_daily - no data field
    mock_coordinator_full.data["forecast"] = {"dies": [{"no_data": "here"}]}
    forecast = sensor.extra_state_attributes["forecast_ha"]
    assert len(forecast) == 0
