"""Test fix for forecast size issue."""
import pytest
from unittest.mock import MagicMock
from custom_components.meteocat_community_edition.sensor import MeteocatForecastSensor

async def test_hourly_forecast_sensor_attributes_size_fix(hass):
    """Test that hourly forecast sensor does NOT return raw forecast data in attributes."""
    
    # Mock coordinator with data
    coordinator = MagicMock()
    coordinator.data = {
        "forecast_hourly": {
            "dies": [
                {
                    "data": "2025-01-01",
                    "variables": {
                        "temp": {"valors": [{"data": "2025-01-01T00:00Z", "valor": 10}]},
                        "estatCel": {"valors": [{"data": "2025-01-01T00:00Z", "valor": 1}]},
                        "precipitacio": {"valors": [{"data": "2025-01-01T00:00Z", "valor": 0}]}
                    }
                }
            ]
        }
    }
    
    # Mock entry
    entry = MagicMock()
    entry.entry_id = "test_entry"
    
    # Create sensor
    sensor = MeteocatForecastSensor(
        coordinator,
        entry,
        "Test Device",
        "Test Entity",
        "hourly"
    )
    
    # Check attributes
    attributes = sensor.extra_state_attributes
    
    # Verify 'forecast' key (raw data) is missing
    assert "forecast" not in attributes
    
    # Verify 'forecast_ha' is present and correct
    assert "forecast_ha" in attributes
    assert len(attributes["forecast_ha"]) > 0
    assert attributes["forecast_ha"][0]["datetime"] == "2025-01-01T00:00Z"

async def test_daily_forecast_sensor_attributes_optimized(hass):
    """Test that daily forecast sensor ALSO excludes raw forecast data."""
    
    # Mock coordinator with data
    coordinator = MagicMock()
    coordinator.data = {
        "forecast": {
            "dies": [
                {
                    "data": "2025-01-01",
                    "variables": {}
                }
            ]
        }
    }
    
    # Mock entry
    entry = MagicMock()
    entry.entry_id = "test_entry"
    
    # Create sensor
    sensor = MeteocatForecastSensor(
        coordinator,
        entry,
        "Test Device",
        "Test Entity",
        "daily"
    )
    
    # Check attributes
    attributes = sensor.extra_state_attributes
    
    # Verify 'forecast' key is REMOVED for consistency
    assert "forecast" not in attributes
    assert "forecast_ha" in attributes
