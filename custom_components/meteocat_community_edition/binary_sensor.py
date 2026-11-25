"""Binary sensors for update health and calculated weather conditions.

Calculated conditions are created only when the configured station or local
sensors provide the required inputs. Local-source changes update their states
immediately; XEMA-based conditions update with coordinator measurements.
"""
from __future__ import annotations

import logging
import math
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_MODE,
    CONF_MUNICIPALITY_CODE,
    CONF_STATION_CODE,
    CONF_STATION_NAME,
    CONF_MUNICIPALITY_NAME,
    CONF_SENSOR_HUMIDITY,
    CONF_SENSOR_RAIN_INTENSITY,
    CONF_SENSOR_TEMPERATURE,
    CONF_SENSOR_WIND_SPEED,
    DOMAIN,
    INTEGRATION_VERSION,
    MANUFACTURER,
    MODE_EXTERNAL,
    MODE_LOCAL,
)
from .coordinator import MeteocatCoordinator
from .utils import calculate_utci

_LOGGER = logging.getLogger(__name__)

_LOCAL_CONDITION_SOURCES = {
    "freezing": ("temperature",),
    "raining": ("rain",),
    "windy": ("wind",),
    "muggy": ("temperature", "humidity", "wind"),
}
_LOCAL_SOURCE_CONFIG_KEYS = {
    "temperature": CONF_SENSOR_TEMPERATURE,
    "humidity": CONF_SENSOR_HUMIDITY,
    "rain": CONF_SENSOR_RAIN_INTENSITY,
    "wind": CONF_SENSOR_WIND_SPEED,
}
_EXTERNAL_CONDITION_CODES = {
    "freezing": {"temperature": 32},
    "windy": {"wind": 30},
    "muggy": {"temperature": 32, "humidity": 33, "wind": 30},
}
_CONDITION_ICONS = {
    "freezing": "mdi:snowflake-thermometer",
    "raining": "mdi:weather-rainy",
    "windy": "mdi:weather-windy",
    "muggy": "mdi:water-percent",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteocat binary sensor entities."""
    coordinator: MeteocatCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Get entity name based on mode
    mode = entry.data.get(CONF_MODE, MODE_EXTERNAL)
    station_code = entry.data.get(CONF_STATION_CODE, "")
    
    if mode == MODE_EXTERNAL:
        station_name = entry.data.get(CONF_STATION_NAME, f"Estació {station_code}")
        entity_name = station_name
        entity_name_with_code = f"{station_name} {station_code}"
    else:
        municipality_code = entry.data.get(CONF_MUNICIPALITY_CODE, "")
        entity_name = entry.data.get(CONF_MUNICIPALITY_NAME, f"Municipi {municipality_code}")
        entity_name_with_code = entity_name
    
    entities: list[BinarySensorEntity] = [
        MeteocatUpdateStatusBinarySensor(
            coordinator,
            entry,
            entity_name,
            entity_name_with_code,
            mode,
            station_code if mode == MODE_EXTERNAL else None,
        )
    ]

    if mode == MODE_EXTERNAL:
        available_codes = _get_external_measurement_codes(coordinator)
        for condition, source_codes in _EXTERNAL_CONDITION_CODES.items():
            if all(str(code) in available_codes for code in source_codes.values()):
                entities.append(
                    MeteocatCalculatedConditionBinarySensor(
                        coordinator,
                        entry,
                        entity_name,
                        entity_name_with_code,
                        mode,
                        condition,
                    )
                )
    else:
        configured_sources = {
            source: _get_configured_entity_id(entry, config_key)
            for source, config_key in _LOCAL_SOURCE_CONFIG_KEYS.items()
        }
        for condition, required_sources in _LOCAL_CONDITION_SOURCES.items():
            if all(configured_sources[source] for source in required_sources):
                entities.append(
                    MeteocatCalculatedConditionBinarySensor(
                        coordinator,
                        entry,
                        entity_name,
                        entity_name_with_code,
                        mode,
                        condition,
                        configured_sources,
                    )
                )

    async_add_entities(entities)


def _get_configured_entity_id(entry: ConfigEntry, key: str) -> str | None:
    """Return the first configured source entity ID."""
    entity_id = entry.data.get(key)
    if isinstance(entity_id, list):
        entity_id = entity_id[0] if entity_id else None
    return entity_id if isinstance(entity_id, str) and entity_id else None


def _get_external_measurement_codes(coordinator: MeteocatCoordinator) -> set[str]:
    """Return XEMA measurement codes available for the configured station."""
    data = coordinator.data
    measurements = data.get("measurements") if isinstance(data, dict) else None
    if not isinstance(measurements, list) or not measurements:
        return set()

    station = measurements[0]
    if not isinstance(station, dict):
        return set()
    variables = station.get("variables", [])
    if not isinstance(variables, list):
        return set()
    return {
        str(variable["codi"])
        for variable in variables
        if isinstance(variable, dict) and variable.get("codi") is not None
    }


class MeteocatCalculatedConditionBinarySensor(
    CoordinatorEntity[MeteocatCoordinator], BinarySensorEntity
):
    """Binary sensor for a calculated local or XEMA weather condition."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        mode: str,
        condition: str,
        configured_sources: dict[str, str | None] | None = None,
    ) -> None:
        """Initialize a calculated condition sensor."""
        super().__init__(coordinator)

        self._mode = mode
        self._condition = condition
        self._configured_sources = configured_sources or {}
        self._attr_unique_id = f"{entry.entry_id}_{condition}"
        self._attr_translation_key = condition
        self._attr_icon = _CONDITION_ICONS[condition]

        if mode == MODE_EXTERNAL:
            base_name = entity_name.replace(
                f" {entry.data.get(CONF_STATION_CODE, '')}", ""
            ).lower().replace(" ", "_")
            code = entry.data.get(CONF_STATION_CODE, "").lower().replace(" ", "_")
            self.entity_id = f"binary_sensor.{base_name}_{code}_{condition}"
            model = "Estació XEMA"
        else:
            self.entity_id = (
                f"binary_sensor.{entity_name.lower().replace(' ', '_')}_{condition}"
            )
            model = "Estació Local"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": MANUFACTURER,
            "model": model,
            "sw_version": INTEGRATION_VERSION,
        }

    async def async_added_to_hass(self) -> None:
        """Subscribe to configured local sensor changes."""
        await super().async_added_to_hass()
        if self._mode == MODE_LOCAL:
            source_entity_ids = [
                entity_id
                for entity_id in self._configured_sources.values()
                if entity_id is not None
            ]
            if source_entity_ids:
                self.async_on_remove(
                    async_track_state_change_event(
                        self.hass, source_entity_ids, self._handle_local_update
                    )
                )

    @callback
    def _handle_local_update(self, event: Event) -> None:
        """Refresh the calculated state after a local source changes."""
        self.async_write_ha_state()

    def _get_value(self, source: str) -> float | None:
        """Read a numeric value from the configured source."""
        if self._mode == MODE_LOCAL:
            entity_id = self._configured_sources.get(source)
            if entity_id is None:
                return None
            state = self.hass.states.get(entity_id)
            if state is None or state.state in ("unknown", "unavailable"):
                return None
            raw_value = state.state
        else:
            code = _EXTERNAL_CONDITION_CODES.get(self._condition, {}).get(source)
            if code is None:
                return None
            data = self.coordinator.data
            measurements = data.get("measurements", []) if isinstance(data, dict) else []
            if not isinstance(measurements, list) or not measurements:
                return None
            station = measurements[0]
            if not isinstance(station, dict):
                return None
            variables = station.get("variables", [])
            if not isinstance(variables, list):
                return None
            raw_value = None
            for variable in variables:
                if (
                    isinstance(variable, dict)
                    and str(variable.get("codi")) == str(code)
                ):
                    lectures = variable.get("lectures", [])
                    if isinstance(lectures, list) and lectures:
                        reading = lectures[-1]
                        if isinstance(reading, dict):
                            raw_value = reading.get("valor")
                    break

        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            return None
        return value if math.isfinite(value) else None

    def _get_condition_values(self) -> dict[str, float | None]:
        """Read all values required to calculate this condition."""
        if self._mode == MODE_LOCAL:
            sources = _LOCAL_CONDITION_SOURCES[self._condition]
        else:
            sources = tuple(_EXTERNAL_CONDITION_CODES[self._condition])
        return {source: self._get_value(source) for source in sources}

    @property
    def is_on(self) -> bool:
        """Return whether the configured weather condition is active."""
        values = self._get_condition_values()
        if any(value is None for value in values.values()):
            return False

        if self._condition == "freezing":
            return values["temperature"] <= 0
        if self._condition == "raining":
            return values["rain"] > 0
        if self._condition == "windy":
            return values["wind"] > 0

        wind_speed = values["wind"]
        if self._mode == MODE_EXTERNAL:
            wind_speed *= 3.6
        return calculate_utci(
            values["temperature"],
            values["humidity"],
            wind_speed,
        ) > 25

    @property
    def available(self) -> bool:
        """Return whether all required source values are available."""
        return all(
            value is not None for value in self._get_condition_values().values()
        )


