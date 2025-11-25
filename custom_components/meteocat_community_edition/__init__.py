"""The Meteocat (Community Edition) integration."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import CONF_MODE, DOMAIN, MODE_ESTACIO
from .coordinator import MeteocatCoordinator

if TYPE_CHECKING:
    from .api import MeteocatAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.WEATHER, Platform.SENSOR, Platform.BUTTON]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Meteocat (Community Edition) from a config entry."""
    coordinator = MeteocatCoordinator(hass, entry)
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Determine which platforms to load based on mode
    mode = entry.data.get(CONF_MODE, MODE_ESTACIO)  # Default to ESTACIO for backwards compatibility

    if mode == MODE_ESTACIO:
        # XEMA mode: load weather entity + sensors + button
        platforms = PLATFORMS
    else:
        # Municipal mode: load only sensors (forecasts) + button
        platforms = [Platform.SENSOR, Platform.BUTTON]
    
    await hass.config_entries.async_forward_entry_setups(entry, platforms)
    
    # Register update listener for options flow
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Determine platforms based on mode
    mode = entry.data.get(CONF_MODE, MODE_ESTACIO)
    if mode == MODE_ESTACIO:
        platforms = PLATFORMS
    else:
        platforms = [Platform.SENSOR, Platform.BUTTON]
    
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, platforms):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
