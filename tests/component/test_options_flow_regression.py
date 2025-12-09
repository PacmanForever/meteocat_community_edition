"""Test for Options Flow regression."""
import pytest
from unittest.mock import MagicMock
from custom_components.meteocat_community_edition.config_flow import MeteocatOptionsFlow
from custom_components.meteocat_community_edition.const import CONF_MODE, MODE_EXTERNAL

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
