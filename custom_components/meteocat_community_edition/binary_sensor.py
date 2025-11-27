"""Binary sensor entities for Meteocat (Community Edition).

This module provides health monitoring for the integration through a diagnostic
binary sensor that tracks update success/failure status.

Sensor:
- Update Status: Reports problems with data updates
  - Name: "Problema actualitzant dades" (via translation_key)
  - Device class: problem
  - Category: diagnostic
  - Logic: ON = problem detected, OFF = ok
  - has_entity_name: True with name=None (uses only translation key)
  - Always available (can report failures even when coordinator is unavailable)
  - Checks ALL API calls based on mode (measurements, forecast, forecast_hourly, uv_index)
  - Extra attributes: failed_calls, last_check, error details

Last updated: 2025-11-27
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_MODE,
    CONF_MUNICIPALITY_CODE,
    CONF_STATION_CODE,
    CONF_STATION_NAME,
    CONF_MUNICIPALITY_NAME,
    DOMAIN,
    MODE_ESTACIO,
    MODE_MUNICIPI,
)
from .coordinator import MeteocatCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteocat binary sensor entities."""
    coordinator: MeteocatCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Get entity name based on mode
    mode = entry.data.get(CONF_MODE, MODE_ESTACIO)
    station_code = entry.data.get(CONF_STATION_CODE, "")
    
    if mode == MODE_ESTACIO:
        station_name = entry.data.get(CONF_STATION_NAME, f"Estació {station_code}")
        entity_name = station_name
        entity_name_with_code = f"{station_name} {station_code}"
    else:
        municipality_code = entry.data.get(CONF_MUNICIPALITY_CODE, "")
        entity_name = entry.data.get(CONF_MUNICIPALITY_NAME, f"Municipi {municipality_code}")
        entity_name_with_code = entity_name
    
    # Create update status binary sensor
    async_add_entities([
        MeteocatUpdateStatusBinarySensor(
            coordinator,
            entry,
            entity_name,
            entity_name_with_code,
            mode,
            station_code if mode == MODE_ESTACIO else None,
        )
    ])