class MeteocatUpdateStatusBinarySensor(CoordinatorEntity[MeteocatCoordinator], BinarySensorEntity):
    """Binary sensor for monitoring update status.
    
    Reports whether there are problems with data updates by checking ALL
    API calls based on the configured mode:
    - MODE_EXTERNAL: Checks measurements data
    - MODE_LOCAL: Checks forecast and forecast_hourly data
    
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
        
        self._attr_unique_id = f"{entry.entry_id}_update_state"
        self._attr_translation_key = "update_state"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_has_entity_name = False
        self._attr_name = "Última actualització correcte"
        
        # Set explicit entity_id based on mode
        if mode == MODE_EXTERNAL and station_code:
            base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
            code_lower = station_code.lower()
            self.entity_id = f"binary_sensor.{base_name}_{code_lower}_update_state"
        else:
            base_name = entity_name.lower().replace(" ", "_")
            self.entity_id = f"binary_sensor.{base_name}_update_state"
        
        # Set device info to group with other entities
        if mode == MODE_EXTERNAL:
            model = "Estació Externa"
        else:
            model = "Estació Local"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": MANUFACTURER,
            "model": model,
            "sw_version": INTEGRATION_VERSION,
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
        
        # For MODE_EXTERNAL: check measurements (always required)
        if self._mode == MODE_EXTERNAL:
            measurements = self.coordinator.data.get("measurements")
            if measurements is None or (isinstance(measurements, (list, dict)) and len(measurements) == 0):
                failed_calls.append("measurements")
        
        # For both modes: check forecasts if municipality_code exists
        # In MODE_EXTERNAL: forecasts are optional (only if station has municipality)
        # In MODE_LOCAL: forecasts are always expected
        municipality_code = self.coordinator.data.get("municipality_code")
        
        if municipality_code or self._mode == MODE_LOCAL:
            # Check daily forecast (only if enabled)
            if self.coordinator.enable_forecast_daily:
                forecast = self.coordinator.data.get("forecast")
                if forecast is None or (isinstance(forecast, (list, dict)) and len(forecast) == 0):
                    failed_calls.append("forecast")
            
            # Check hourly forecast (only if enabled)
            if self.coordinator.enable_forecast_hourly:
                forecast_hourly = self.coordinator.data.get("forecast_hourly")
                if forecast_hourly is None or (isinstance(forecast_hourly, (list, dict)) and len(forecast_hourly) == 0):
                    failed_calls.append("forecast_hourly")
        
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
                
                # Check measurements (MODE_EXTERNAL only)
                if self._mode == MODE_EXTERNAL:
                    measurements = self.coordinator.data.get("measurements")
                    if measurements is None:
                        failed_calls.append("measurements (API call failed)")
                    elif isinstance(measurements, (list, dict)) and len(measurements) == 0:
                        failed_calls.append("measurements (empty/quota exhausted)")
                
                # Check forecasts (both modes if municipality_code exists)
                municipality_code = self.coordinator.data.get("municipality_code")
                if municipality_code or self._mode == MODE_LOCAL:
                    if self.coordinator.enable_forecast_daily:
                        forecast = self.coordinator.data.get("forecast")
                        if forecast is None:
                            failed_calls.append("forecast (API call failed)")
                        elif isinstance(forecast, (list, dict)) and len(forecast) == 0:
                            failed_calls.append("forecast (empty/quota exhausted)")
                    
                    if self.coordinator.enable_forecast_hourly:
                        forecast_hourly = self.coordinator.data.get("forecast_hourly")
                        if forecast_hourly is None:
                            failed_calls.append("forecast_hourly (API call failed)")
                        elif isinstance(forecast_hourly, (list, dict)) and len(forecast_hourly) == 0:
                            failed_calls.append("forecast_hourly (empty/quota exhausted)")
                
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
