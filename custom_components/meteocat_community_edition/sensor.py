"""Sensor entities for Meteocat (Community Edition)."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_MODE,
    CONF_MUNICIPALITY_CODE,
    CONF_MUNICIPALITY_NAME,
    CONF_STATION_CODE,
    CONF_STATION_NAME,
    DOMAIN,
    MODE_MUNICIPI,
    MODE_ESTACIO,
)
from .coordinator import MeteocatCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteocat sensor entities."""
    coordinator: MeteocatCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Create sensor list
    entities: list[SensorEntity] = []
    
    # Get entity name based on mode
    mode = entry.data.get(CONF_MODE, MODE_ESTACIO)
    station_code = entry.data.get(CONF_STATION_CODE, "")
    municipality_code = entry.data.get(CONF_MUNICIPALITY_CODE, "")
    
    if mode == MODE_ESTACIO:
        station_name = entry.data.get(CONF_STATION_NAME, f"Estació {station_code}")
        entity_name = station_name  # Visual name without code (for forecast sensors)
        entity_name_with_code = f"{station_name} {station_code}"  # For device grouping
    else:
        entity_name = entry.data.get(CONF_MUNICIPALITY_NAME, f"Municipi {municipality_code}")
        entity_name_with_code = entity_name  # For device grouping
    
    # Add forecast sensors for municipal mode
    if mode == MODE_MUNICIPI:
        entities.extend([
            MeteocatForecastSensor(coordinator, entry, entity_name_with_code, entity_name, "hourly"),
            MeteocatForecastSensor(coordinator, entry, entity_name_with_code, entity_name, "daily"),
            MeteocatUVSensor(coordinator, entry, entity_name_with_code, entity_name),
        ])
    
    # Create quota sensors (for both modes)
    if coordinator.data and coordinator.data.get("quotes"):
        quotes = coordinator.data["quotes"]
        
        # API returns: {"client": {"nom": "..."}, "plans": [{...}, {...}]}
        if isinstance(quotes, dict) and "plans" in quotes:
            for plan in quotes.get("plans", []):
                if isinstance(plan, dict) and "nom" in plan:
                    entities.append(
                        MeteocatQuotaSensor(
                            coordinator,
                            entry,
                            plan,
                            entity_name,
                            entity_name_with_code,
                            mode,
                            station_code if mode == MODE_ESTACIO else None,
                        )
                    )
    
    # Add update timestamp sensors (for both modes)
    entities.extend([
        MeteocatLastUpdateSensor(coordinator, entry, entity_name, entity_name_with_code, mode, station_code if mode == MODE_ESTACIO else None),
        MeteocatNextUpdateSensor(coordinator, entry, entity_name, entity_name_with_code, mode, station_code if mode == MODE_ESTACIO else None),
        MeteocatUpdateTimeSensor(coordinator, entry, entity_name, entity_name_with_code, mode, 1, station_code if mode == MODE_ESTACIO else None),
        MeteocatUpdateTimeSensor(coordinator, entry, entity_name, entity_name_with_code, mode, 2, station_code if mode == MODE_ESTACIO else None),
    ])
    
    # Add altitude sensor (only for station mode)
    if mode == MODE_ESTACIO:
        entities.append(
            MeteocatAltitudeSensor(coordinator, entry, entity_name, entity_name_with_code, station_code)
        )
    
    async_add_entities(entities)


class MeteocatQuotaSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Representation of a Meteocat API quota sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        plan_data: dict[str, Any],
        entity_name: str,
        device_name: str,
        mode: str,
        station_code: str | None = None,
    ) -> None:
        """Initialize the quota sensor."""
        super().__init__(coordinator)
        
        self._plan_name = plan_data.get("nom", "Unknown")
        self._entity_name = entity_name
        self._device_name = device_name
        self._mode = mode
        self._station_code = station_code
        
        # Normalize plan name for display and ID
        display_name, plan_id = self._normalize_plan_name(self._plan_name)
        
        self._attr_unique_id = f"{entry.entry_id}_quota_{plan_id}"
        self._attr_name = f"Peticions disponibles {display_name}"
        
        # Set explicit entity_id based on mode
        if mode == MODE_ESTACIO and station_code:
            # XEMA: include station code in entity_id
            base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
            code_lower = station_code.lower()
            self.entity_id = f"sensor.{base_name}_{code_lower}_quota_{plan_id}"
        else:
            # Municipal: no code in entity_id
            base_name = entity_name.lower().replace(" ", "_")
            self.entity_id = f"sensor.{base_name}_quota_{plan_id}"
        
        # Set device info to group with weather entity
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edició Comunitària",
            "model": "Estació XEMA" if mode == MODE_ESTACIO else "Predicció Municipi",
        }
        
        # Quota sensors are diagnostic information
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
    
    def _normalize_plan_name(self, plan_name: str) -> tuple[str, str]:
        """Normalize plan name for display and entity ID.
        
        Returns:
            tuple: (display_name, entity_id_suffix)
        """
        plan_lower = plan_name.lower()
        
        # Map plan names to simplified versions
        if "prediccio" in plan_lower or "predicció" in plan_lower:
            return ("Predicció", "prediccio")
        elif "referencia" in plan_lower or "referència" in plan_lower:
            return ("Referència", "referencia")
        elif "xdde" in plan_lower:
            return ("XDDE", "xdde")
        elif "xema" in plan_lower:
            return ("XEMA", "xema")
        else:
            # Fallback: use original name
            clean_id = plan_name.replace(" ", "_").replace("è", "e").replace("à", "a").lower()
            return (plan_name, clean_id)

    @property
    def native_value(self) -> int | None:
        """Return the number of remaining requests."""
        quotes = self.coordinator.data.get("quotes")
        if not quotes or not isinstance(quotes, dict):
            return None
        
        # Find the plan in the plans array
        for plan in quotes.get("plans", []):
            if plan.get("nom") == self._plan_name:
                return plan.get("consultesRestants", 0)
        
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        quotes = self.coordinator.data.get("quotes")
        if not quotes or not isinstance(quotes, dict):
            return {}
        
        # Find the plan in the plans array
        for plan in quotes.get("plans", []):
            if plan.get("nom") == self._plan_name:
                return {
                    "max_consultes": plan.get("maxConsultes", 0),
                    "consultes_realitzades": plan.get("consultesRealitzades", 0),
                    "consultes_restants": plan.get("consultesRestants", 0),
                    "periode": plan.get("periode", ""),
                    "plan": self._plan_name,
                }
        
        return {}

    @property
    def icon(self) -> str:
        """Return the icon."""
        # Show warning icon if quota is low
        if self.native_value is not None:
            if self.native_value == 0:
                return "mdi:alert-circle"
            elif self.native_value < 100:
                return "mdi:alert"
        
        return "mdi:counter"


class MeteocatForecastSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Representation of a Meteocat forecast sensor (hourly or daily)."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        device_name: str,
        entity_name: str,
        forecast_type: str,  # "hourly" or "daily"
    ) -> None:
        """Initialize the forecast sensor."""
        super().__init__(coordinator)
        
        self._forecast_type = forecast_type
        self._device_name = device_name
        self._entity_name = entity_name
        
        # Create unique ID and name
        self._attr_unique_id = f"{entry.entry_id}_forecast_{forecast_type}"
        if forecast_type == "hourly":
            self._attr_name = f"{self._entity_name} Predicció Horària"
        else:
            self._attr_name = f"{self._entity_name} Predicció Diària"
        
        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edició Comunitària",
            "model": "Predicció Municipi",
        }

    @property
    def native_value(self) -> int | None:
        """Return the state (number of forecast periods)."""
        if self._forecast_type == "hourly":
            # Use hourly forecast data
            forecast_hourly = self.coordinator.data.get("forecast_hourly")
            if not forecast_hourly:
                return "0 hores"
            
            # Count total hours
            total = 0
            dies = forecast_hourly.get("dies", [])
            for dia in dies:
                variables = dia.get("variables", {})
                temp_data = variables.get("temp", {})
                valors = temp_data.get("valors", [])
                total += len(valors)
            return f"{total} hores" if total > 0 else "0 hores"
        else:
            # Use daily forecast data
            forecast = self.coordinator.data.get("forecast")
            if not forecast:
                return "0 dies"
            
            dies = forecast.get("dies", [])
            return f"{len(dies)} dies" if dies else "0 dies"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return forecast data as attributes."""
        if self._forecast_type == "hourly":
            forecast_hourly = self.coordinator.data.get("forecast_hourly")
            if not forecast_hourly:
                return {}
            return {"forecast": forecast_hourly}
        else:
            forecast = self.coordinator.data.get("forecast")
            if not forecast:
                return {}
            return {"forecast": forecast}

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:weather-partly-cloudy" if self._forecast_type == "hourly" else "mdi:calendar-week"


class MeteocatUVSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Representation of a Meteocat UV index sensor."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        device_name: str,
        entity_name: str,
    ) -> None:
        """Initialize the UV sensor."""
        super().__init__(coordinator)
        
        self._device_name = device_name
        self._entity_name = entity_name
        
        # Create unique ID and name
        self._attr_unique_id = f"{entry.entry_id}_uv_index"
        self._attr_name = f"{self._entity_name} Predicció Índex UV"

        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edició Comunitària",
            "model": "Predicció Municipi",
        }

    @property
    def native_value(self) -> str | None:
        """Return the state (number of forecast periods)."""
        uv_data = self.coordinator.data.get("uv_index")
        if not uv_data or not isinstance(uv_data, dict):
            return "0 dies"
        
        # Get UV data array
        uvi_array = uv_data.get("uvi", [])
        if not uvi_array:
            return "0 dies"
        
        # Count total days with UV forecast
        total_days = len(uvi_array)
        return f"{total_days} dies" if total_days > 0 else "0 dies"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return UV forecast data as attributes."""
        uv_data = self.coordinator.data.get("uv_index")
        if not uv_data:
            return {}
        
        return {"uv_forecast": uv_data}

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:weather-sunny-alert"


class MeteocatLastUpdateSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Sensor showing last update timestamp."""

    _attr_attribution = ATTRIBUTION
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        mode: str,
        station_code: str | None = None,
    ) -> None:
        """Initialize the last update sensor."""
        super().__init__(coordinator)
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._mode = mode
        self._station_code = station_code
        
        self._attr_unique_id = f"{entry.entry_id}_last_update"
        self._attr_name = "Última actualització"
        
        # Set explicit entity_id based on mode
        if mode == MODE_ESTACIO and station_code:
            base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
            code_lower = station_code.lower()
            self.entity_id = f"sensor.{base_name}_{code_lower}_last_update"
        else:
            base_name = entity_name.lower().replace(" ", "_")
            self.entity_id = f"sensor.{base_name}_last_update"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edició Comunitària",
            "model": "Estació XEMA" if mode == MODE_ESTACIO else "Predicció Municipi",
        }
        
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the last update timestamp."""
        return self.coordinator.last_successful_update_time

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:update"


class MeteocatNextUpdateSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Sensor showing next scheduled update timestamp."""

    _attr_attribution = ATTRIBUTION
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        mode: str,
        station_code: str | None = None,
    ) -> None:
        """Initialize the next update sensor."""
        super().__init__(coordinator)
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._mode = mode
        self._station_code = station_code
        
        self._attr_unique_id = f"{entry.entry_id}_next_update"
        self._attr_name = "Pròxima actualització"
        
        # Set explicit entity_id based on mode
        if mode == MODE_ESTACIO and station_code:
            base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
            code_lower = station_code.lower()
            self.entity_id = f"sensor.{base_name}_{code_lower}_next_update"
        else:
            base_name = entity_name.lower().replace(" ", "_")
            self.entity_id = f"sensor.{base_name}_next_update"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edició Comunitària",
            "model": "Estació XEMA" if mode == MODE_ESTACIO else "Predicció Municipi",
        }
        
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the next update time."""
        from homeassistant.util import dt as dt_util
        
        if self.coordinator.last_successful_update_time and self.coordinator.update_interval:
            return self.coordinator.last_successful_update_time + self.coordinator.update_interval
        return None

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:clock-outline"


class MeteocatUpdateTimeSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Sensor showing configured update time."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        mode: str,
        time_number: int,  # 1 or 2
        station_code: str | None = None,
    ) -> None:
        """Initialize the update time sensor."""
        super().__init__(coordinator)
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._mode = mode
        self._station_code = station_code
        self._time_number = time_number
        
        self._attr_unique_id = f"{entry.entry_id}_update_time_{time_number}"
        self._attr_name = f"Hora d'actualització {time_number}"
        
        # Set explicit entity_id based on mode
        if mode == MODE_ESTACIO and station_code:
            base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
            code_lower = station_code.lower()
            self.entity_id = f"sensor.{base_name}_{code_lower}_update_time_{time_number}"
        else:
            base_name = entity_name.lower().replace(" ", "_")
            self.entity_id = f"sensor.{base_name}_update_time_{time_number}"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edició Comunitària",
            "model": "Estació XEMA" if mode == MODE_ESTACIO else "Predicció Municipi",
        }
        
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the configured update time."""
        if self._time_number == 1:
            return self.coordinator.update_time_1
        return self.coordinator.update_time_2

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:clock-time-four-outline"


class MeteocatAltitudeSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Sensor showing station altitude."""

    _attr_attribution = ATTRIBUTION
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_native_unit_of_measurement = "m"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        station_code: str,
    ) -> None:
        """Initialize the altitude sensor."""
        super().__init__(coordinator)
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._station_code = station_code
        
        self._attr_unique_id = f"{entry.entry_id}_altitude"
        self._attr_name = "Altitud"
        
        # Set explicit entity_id
        base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
        code_lower = station_code.lower()
        self.entity_id = f"sensor.{base_name}_{code_lower}_altitude"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edició Comunitària",
            "model": "Estació XEMA",
        }

    @property
    def native_value(self) -> float | None:
        """Return the station altitude in meters."""
        station_data = self.coordinator.data.get("station")
        if not station_data or not isinstance(station_data, dict):
            return None
        
        return station_data.get("altitud")

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:elevation-rise"