class MeteocatUpdateStatusBinarySensor(CoordinatorEntity[MeteocatCoordinator], BinarySensorEntity):
    """Binary sensor for monitoring update status.
    
    Reports whether there are problems with data updates by checking ALL
    API calls based on the configured mode:
    - MODE_ESTACIO: Checks measurements data
    - MODE_MUNICIPI: Checks forecast, forecast_hourly, and uv_index data
    
    The sensor:
    - Uses translation_key "update_status" for entity name ("Problema actualitzant dades")
    - Sets name=None to use only translation without device prefix in events
    - Device class: PROBLEM (ON = problem detected, OFF = ok)
    - Always available to report errors even when coordinator fails
    - Provides detailed error information in attributes (failed_calls, error details)
    
    Useful for:
    - Automations triggered on data update failures
    - Monitoring integration health in diagnostics
    - Dashboard status indicators
    
    Last updated: 2025-11-27
    """

    _attr_attribution = ATTRIBUTION
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        mode: str,
        station_code: str | None = None,
    ) -> None:
        """Initialize the update status binary sensor."""
        super().__init__(coordinator)
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._mode = mode
        self._station_code = station_code
        self._entry = entry
        
        self._attr_unique_id = f"{entry.entry_id}_update_status"
        self._attr_translation_key = "update_status"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_name = None  # Use translation key for the name
        
        # Set device info to group with other entities
        if mode == MODE_ESTACIO:
            model = "Estació XEMA"
        else:
            model = "Predicció Municipal"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edició Comunitària",
            "model": model,
        }

    @property
    def is_on(self) -> bool:
        """Return True if there is a problem (any API call failed).
        
        Problem detection logic:
        - Check if coordinator.data exists
        - Check ALL expected API calls for the mode
        - If ANY call returned None (failed) or empty data -> Problem
        - All calls must succeed with data -> OK
        """
        # Verify we have coordinator data
        if not self.coordinator.data:
            return True  # Problem: no data at all
        
        # Track failed API calls
        failed_calls = []
        
        # For MODE_ESTACIO: check measurements (always required)
        if self._mode == MODE_ESTACIO:
            measurements = self.coordinator.data.get("measurements")
            if measurements is None or (isinstance(measurements, (list, dict)) and len(measurements) == 0):
                failed_calls.append("measurements")
        
        # For both modes: check forecasts if municipality_code exists
        # In MODE_ESTACIO: forecasts are optional (only if station has municipality)
        # In MODE_MUNICIPI: forecasts are always expected
        municipality_code = self.coordinator.data.get("municipality_code")
        
        if municipality_code or self._mode == MODE_MUNICIPI:
            # Check daily forecast
            forecast = self.coordinator.data.get("forecast")
            if forecast is None or (isinstance(forecast, (list, dict)) and len(forecast) == 0):
                failed_calls.append("forecast")
            
            # Check hourly forecast
            forecast_hourly = self.coordinator.data.get("forecast_hourly")
            if forecast_hourly is None or (isinstance(forecast_hourly, (list, dict)) and len(forecast_hourly) == 0):
                failed_calls.append("forecast_hourly")
            
            # Check UV index
            uv_index = self.coordinator.data.get("uv_index")
            if uv_index is None or (isinstance(uv_index, (list, dict)) and len(uv_index) == 0):
                failed_calls.append("uv_index")
        
        # If any call failed, there's a problem
        if failed_calls:
            return True
        
        # Check if the last update had errors
        if not self.coordinator.last_update_success:
            return True  # Problem: last update failed
        
        # All checks passed: no problem
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {}
        
        # Add last successful update time if available
        if self.coordinator.last_successful_update_time:
            attrs["last_success"] = self.coordinator.last_successful_update_time.isoformat()
        
        # Add status based on is_on (inverted logic: ON = problem)
        if self.is_on:
            attrs["status"] = "error"
            
            # Build list of failed API calls
            if not self.coordinator.data:
                attrs["error"] = "No data available - coordinator not initialized"
            else:
                failed_calls = []
                
                # Check measurements (MODE_ESTACIO only)
                if self._mode == MODE_ESTACIO:
                    measurements = self.coordinator.data.get("measurements")
                    if measurements is None:
                        failed_calls.append("measurements (API call failed)")
                    elif isinstance(measurements, (list, dict)) and len(measurements) == 0:
                        failed_calls.append("measurements (empty/quota exhausted)")
                
                # Check forecasts (both modes if municipality_code exists)
                municipality_code = self.coordinator.data.get("municipality_code")
                if municipality_code or self._mode == MODE_MUNICIPI:
                    forecast = self.coordinator.data.get("forecast")
                    if forecast is None:
                        failed_calls.append("forecast (API call failed)")
                    elif isinstance(forecast, (list, dict)) and len(forecast) == 0:
                        failed_calls.append("forecast (empty/quota exhausted)")
                    
                    forecast_hourly = self.coordinator.data.get("forecast_hourly")
                    if forecast_hourly is None:
                        failed_calls.append("forecast_hourly (API call failed)")
                    elif isinstance(forecast_hourly, (list, dict)) and len(forecast_hourly) == 0:
                        failed_calls.append("forecast_hourly (empty/quota exhausted)")
                    
                    uv_index = self.coordinator.data.get("uv_index")
                    if uv_index is None:
                        failed_calls.append("uv_index (API call failed)")
                    elif isinstance(uv_index, (list, dict)) and len(uv_index) == 0:
                        failed_calls.append("uv_index (empty/quota exhausted)")
                
                if failed_calls:
                    attrs["error"] = f"Failed: {', '.join(failed_calls)}"
                    attrs["failed_count"] = len(failed_calls)
                else:
                    attrs["error"] = "Update failed - check logs for details"
        else:
            attrs["status"] = "ok"
        
        return attrs

    @property
    def icon(self) -> str:
        """Return icon based on status."""
        if self.is_on:
            return "mdi:alert-circle"
        return "mdi:check-circle"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # This sensor is always available, even if coordinator fails
        # This way it can report the failure status
        return True
