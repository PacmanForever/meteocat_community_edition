"""The Meteocat (Community Edition) integration.

This integration provides weather data from the Meteocat API for Catalonia.

Platforms:
- Weather: Weather entity (MODE_EXTERNAL only)
- Sensor: All data sensors (forecasts, measurements, timestamps, quotas, geographic)
- Binary Sensor: Health monitoring (update status)
- Button: Manual data refresh

Last updated: 2025-11-27
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import CONF_MODE, DOMAIN, MODE_EXTERNAL
from .coordinator import MeteocatCoordinator

if TYPE_CHECKING:
    from .api import MeteocatAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.WEATHER, Platform.SENSOR, Platform.BUTTON, Platform.BINARY_SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Meteocat (Community Edition) from a config entry.
    
    ⚠️ CRITICAL: Update Sequence for API Quota Management
    
    The order of operations is CRITICAL to prevent API quota exhaustion:
    
    1. async_config_entry_first_refresh() - Performs EXACTLY ONE initial update
    2. _schedule_next_update() - Schedules future updates at configured times
    
    DO NOT add any additional update calls here, as they would waste API quota.
    Updates will automatically happen at the configured times (default 06:00 and 14:00).
    
    Test Coverage: test_no_duplicate_updates_on_ha_restart in test_scheduled_updates.py
    """
    
    coordinator = MeteocatCoordinator(hass, entry)
    
    # Migrate API key from options to data if necessary
    from .const import CONF_API_KEY
    if CONF_API_KEY in entry.options and CONF_API_KEY not in entry.data:
        new_data = dict(entry.data)
        new_data[CONF_API_KEY] = entry.options[CONF_API_KEY]
        await hass.config_entries.async_update_entry(entry, data=new_data)
        # Remove from options
        new_options = dict(entry.options)
        new_options.pop(CONF_API_KEY, None)
        await hass.config_entries.async_update_entry(entry, options=new_options)
        _LOGGER.info("Migrated API key from options to data for entry %s", entry.title)
    
    # ⚠️ CRITICAL: First refresh - this is the ONLY manual update call
    # All future updates will be scheduled automatically
    await coordinator.async_config_entry_first_refresh()
    
    # ⚠️ CRITICAL: Schedule future updates at configured times
    # This MUST be called to enable scheduled updates
    coordinator._schedule_next_update()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Load all platforms for both modes (External and Local)
    # Weather entity is now supported in both modes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register update listener for options flow
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.
    
    ⚠️ CRITICAL: Cleanup for API Quota Management
    
    async_shutdown() MUST be called to cancel pending scheduled updates.
    Without this, orphaned schedulers would continue making API calls even after
    the integration is unloaded, wasting quota.
    
    Test Coverage: test_cleanup_cancels_scheduled_update in test_scheduled_updates.py
    """
    # ⚠️ CRITICAL: Clean up scheduled updates to prevent orphaned schedulers
    coordinator: MeteocatCoordinator = hass.data[DOMAIN].get(entry.entry_id)
    if coordinator:
        await coordinator.async_shutdown()
    
    # Determine platforms based on mode
    mode = entry.data.get(CONF_MODE, MODE_EXTERNAL)
    if mode == MODE_EXTERNAL:
        platforms = PLATFORMS
    else:
        # Local mode now includes weather entity too
        platforms = PLATFORMS
    
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, platforms):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
