"""Test reproduction for zero values in forecast SENSOR."""
from unittest.mock import MagicMock
import pytest
from homeassistant.core import HomeAssistant
from custom_components.meteocat_community_edition.const import DOMAIN
from custom_components.meteocat_community_edition.sensor import MeteocatForecastSensor
from pytest_homeassistant_custom_component.common import MockConfigEntry

@pytest.fixture
def mock_coordinator(hass):
    """Mock the coordinator."""
    coordinator = MagicMock()
    coordinator.hass = hass
    coordinator.enable_forecast_daily = True
    coordinator.enable_forecast_hourly = True
    return coordinator

async def test_sensor_zero_temp_handling(hass: HomeAssistant, mock_coordinator):
    """Test that 0 degrees is handled correctly and not skipped in SENSOR."""
    entry = MockConfigEntry(domain=DOMAIN, data={"mode": "XEMA", "station_code": "X1", "station_name": "Test"})
    
    # Mock forecast data with 0 values
    mock_coordinator.data = {
        "forecast": {
            "dies": [
                {
                    "data": "2026-01-07",
                    "variables": {
                        "tmin": {"valor": 0},      # This is the key test: value 0
                        "tmax": {"valor": 11},
                        "estatCel": {"valor": 1},
                        "precipitacio": {"valor": 0} # 0% probability
                    }
                }
            ]
        }
    }
    
    # Instantiate sensor (type daily)
    entity = MeteocatForecastSensor(mock_coordinator, entry, "TestDevice", "TestEntity", "daily")
    entity.hass = hass
    
    # Get attrs
    attrs = entity.extra_state_attributes
    forecast_list = attrs.get("forecast_ha", [])
    
    assert len(forecast_list) == 1
    day = forecast_list[0]
    
    # Validation
    assert "temperature" in day
    assert day["temperature"] == 11.0
    
    # Verify minimal temperature (0 degrees)
    assert "templow" in day, "minimal temperature should be present in SENSOR"
    assert day["templow"] == 0.0, "minimal temperature should be 0.0 in SENSOR"

    # Verify precipitation (0 percent)
    assert "precipitation" in day
    assert day["precipitation"] == 0.0
