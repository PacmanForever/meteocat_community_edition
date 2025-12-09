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
from .coordinator import MeteocatCoordinator, MeteocatForecastCoordinator, MeteocatLegacyCoordinator

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
    mode = entry.data.get(CONF_MODE, MODE_EXTERNAL)  # Default to ESTACIO for backwards compatibility

    if mode == MODE_EXTERNAL:
        # XEMA mode: Use Legacy Coordinator (handles both station and forecast)
        coordinator = MeteocatLegacyCoordinator(hass, entry)
    else:
        # Municipal mode: Use Forecast Coordinator (handles only forecast)
        coordinator = MeteocatForecastCoordinator(hass, entry)
    
    # ⚠️ CRITICAL: First refresh - this is the ONLY manual update call
    # All future updates will be scheduled automatically
    await coordinator.async_config_entry_first_refresh()
    
    # ⚠️ CRITICAL: Schedule future updates at configured times
    # This MUST be called to enable scheduled updates
    coordinator._schedule_next_update()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    if mode == MODE_EXTERNAL:
        # XEMA mode: load weather entity + sensors + button + binary_sensor
        platforms = PLATFORMS
    else:
        # Municipal mode: load sensors (forecasts) + button + binary_sensor
        platforms = [Platform.SENSOR, Platform.BUTTON, Platform.BINARY_SENSOR]
    
    # Use async_forward_entry_setups for HA 2022.8+
    # This method batches platform loading for better performance
    await hass.config_entries.async_forward_entry_setups(entry, platforms)
    
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
        platforms = [Platform.SENSOR, Platform.BUTTON, Platform.BINARY_SENSOR]
    
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, platforms):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
