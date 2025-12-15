"""Test for Options Flow regression."""
import pytest
from unittest.mock import MagicMock
from custom_components.meteocat_community_edition.config_flow import MeteocatOptionsFlow
from custom_components.meteocat_community_edition.const import (
    CONF_MODE, MODE_EXTERNAL, MODE_LOCAL,
    CONF_ENABLE_FORECAST_DAILY, CONF_ENABLE_FORECAST_HOURLY,
    CONF_UPDATE_TIME_1, CONF_UPDATE_TIME_2, CONF_UPDATE_TIME_3,
    CONF_API_KEY
)

@pytest.mark.asyncio
async def test_options_flow_init_regression():
    """Test that MeteocatOptionsFlow can be instantiated and initialized without error."""
    mock_entry = MagicMock()
    mock_entry.data = {CONF_MODE: MODE_EXTERNAL}
    mock_entry.options = {}

    # This should not raise AttributeError: property 'config_entry' of 'MeteocatOptionsFlow' object has no setter
    try:
        flow = MeteocatOptionsFlow(mock_entry)
    except AttributeError as e:
        pytest.fail(f"Initialization failed with AttributeError: {e}")

    # In the test environment, we might need to manually set config_entry if the base class doesn't do it
    # and we removed the assignment.
    # However, to simulate the fix working, we should check if it's present.
    if not hasattr(flow, "config_entry"):
        # If it's missing in test env, we set it manually to allow testing async_step_init
        # This mimics what HA FlowManager would do (or what the property would return)
        flow.config_entry = mock_entry

    # Test async_step_init
    result = await flow.async_step_init()
    assert result["type"] == "form"
    assert result["step_id"] == "init"


@pytest.mark.asyncio
async def test_options_flow_forecast_validation_local_mode():
    """Test that forecast validation works for local mode stations."""
    mock_entry = MagicMock()
    mock_entry.data = {
        CONF_MODE: MODE_LOCAL,
        CONF_API_KEY: "test_api_key",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False
    }
    mock_entry.options = {
        CONF_UPDATE_TIME_1: "08:00",
        CONF_UPDATE_TIME_2: "14:00",
        CONF_UPDATE_TIME_3: "20:00"
    }

    flow = MeteocatOptionsFlow(mock_entry)

    # Test: disable both forecasts should trigger validation error
    user_input = {
        CONF_UPDATE_TIME_1: "08:00",
        CONF_UPDATE_TIME_2: "14:00",
        CONF_UPDATE_TIME_3: "20:00",
        CONF_ENABLE_FORECAST_DAILY: False,
        CONF_ENABLE_FORECAST_HOURLY: False
    }

    result = await flow.async_step_init(user_input)
    assert result["type"] == "form"
    assert "errors" in result
    assert result["errors"]["base"] == "must_select_one_forecast"


@pytest.mark.asyncio
async def test_options_flow_forecast_validation_external_mode():
    """Test that forecast validation works for external mode stations."""
    mock_entry = MagicMock()
    mock_entry.data = {
        CONF_MODE: MODE_EXTERNAL,
        CONF_API_KEY: "test_api_key",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False
    }
    mock_entry.options = {
        CONF_UPDATE_TIME_1: "08:00",
        CONF_UPDATE_TIME_2: "14:00",
        CONF_UPDATE_TIME_3: "20:00"
    }

    flow = MeteocatOptionsFlow(mock_entry)
    # Mock hass to avoid AttributeError when updating entry
    flow.hass = MagicMock()
    flow.hass.config_entries = MagicMock()

    # Test: disable both forecasts should trigger validation error for external mode
    user_input = {
        CONF_UPDATE_TIME_1: "08:00",
        CONF_UPDATE_TIME_2: "14:00",
        CONF_UPDATE_TIME_3: "20:00",
        CONF_ENABLE_FORECAST_DAILY: False,
        CONF_ENABLE_FORECAST_HOURLY: False
    }

    result = await flow.async_step_init(user_input)
    assert result["type"] == "form"
    assert "errors" in result
    assert result["errors"]["base"] == "must_select_one_forecast"


@pytest.mark.asyncio
async def test_options_flow_forecast_validation_success():
    """Test that forecast validation allows valid configurations."""
    mock_entry = MagicMock()
    mock_entry.data = {
        CONF_MODE: MODE_LOCAL,
        CONF_API_KEY: "test_api_key",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False
    }
    mock_entry.options = {
        CONF_UPDATE_TIME_1: "08:00",
        CONF_UPDATE_TIME_2: "14:00",
        CONF_UPDATE_TIME_3: "20:00"
    }

    flow = MeteocatOptionsFlow(mock_entry)

    # Test: enable at least one forecast should succeed
    user_input = {
        CONF_UPDATE_TIME_1: "08:00",
        CONF_UPDATE_TIME_2: "14:00",
        CONF_UPDATE_TIME_3: "20:00",
        CONF_ENABLE_FORECAST_DAILY: True,
        CONF_ENABLE_FORECAST_HOURLY: False
    }

    result = await flow.async_step_init(user_input)
    print(f"Result: {result}")
    # For local mode, it should continue to the next step (local_sensors)
    assert result["type"] == "form"
    assert result["step_id"] == "local_sensors"
