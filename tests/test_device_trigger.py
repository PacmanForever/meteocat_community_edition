"""Tests for Meteocat device triggers."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE

from custom_components.meteocat_community_edition.device_trigger import (
    async_get_triggers,
    async_attach_trigger,
    async_get_trigger_capabilities,
    TRIGGER_DATA_UPDATED,
)
from custom_components.meteocat_community_edition.const import DOMAIN, EVENT_DATA_UPDATED


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    return hass


@pytest.mark.asyncio
async def test_async_get_triggers(mock_hass):
    """Test that async_get_triggers returns correct trigger list."""
    device_id = "test_device_id_123"
    
    triggers = await async_get_triggers(mock_hass, device_id)
    
    # Should return exactly 2 triggers (data_updated and next_update_changed)
    assert len(triggers) == 2
    
    # Verify trigger structure
    for trigger in triggers:
        assert trigger[CONF_PLATFORM] == "device"
        assert trigger[CONF_DEVICE_ID] == device_id
        assert trigger[CONF_DOMAIN] == DOMAIN
        assert trigger[CONF_TYPE] in ["data_updated", "next_update_changed"]


@pytest.mark.asyncio
async def test_async_get_triggers_different_devices(mock_hass):
    """Test that different device IDs get different triggers."""
    device_id_1 = "device_1"
    device_id_2 = "device_2"
    
    triggers_1 = await async_get_triggers(mock_hass, device_id_1)
    triggers_2 = await async_get_triggers(mock_hass, device_id_2)
    
    # Both should have 2 triggers
    assert len(triggers_1) == 2
    assert len(triggers_2) == 2
    
    # But with different device IDs
    assert triggers_1[0][CONF_DEVICE_ID] == device_id_1
    assert triggers_2[0][CONF_DEVICE_ID] == device_id_2


@pytest.mark.asyncio
async def test_async_attach_trigger(mock_hass):
    """Test that async_attach_trigger properly attaches an event trigger."""
    device_id = "test_device_123"
    
    config = {
        CONF_PLATFORM: "device",
        CONF_DEVICE_ID: device_id,
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: TRIGGER_DATA_UPDATED,
    }
    
    action = AsyncMock()
    trigger_info = {"trigger_data": "test"}
    
    # Mock the event_trigger.async_attach_trigger
    with patch("custom_components.meteocat_community_edition.device_trigger.event_trigger.async_attach_trigger") as mock_attach:
        mock_attach.return_value = AsyncMock()
        
        result = await async_attach_trigger(mock_hass, config, action, trigger_info)
        
        # Should have called event_trigger.async_attach_trigger
        mock_attach.assert_called_once()
        
        # Verify the event config passed to event_trigger
        call_args = mock_attach.call_args
        event_config = call_args[0][1]  # Second positional argument
        
        # Verify event configuration
        assert event_config["platform"] == "event"
        # event_type might be a Template, just verify it's present
        assert "event_type" in event_config
        assert "event_data" in event_config
        assert event_config["event_data"]["device_id"] == device_id
        
        # Verify action and trigger_info were passed through
        assert call_args[0][2] == action
        assert call_args[0][3] == trigger_info
        
        # Verify platform_type kwarg
        assert call_args[1]["platform_type"] == "device"


@pytest.mark.asyncio
async def test_async_attach_trigger_with_different_device_ids(mock_hass):
    """Test that different device IDs create different event filters."""
    device_id_1 = "device_abc"
    device_id_2 = "device_xyz"
    
    config_1 = {
        CONF_PLATFORM: "device",
        CONF_DEVICE_ID: device_id_1,
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: TRIGGER_DATA_UPDATED,
    }
    
    config_2 = {
        CONF_PLATFORM: "device",
        CONF_DEVICE_ID: device_id_2,
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: TRIGGER_DATA_UPDATED,
    }
    
    action = AsyncMock()
    trigger_info = {}
    
    with patch("custom_components.meteocat_community_edition.device_trigger.event_trigger.async_attach_trigger") as mock_attach:
        mock_attach.return_value = AsyncMock()
        
        # Attach first trigger
        await async_attach_trigger(mock_hass, config_1, action, trigger_info)
        first_call_config = mock_attach.call_args[0][1]
        
        # Attach second trigger
        await async_attach_trigger(mock_hass, config_2, action, trigger_info)
        second_call_config = mock_attach.call_args[0][1]
        
        # Verify different device IDs were used
        assert first_call_config["event_data"]["device_id"] == device_id_1
        assert second_call_config["event_data"]["device_id"] == device_id_2


@pytest.mark.asyncio
async def test_async_get_trigger_capabilities(mock_hass):
    """Test that async_get_trigger_capabilities returns empty dict."""
    config = {
        CONF_PLATFORM: "device",
        CONF_DEVICE_ID: "test_device",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: TRIGGER_DATA_UPDATED,
    }
    
    capabilities = await async_get_trigger_capabilities(mock_hass, config)
    
    # Should return empty dict (no additional capabilities)
    assert capabilities == {}
    assert isinstance(capabilities, dict)


@pytest.mark.asyncio
async def test_trigger_type_constant():
    """Test that trigger type constant has correct value."""
    assert TRIGGER_DATA_UPDATED == "data_updated"


@pytest.mark.asyncio
async def test_async_attach_trigger_returns_callback(mock_hass):
    """Test that async_attach_trigger returns a callback."""
    config = {
        CONF_PLATFORM: "device",
        CONF_DEVICE_ID: "test_device",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: TRIGGER_DATA_UPDATED,
    }
    
    action = AsyncMock()
    trigger_info = {}
    
    mock_callback = MagicMock()
    
    with patch("custom_components.meteocat_community_edition.device_trigger.event_trigger.async_attach_trigger") as mock_attach:
        mock_attach.return_value = mock_callback
        
        result = await async_attach_trigger(mock_hass, config, action, trigger_info)
        
        # Result should be the callback
        assert result == mock_callback
