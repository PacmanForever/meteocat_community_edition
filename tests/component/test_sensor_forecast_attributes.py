"""Tests for Meteocat forecast sensor attributes."""
from unittest.mock import MagicMock
import pytest

from custom_components.meteocat_community_edition.sensor import MeteocatForecastSensor
from custom_components.meteocat_community_edition.const import MODE_MUNICIPI

@pytest.fixture
def mock_coordinator():
    """Mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "forecast": {
            "dies": [
                {
                    "data": "2025-12-10",
                    "variables": {
                        "tmin": {"valor": 10},
                        "tmax": {"valor": 20},
                        "estatCel": {"valor": 1},  # Sunny
                        "precipitacio": {"valor": 1.5}
                    }
                }
            ]
        },
        "forecast_hourly": {
            "dies": [
                {
                    "data": "2025-12-10",
                    "variables": {
                        "temp": {"valors": [{"data": "2025-12-10T10:00Z", "valor": 15}]},
                        "estatCel": {"valors": [{"data": "2025-12-10T10:00Z", "valor": 1}]},
                        "precipitacio": {"valors": [{"data": "2025-12-10T10:00Z", "valor": 1.5}]}
                    }
                }
            ]
        }
    }
    return coordinator

@pytest.fixture
def mock_entry():
    """Mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {"mode": MODE_MUNICIPI}
    return entry

def test_forecast_sensor_daily_attributes(mock_coordinator, mock_entry):
    """Test daily forecast sensor attributes."""
    sensor = MeteocatForecastSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers",
        "daily"
    )
    
    attrs = sensor.extra_state_attributes
    assert "forecast_ha" in attrs
    forecast = attrs["forecast_ha"]
    assert len(forecast) == 1
    assert forecast[0]["datetime"] == "2025-12-10"
    assert forecast[0]["templow"] == 10
    assert forecast[0]["temperature"] == 20
    assert forecast[0]["condition"] == "sunny"
    assert forecast[0]["precipitation"] == 1.5

def test_forecast_sensor_hourly_attributes(mock_coordinator, mock_entry):
    """Test hourly forecast sensor attributes."""
    sensor = MeteocatForecastSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers",
        "hourly"
    )
    
    attrs = sensor.extra_state_attributes
    assert "forecast_ha" in attrs
    forecast = attrs["forecast_ha"]
    assert len(forecast) == 1
    assert forecast[0]["datetime"] == "2025-12-10T10:00Z"
    assert forecast[0]["temperature"] == 15
    assert forecast[0]["condition"] == "sunny"
    assert forecast[0]["precipitation"] == 1.5

def test_forecast_sensor_daily_empty(mock_coordinator, mock_entry):
    """Test daily forecast sensor with no data."""
    mock_coordinator.data["forecast"] = None
    sensor = MeteocatForecastSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers",
        "daily"
    )
    
    attrs = sensor.extra_state_attributes
    assert attrs == {}

def test_forecast_sensor_hourly_empty(mock_coordinator, mock_entry):
    """Test hourly forecast sensor with no data."""
    mock_coordinator.data["forecast_hourly"] = None
    sensor = MeteocatForecastSensor(
        mock_coordinator,
        mock_entry,
        "Granollers",
        "Granollers",
        "hourly"
    )
    
    attrs = sensor.extra_state_attributes
    assert attrs == {}
