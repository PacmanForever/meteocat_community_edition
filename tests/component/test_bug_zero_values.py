"""Test reproduction for zero values in forecast."""
from unittest.mock import MagicMock
import pytest
from homeassistant.core import HomeAssistant
from custom_components.meteocat_community_edition.const import DOMAIN
from custom_components.meteocat_community_edition.weather import MeteocatWeather
from pytest_homeassistant_custom_component.common import MockConfigEntry

@pytest.fixture
def mock_coordinator(hass):
    """Mock the coordinator."""
    coordinator = MagicMock()
    coordinator.hass = hass
    return coordinator

async def test_zero_temp_handling(hass: HomeAssistant, mock_coordinator):
    """Test that 0 degrees is handled correctly and not skipped."""
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
    
    entity = MeteocatWeather(mock_coordinator, entry)
    entity.hass = hass
    
    # Get forecast
    forecast = await entity.async_forecast_daily()
    
    assert forecast is not None
    assert len(forecast) == 1
    day = forecast[0]
    
    # Validation
    assert "native_temperature" in day
    assert day["native_temperature"] == 11.0
    
    # The bug implies this will fail if code uses 'if valor:'
    assert "native_templow" in day
    assert day["native_templow"] == 0.0

    # Also check precip probability
    assert "precipitation_probability" in day
    assert day["precipitation_probability"] == 0.0
