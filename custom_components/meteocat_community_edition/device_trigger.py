"""Provides device triggers for Meteocat."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_PLATFORM,
    CONF_TYPE,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, EVENT_DATA_UPDATED, EVENT_NEXT_UPDATE_CHANGED

# Trigger types
TRIGGER_DATA_UPDATED = "data_updated"
TRIGGER_NEXT_UPDATE_CHANGED = "next_update_changed"

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In([TRIGGER_DATA_UPDATED, TRIGGER_NEXT_UPDATE_CHANGED]),
    }
)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """List device triggers for Meteocat devices."""
    return [
        {
            CONF_PLATFORM: "device",
            CONF_DEVICE_ID: device_id,
            CONF_DOMAIN: DOMAIN,
            CONF_TYPE: TRIGGER_DATA_UPDATED,
        },
        {
            CONF_PLATFORM: "device",
            CONF_DEVICE_ID: device_id,
            CONF_DOMAIN: DOMAIN,
            CONF_TYPE: TRIGGER_NEXT_UPDATE_CHANGED,
        },
    ]


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: Any,
    trigger_info: dict[str, Any],
) -> CALLBACK_TYPE:
    """Attach a trigger."""
    trigger_type = config[CONF_TYPE]
    event_type = EVENT_DATA_UPDATED if trigger_type == TRIGGER_DATA_UPDATED else EVENT_NEXT_UPDATE_CHANGED
    
    # Build event config compatible with current and future HA versions
    event_config = {
        event_trigger.CONF_PLATFORM: "event",
        event_trigger.CONF_EVENT_TYPE: event_type,
        event_trigger.CONF_EVENT_DATA: {
            "device_id": config[CONF_DEVICE_ID],
        },
    }
    
    # Validate config using schema (compatible with schema changes)
    event_config = event_trigger.TRIGGER_SCHEMA(event_config)
    
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )


async def async_get_trigger_capabilities(
    hass: HomeAssistant, config: ConfigType
) -> dict[str, vol.Schema]:
    """List trigger capabilities."""
    return {}
