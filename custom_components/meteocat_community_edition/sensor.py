"""Sensor entities for Meteocat (Community Edition).

This module provides all sensor entities for both MODE_EXTERNAL and MODE_LOCAL.

Geographic sensors (Comarca, Municipi, Prov\u00edncia):
- Data source: entry.data (static metadata saved during config_flow)
- NO API calls during runtime (quota optimization)
- Conditionally created based on data availability

Timestamp sensors:
- \u00daltima actualitzaci\u00f3: Last successful update time (from coordinator)
- Pr\u00f2xima actualitzaci\u00f3: Next scheduled update time (from coordinator.next_scheduled_update)
- Category: diagnostic

Last updated: 2025-11-27
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    PERCENTAGE,
    DEGREE,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers import entity_registry as er
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback, State
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.typing import EventType

from .utils import calculate_utci
from .const import (
    ATTRIBUTION,
    METEOCAT_CONDITION_MAP,
    CONF_COMARCA_NAME,
    CONF_MODE,
    CONF_MUNICIPALITY_CODE,
    CONF_MUNICIPALITY_NAME,
    CONF_STATION_CODE,
    CONF_STATION_NAME,
    CONF_SENSOR_TEMPERATURE,
    CONF_SENSOR_HUMIDITY,
    CONF_SENSOR_WIND_SPEED,
    DOMAIN,
    MODE_LOCAL,
    MODE_EXTERNAL,
    XEMA_VARIABLES,
)
from .coordinator import MeteocatCoordinator

_LOGGER = logging.getLogger(__name__)


# Sensor types configuration
# Maps variable code to sensor configuration
SENSOR_TYPES: dict[int, dict[str, Any]] = {
    32: {  # Temperature
        "key": "temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:thermometer",
    },
    33: {  # Humidity
        "key": "humidity",
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:water-percent",
    },
    34: {  # Pressure
        "key": "pressure",
        "device_class": SensorDeviceClass.PRESSURE,
        "unit": UnitOfPressure.HPA,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:gauge",
    },
    30: {  # Wind Speed
        "key": "wind_speed",
        "device_class": SensorDeviceClass.WIND_SPEED,
        "unit": UnitOfSpeed.METERS_PER_SECOND,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:weather-windy",
    },
    31: {  # Wind Direction
        "key": "wind_direction",
        "device_class": None,
        "unit": DEGREE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:compass",
    },
    35: {  # Precipitation
        "key": "precipitation",
        "device_class": SensorDeviceClass.PRECIPITATION,
        "unit": UnitOfPrecipitationDepth.MILLIMETERS,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:weather-rainy",
    },
    36: {  # Solar Radiation
        "key": "solar_radiation",
        "device_class": SensorDeviceClass.IRRADIANCE,
        "unit": "W/m\u00b2",
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-power",
    },
}


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
    mode = entry.data.get(CONF_MODE, MODE_EXTERNAL)
    station_code = entry.data.get(CONF_STATION_CODE, "")
    municipality_code = entry.data.get(CONF_MUNICIPALITY_CODE, "")
    
    if mode == MODE_EXTERNAL:
        station_name = entry.data.get(CONF_STATION_NAME, f"Estaci\u00f3 {station_code}")
        entity_name = station_name  # Visual name without code (for forecast sensors)
        entity_name_with_code = f"{station_name} {station_code}"  # For device grouping
        
        # Add XEMA sensors
        for variable_code in SENSOR_TYPES:
            entities.append(
                MeteocatXemaSensor(coordinator, entry, entity_name, variable_code)
            )
        
        # Add UTCI Sensor (External)
        entities.append(MeteocatUTCISensor(coordinator, entry, entity_name_with_code))
    else:
        entity_name = entry.data.get(CONF_MUNICIPALITY_NAME, f"Municipi {municipality_code}")
        entity_name_with_code = entity_name  # For device grouping

        # Add UTCI Sensor (Local)
        if (entry.data.get(CONF_SENSOR_TEMPERATURE) and 
            entry.data.get(CONF_SENSOR_HUMIDITY) and 
            entry.data.get(CONF_SENSOR_WIND_SPEED)):
            entities.append(MeteocatUTCISensor(coordinator, entry, entity_name_with_code))
    
    # Clean up forecast sensors if disabled or not supported in current mode
    try:
        registry = er.async_get(hass)
        for forecast_type in ["hourly", "daily"]:
            # Check if enabled config
            is_enabled = getattr(coordinator, f"enable_forecast_{forecast_type}", False)
            
            # Sensors are only supported in LOCAL mode currently
            should_exist = (mode == MODE_LOCAL) and is_enabled
            
            if not should_exist:
                unique_id = f"{entry.entry_id}_forecast_{forecast_type}"
                if entity_id := registry.async_get_entity_id("sensor", DOMAIN, unique_id):
                    _LOGGER.debug("Removing disabled/unsupported forecast sensor: %s", entity_id)
                    registry.async_remove(entity_id)
    except Exception as err:
        _LOGGER.warning("Error cleaning up disabled sensors: %s", err)

    # Add forecast sensors for local mode
    if mode == MODE_LOCAL:
        if coordinator.enable_forecast_hourly:
            entities.append(MeteocatForecastSensor(coordinator, entry, entity_name_with_code, entity_name, "hourly"))
        if coordinator.enable_forecast_daily:
            entities.append(MeteocatForecastSensor(coordinator, entry, entity_name_with_code, entity_name, "daily"))
            
        # Add municipality info sensors
        entities.extend([
            MeteocatMunicipalityNameSensor(coordinator, entry, entity_name, entity_name_with_code, municipality_code),
            MeteocatComarcaNameSensor(coordinator, entry, entity_name, entity_name_with_code, municipality_code),
        ])
        
        # Add province name sensor if available
        if entry.data.get("provincia_name"):
            entities.append(
                MeteocatProvinciaNameSensor(coordinator, entry, entity_name, entity_name_with_code, municipality_code)
            )
        
        # Add coordinate sensors if data available
        if entry.data.get("municipality_lat") is not None:
            entities.append(
                MeteocatMunicipalityLatitudeSensor(coordinator, entry, entity_name, entity_name_with_code, municipality_code)
            )
        if entry.data.get("municipality_lon") is not None:
            entities.append(
                MeteocatMunicipalityLongitudeSensor(coordinator, entry, entity_name, entity_name_with_code, municipality_code)
            )
    
    # Create quota sensors (for both modes)
    if coordinator.data and coordinator.data.get("quotes"):
        quotes = coordinator.data["quotes"]
        
        # API returns: {"client": {"nom": "..."}, "plans": [{...}, {...}]}
        if isinstance(quotes, dict) and "plans" in quotes:
            for plan in quotes.get("plans", []):
                if isinstance(plan, dict) and "nom" in plan:
                    plan_name = plan.get("nom", "").lower()
                    
                    # Filter out Referència and XDDE plans (never used)
                    if "refer" in plan_name or "xdde" in plan_name:
                        continue
                        
                    # Filter out XEMA plan in LOCAL mode (never used)
                    if mode == MODE_LOCAL and "xema" in plan_name:
                        continue
                        
                    entities.append(
                        MeteocatQuotaSensor(
                            coordinator,
                            entry,
                            plan,
                            entity_name,
                            entity_name_with_code,
                            mode,
                            station_code if mode == MODE_EXTERNAL else None,
                        )
                    )
                    # Add estimation sensors
                    entities.append(
                        MeteocatEstimatedDaysRemainingSensor(
                            coordinator,
                            entry,
                            plan,
                            entity_name,
                            entity_name_with_code,
                            mode,
                            station_code if mode == MODE_EXTERNAL else None,
                        )
                    )
    
    # Add update timestamp sensors (for both modes)
    entities.extend([
        MeteocatLastUpdateSensor(coordinator, entry, entity_name, entity_name_with_code, mode, station_code if mode == MODE_EXTERNAL else None),
        MeteocatNextUpdateSensor(coordinator, entry, entity_name, entity_name_with_code, mode, station_code if mode == MODE_EXTERNAL else None),
        MeteocatUpdateTimeSensor(coordinator, entry, entity_name, entity_name_with_code, mode, 1, station_code if mode == MODE_EXTERNAL else None),
        MeteocatUpdateTimeSensor(coordinator, entry, entity_name, entity_name_with_code, mode, 2, station_code if mode == MODE_EXTERNAL else None),
    ])
    
    # Add forecast update sensors (only for external mode)
    if mode == MODE_EXTERNAL:
        entities.extend([
            MeteocatNextForecastUpdateSensor(coordinator, entry, entity_name, entity_name_with_code, station_code),
            MeteocatLastForecastUpdateSensor(coordinator, entry, entity_name, entity_name_with_code, station_code),
        ])
    
    # Add 3rd update time sensor if configured
    if coordinator.update_time_3:
        entities.append(
            MeteocatUpdateTimeSensor(coordinator, entry, entity_name, entity_name_with_code, mode, 3, station_code if mode == MODE_EXTERNAL else None)
        )
    
    # Add station location sensors (only for external mode)
    if mode == MODE_EXTERNAL:
        entities.extend([
            MeteocatAltitudeSensor(coordinator, entry, entity_name, entity_name_with_code, station_code),
            MeteocatLatitudeSensor(coordinator, entry, entity_name, entity_name_with_code, station_code),
            MeteocatLongitudeSensor(coordinator, entry, entity_name, entity_name_with_code, station_code),
        ])
        
        # Add comarca name sensor (always available for stations)
        entities.append(
            MeteocatStationComarcaNameSensor(coordinator, entry, entity_name, entity_name_with_code, station_code)
        )
        
        # Add municipality name sensor if available
        if entry.data.get("station_municipality_name"):
            entities.append(
                MeteocatStationMunicipalityNameSensor(coordinator, entry, entity_name, entity_name_with_code, station_code)
            )
        
        # Add province name sensor if available
        if entry.data.get("station_provincia_name"):
            entities.append(
                MeteocatStationProvinciaNameSensor(coordinator, entry, entity_name, entity_name_with_code, station_code)
            )
    
    
    # Force enable configuration sensors that might be disabled in registry
    # This prevents them from sticking in disabled state after category changes
    # Use a try-except block to ensure we never block setup if registry operations fail
    try:
        registry = er.async_get(hass)
        
        # Accessing registry entries safely
        entry_entities = [
            entity for entity in registry.entities.values() 
            if entity.config_entry_id == entry.entry_id
        ]
        
        for reg_entity in entry_entities:
            if reg_entity.disabled: 
                uid = reg_entity.unique_id
                should_enable = (
                    uid.endswith("_municipality_name") or
                    uid.endswith("_comarca_name") or
                    uid.endswith("_provincia_name") or
                    "_update_time_" in uid or
                    "_station_municipality_name" in uid or
                    "_station_comarca_name" in uid or
                    "_station_provincia_name" in uid
                )
                
                if should_enable:
                     registry.async_update_entity(reg_entity.entity_id, disabled_by=None)
    except Exception as ex:
        _LOGGER.warning("Could not force enable config sensors: %s", ex)
    
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
        if mode == MODE_EXTERNAL and station_code:
            # XEMA: include station code in entity_id
            base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
            code_lower = station_code.lower()
            self.entity_id = f"sensor.{base_name}_{code_lower}_quota_disponible_{plan_id}"
        else:
            # Municipal: no code in entity_id
            base_name = entity_name.lower().replace(" ", "_")
            self.entity_id = f"sensor.{base_name}_quota_disponible_{plan_id}"
        
        # Set device info to group with weather entity
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA" if mode == MODE_EXTERNAL else "Predicci\u00f3 Municipi",
        }
        
        # Quota sensors are diagnostic information
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
    
    def _normalize_plan_name(self, plan_name: str) -> tuple[str, str]:
        """Normalize plan name for display and entity ID.
        
        Returns:
            tuple: (display_name, entity_id_suffix)
        """
        import re
        import unicodedata

        # Strip accents and normalize to a slug-friendly form
        def _slug(text: str) -> str:
            # Manual replacements for Catalan/Spanish chars to ensure they are handled
            # Using unicode escapes to avoid file encoding issues
            replacements = {
                "\u00e0": "a", "\u00e1": "a", "\u00e8": "e", "\u00e9": "e", "\u00ed": "i", "\u00ef": "i",
                "\u00f2": "o", "\u00f3": "o", "\u00fa": "u", "\u00fc": "u", "\u00e7": "c", "\u00f1": "n",
                "\u00c0": "a", "\u00c1": "a", "\u00c8": "e", "\u00c9": "e", "\u00cd": "i", "\u00cf": "i",
                "\u00d2": "o", "\u00d3": "o", "\u00da": "u", "\u00dc": "u", "\u00c7": "c", "\u00d1": "n"
            }
            for char, repl in replacements.items():
                text = text.replace(char, repl)

            text_norm = unicodedata.normalize("NFD", text)
            text_no_accents = "".join(ch for ch in text_norm if unicodedata.category(ch) != "Mn")
            text_lower = text_no_accents.lower()
            text_spaces = re.sub(r"\s+", "_", text_lower)
            text_clean = re.sub(r"[^a-z0-9_]+", "_", text_spaces)
            slug = re.sub(r"_+", "_", text_clean).strip("_")
            
            # Fix common corruptions caused by encoding issues on some systems
            # e.g. "Predicci_100" -> "prediccio_100"
            # e.g. "refer_ncia_b_sic" -> "referencia_basic"
            slug = slug.replace("predicci_", "prediccio_")
            slug = slug.replace("refer_ncia", "referencia")
            slug = slug.replace("b_sic", "basic")
            
            return slug

        slug = _slug(plan_name)

        def _with_suffix(base: str) -> str:
            if slug.startswith(base):
                tail = slug[len(base):].lstrip("_")
                return f"{base}_{tail}" if tail else base
            return base

        if "prediccio" in slug:
            return ("Predicci\u00f3", _with_suffix("prediccio"))
        if "quota" in slug:
            return ("Quota", _with_suffix("quota"))
        if "xema" in slug:
            return ("XEMA", _with_suffix("xema"))

        # Fallback: use sanitized slug
        return (plan_name, slug)

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


class MeteocatXemaSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Representation of a Meteocat XEMA sensor."""

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        variable_code: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._variable_code = variable_code
        self._sensor_config = SENSOR_TYPES[variable_code]
        
        station_code = entry.data.get(CONF_STATION_CODE, "")
        key = self._sensor_config["key"]
        
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_has_entity_name = True
        self._attr_translation_key = key
        
        self._attr_device_class = self._sensor_config["device_class"]
        self._attr_native_unit_of_measurement = self._sensor_config["unit"]
        self._attr_state_class = self._sensor_config["state_class"]
        self._attr_icon = self._sensor_config["icon"]
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{entity_name} {station_code}",
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA",
        }

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        measurements = self.coordinator.data.get("measurements")
        if not measurements or not isinstance(measurements, list):
            return None
        
        # API returns list of stations, get first one
        station_data = measurements[0]
        variables = station_data.get("variables", [])
        
        # Find measurement for this variable code
        for variable in variables:
            if variable.get("codi") == self._variable_code:
                lectures = variable.get("lectures", [])
                if lectures:
                     # Special handling for Precipitation (35): Daily accumulation
                    if self._variable_code == 35:
                        total_precip = 0.0
                        for reading in lectures:
                            valor = reading.get("valor")
                            if valor is not None:
                                try:
                                    total_precip += float(valor)
                                except (ValueError, TypeError):
                                    continue
                        # Round to 1 decimal place as per convention
                        return round(total_precip, 1)
                    
                    # Default behavior for other sensors: return last value
                    return lectures[-1].get("valor")
        
        return None


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
        self._attr_has_entity_name = True
        if forecast_type == "hourly":
            self._attr_translation_key = "forecast_hourly"
        else:
            self._attr_translation_key = "forecast_daily"
        
        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Predicci\u00f3 Municipi",
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
            if not self.coordinator.data.get("forecast_hourly"):
                return {}
            # Only return filtered HA format to avoid exceeding DB size limit (16KB)
            return {
                "forecast_ha": self._get_forecast_hourly(),
            }
        else:
            if not self.coordinator.data.get("forecast"):
                return {}
            # Only return filtered HA format for consistency and DB optimization
            return {
                "forecast_ha": self._get_forecast_daily(),
            }

    def _get_forecast_hourly(self) -> list[dict[str, Any]]:
        """Return the hourly forecast in HA format."""
        forecast_hourly = self.coordinator.data.get("forecast_hourly")
        if not forecast_hourly:
            return []
        
        forecasts = []
        
        dies = forecast_hourly.get("dies", [])
        for dia in dies:
            variables = dia.get("variables", {})
            
            # Get hourly variables with their values arrays
            temp_data = variables.get("temp", {})
            estat_cel_data = variables.get("estatCel", {})
            precip_data = variables.get("precipitacio", {})
            
            temp_valors = temp_data.get("valors", [])
            estat_valors = estat_cel_data.get("valors", [])
            precip_valors = precip_data.get("valors", [])
            
            # Build dictionaries by timestamp
            temp_dict = {h.get("data"): h.get("valor") for h in temp_valors}
            estat_dict = {h.get("data"): h.get("valor") for h in estat_valors}
            precip_dict = {h.get("data"): h.get("valor") for h in precip_valors}
            
            # Get all unique timestamps
            all_times = set(temp_dict.keys()) | set(estat_dict.keys()) | set(precip_dict.keys())
            
            for time_str in sorted(all_times):
                if time_str:
                    forecast_item = {
                        "datetime": time_str,
                    }
                    
                    if time_str in temp_dict:
                        try:
                            forecast_item["temperature"] = float(temp_dict[time_str])
                        except (ValueError, TypeError):
                            pass
                    
                    if time_str in estat_dict:
                        condition = METEOCAT_CONDITION_MAP.get(estat_dict[time_str], "cloudy")
                        forecast_item["condition"] = condition
                    
                    if time_str in precip_dict:
                        try:
                            forecast_item["precipitation"] = float(precip_dict[time_str])
                        except (ValueError, TypeError):
                            pass
                    
                    forecasts.append(forecast_item)
        
        return forecasts[:72]  # Limit to 72 hours

    def _get_forecast_daily(self) -> list[dict[str, Any]]:
        """Return the daily forecast in HA format."""
        forecast = self.coordinator.data.get("forecast")
        if not forecast:
            return []
        
        forecasts = []
        
        dies = forecast.get("dies", [])[:8]  # Limit to 8 days
        for dia in dies:
            data = dia.get("data")
            if not data:
                continue
            
            variables = dia.get("variables", {})
            
            forecast_item = {
                "datetime": data,
            }
            
            # Temperature min/max (simple objects with valor)
            tmin = variables.get("tmin", {})
            if isinstance(tmin, dict):
                valor = tmin.get("valor")
                if valor is not None:
                    try:
                        forecast_item["templow"] = float(valor)
                    except (ValueError, TypeError):
                        pass
            
            tmax = variables.get("tmax", {})
            if isinstance(tmax, dict):
                valor = tmax.get("valor")
                if valor is not None:
                    try:
                        forecast_item["temperature"] = float(valor)
                    except (ValueError, TypeError):
                        pass
            
            # Condition (simple object with valor)
            estat_cel = variables.get("estatCel", {})
            if isinstance(estat_cel, dict):
                estat_code = estat_cel.get("valor")
                if estat_code is not None:
                    condition = METEOCAT_CONDITION_MAP.get(estat_code, "cloudy")
                    forecast_item["condition"] = condition
            
            # Precipitation (simple object with valor, percentage)
            precip = variables.get("precipitacio", {})
            if isinstance(precip, dict):
                valor = precip.get("valor")
                if valor is not None:
                    try:
                        forecast_item["precipitation"] = float(valor)
                    except (ValueError, TypeError):
                        pass
            
            forecasts.append(forecast_item)
            
        return forecasts

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:weather-partly-cloudy" if self._forecast_type == "hourly" else "mdi:calendar-week"


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
        self._attr_has_entity_name = True
        self._attr_translation_key = "last_update"
        
        # Set explicit entity_id based on mode
        if mode == MODE_EXTERNAL and station_code:
            base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
            code_lower = station_code.lower()
            self.entity_id = f"sensor.{base_name}_{code_lower}_last_measurements_update"
        else:
            base_name = entity_name.lower().replace(" ", "_")
            self.entity_id = f"sensor.{base_name}_last_measurements_update"
        
        # Each entry is a separate device under a shared hub
        hub_id = f"{DOMAIN}_hub_external" if mode == MODE_EXTERNAL else f"{DOMAIN}_hub_local"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA" if mode == MODE_EXTERNAL else "Predicci\u00f3 Municipi",

        }
        
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the last update timestamp."""
        if self._mode == MODE_EXTERNAL:
            return self.coordinator.last_measurements_update
        return self.coordinator.last_successful_update_time

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:update"


class MeteocatNextForecastUpdateSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Sensor showing next scheduled forecast update timestamp (External Mode)."""

    _attr_attribution = ATTRIBUTION
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        station_code: str,
    ) -> None:
        """Initialize the next forecast update sensor."""
        super().__init__(coordinator)
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._station_code = station_code
        
        self._attr_unique_id = f"{entry.entry_id}_next_forecast_update"
        self._attr_has_entity_name = True
        self._attr_translation_key = "next_forecast_update"
        
        base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
        code_lower = station_code.lower()
        self.entity_id = f"sensor.{base_name}_{code_lower}_next_forecast_update"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA",
        }
        
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the next forecast update time."""
        return getattr(self.coordinator, "next_forecast_update", None)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:calendar-clock"


class MeteocatLastForecastUpdateSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Sensor showing last forecast update timestamp (External Mode)."""

    _attr_attribution = ATTRIBUTION
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        station_code: str,
    ) -> None:
        """Initialize the last forecast update sensor."""
        super().__init__(coordinator)
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._station_code = station_code
        
        self._attr_unique_id = f"{entry.entry_id}_last_forecast_update"
        self._attr_has_entity_name = True
        self._attr_translation_key = "last_forecast_update"
        
        base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
        code_lower = station_code.lower()
        self.entity_id = f"sensor.{base_name}_{code_lower}_last_forecast_update"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA",
        }
        
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the last forecast update time."""
        return getattr(self.coordinator, "last_forecast_update", None)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:calendar-check"


class MeteocatNextUpdateSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Sensor showing next scheduled update timestamp.
    
    This diagnostic sensor displays when the next automatic data update will occur.
    
    Data source: coordinator.next_scheduled_update
    - Updated automatically when coordinator schedules the next update
    - Reflects actual scheduled time (not calculated from last update)
    - Shows exact time configured in update_time_1 or update_time_2
    
    Device class: timestamp
    Entity category: diagnostic
    
    Last updated: 2025-11-27
    """

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
        self._attr_has_entity_name = True
        self._attr_translation_key = "next_update"
        
        # Set explicit entity_id based on mode
        if mode == MODE_EXTERNAL and station_code:
            base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
            code_lower = station_code.lower()
            self.entity_id = f"sensor.{base_name}_{code_lower}_next_measurements_update"
        else:
            base_name = entity_name.lower().replace(" ", "_")
            self.entity_id = f"sensor.{base_name}_next_measurements_update"
        
        # Each entry is a separate device under a shared hub
        hub_id = f"{DOMAIN}_hub_external" if mode == MODE_EXTERNAL else f"{DOMAIN}_hub_local"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA" if mode == MODE_EXTERNAL else "Predicci\u00f3 Municipi",

        }
        
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the next update time."""
        return self.coordinator.next_scheduled_update

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:clock-outline"


class MeteocatUpdateTimeSensor(SensorEntity):
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
        self._attr_available = True
        # Do not inherit from CoordinatorEntity to keep it always available
        
        self._coordinator = coordinator  # Keep reference for helper property
        self._entity_name = entity_name
        self._device_name = device_name
        self._mode = mode
        self._station_code = station_code
        self._time_number = time_number
        
        self._attr_unique_id = f"{entry.entry_id}_update_time_{time_number}"
        self._attr_has_entity_name = True
        self._attr_translation_key = "update_time"
        self._attr_translation_placeholders = {"number": str(time_number)}
        
        # Set explicit entity_id based on mode
        if mode == MODE_EXTERNAL and station_code:
            base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
            code_lower = station_code.lower()
            self.entity_id = f"sensor.{base_name}_{code_lower}_update_time_{time_number}"
        else:
            base_name = entity_name.lower().replace(" ", "_")
            self.entity_id = f"sensor.{base_name}_update_time_{time_number}"
        
        # Each entry is a separate device under a shared hub
        hub_id = f"{DOMAIN}_hub_external" if mode == MODE_EXTERNAL else f"{DOMAIN}_hub_local"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA" if mode == MODE_EXTERNAL else "Predicci\u00f3 Municipi",

        }
        
        # Update time sensors are configuration information
        # self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = True
        self._attr_available = True
        self._attr_should_poll = False

    @property
    def native_value(self):
        """Return the configured update time."""
        if self._time_number == 1:
            return self._coordinator.update_time_1
        elif self._time_number == 2:
            return self._coordinator.update_time_2
        return self._coordinator.update_time_3

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:clock-time-four-outline"


class MeteocatAltitudeSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Sensor showing station altitude.
    
    Data obtained from coordinator.data['station'] which is cached in entry.data.
    Cached data prevents unnecessary API calls on Home Assistant restart.
    """

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
        self._attr_available = True
        super().__init__(coordinator)
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._station_code = station_code
        self._entry = entry
        
        self._attr_unique_id = f"{entry.entry_id}_altitude"
        self._attr_name = "Altitud"
        
        # Set explicit entity_id
        base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
        code_lower = station_code.lower()
        self.entity_id = f"sensor.{base_name}_{code_lower}_altitude"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA",
        }
        
        # Geographic sensors are configuration information
        # self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = True

    @property
    def native_value(self) -> float | None:
        # Prefer fresh data from coordinator.data
        station_data = self.coordinator.data.get("station")
        if station_data and isinstance(station_data, dict):
            alt = station_data.get("altitud")
            if alt is not None:
                return alt
        
        # Fallback to cached entry.data if coordinator.data empty (quota exhausted)
        station_data = self._entry.data.get("_station_data")
        if station_data and isinstance(station_data, dict):
            return station_data.get("altitud")
        
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Configuration sensors are always available
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:elevation-rise"


class MeteocatLatitudeSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Sensor showing station latitude.
    
    Data obtained from coordinator.data['station'] which is cached in entry.data.
    Cached data prevents unnecessary API calls on Home Assistant restart.
    """

    _attr_attribution = ATTRIBUTION
    _attr_native_unit_of_measurement = "\u00b0"

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        station_code: str,
    ) -> None:
        """Initialize the latitude sensor."""
        self._attr_available = True
        super().__init__(coordinator)
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._station_code = station_code
        self._entry = entry
        
        self._attr_unique_id = f"{entry.entry_id}_latitude"
        self._attr_has_entity_name = True
        self._attr_translation_key = "latitude"
        
        # Set explicit entity_id
        base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
        code_lower = station_code.lower()
        self.entity_id = f"sensor.{base_name}_{code_lower}_latitude"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA",
        }
        
        # Geographic sensors are configuration information
        # self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = True
        self._attr_available = True

    @property
    def native_value(self) -> float | None:
        """Return the station latitude in degrees."""
        # Prefer fresh data from coordinator.data
        station_data = self.coordinator.data.get("station")
        if station_data and isinstance(station_data, dict):
            coordenades = station_data.get("coordenades", {})
            lat = coordenades.get("latitud")
            if lat is not None:
                return lat
        
        # Fallback to cached entry.data if coordinator.data empty (quota exhausted)
        station_data = self._entry.data.get("_station_data")
        if station_data and isinstance(station_data, dict):
            coordenades = station_data.get("coordenades", {})
            return coordenades.get("latitud")
        
        return None

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:latitude"


class MeteocatLongitudeSensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """Sensor showing station longitude.
    
    Data obtained from coordinator.data['station'] which is cached in entry.data.
    Cached data prevents unnecessary API calls on Home Assistant restart.
    """

    _attr_attribution = ATTRIBUTION
    _attr_native_unit_of_measurement = "\u00b0"

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        station_code: str,
    ) -> None:
        """Initialize the longitude sensor."""
        self._attr_available = True
        super().__init__(coordinator)
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._station_code = station_code
        self._entry = entry
        
        self._attr_unique_id = f"{entry.entry_id}_longitude"
        self._attr_has_entity_name = True
        self._attr_translation_key = "longitude"
        
        # Set explicit entity_id
        base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
        code_lower = station_code.lower()
        self.entity_id = f"sensor.{base_name}_{code_lower}_longitude"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA",
        }
        
        # Geographic sensors are configuration information
        # self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = True
        self._attr_available = True

    @property
    def native_value(self) -> float | None:
        """Return the station longitude in degrees."""
        # Prefer fresh data from coordinator.data
        station_data = self.coordinator.data.get("station")
        if station_data and isinstance(station_data, dict):
            coordenades = station_data.get("coordenades", {})
            lon = coordenades.get("longitud")
            if lon is not None:
                return lon
        
        # Fallback to cached entry.data if coordinator.data empty (quota exhausted)
        station_data = self._entry.data.get("_station_data")
        if station_data and isinstance(station_data, dict):
            coordenades = station_data.get("coordenades", {})
            return coordenades.get("longitud")
        
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Configuration sensors are always available
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:longitude"


class MeteocatMunicipalityNameSensor(SensorEntity):
    """Sensor showing municipality name.
    
    Data obtained from configuration (entry.data) - no API calls needed.
    """

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        municipality_code: str,
    ) -> None:
        """Initialize the municipality name sensor."""
        self._attr_available = True
        # Do NOT call super().__init__(coordinator) to avoid linkage to API status
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._municipality_code = municipality_code
        self._municipality_name = entry.data.get(CONF_MUNICIPALITY_NAME, "")
        
        self._attr_unique_id = f"{entry.entry_id}_municipality_name"
        self._attr_name = "Municipi"
        
        # Set explicit entity_id
        base_name = entity_name.lower().replace(" ", "_")
        self.entity_id = f"sensor.{base_name}_municipality_name"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Predicci\u00f3 Municipi",
        }
        
        # Municipality name is configuration information
        # self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = True
        self._attr_available = True
        self._attr_should_poll = False

    @property
    def native_value(self) -> str | None:
        """Return the municipality name."""
        return self._municipality_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Configuration sensors are always available
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:city"


class MeteocatComarcaNameSensor(SensorEntity):
    """Sensor showing comarca name.
    
    Data obtained from configuration (entry.data) - no API calls needed.
    """

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        municipality_code: str,
    ) -> None:
        """Initialize the comarca name sensor."""
        self._attr_available = True
        # Do NOT call super().__init__(coordinator) to avoid linkage to API status
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._municipality_code = municipality_code
        self._comarca_name = entry.data.get(CONF_COMARCA_NAME, "")
        
        self._attr_unique_id = f"{entry.entry_id}_comarca_name"
        self._attr_name = "Comarca"
        
        # Set explicit entity_id
        base_name = entity_name.lower().replace(" ", "_")
        self.entity_id = f"sensor.{base_name}_comarca_name"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Predicci\u00f3 Municipi",
        }
        
        # Comarca name is configuration information
        # self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = True
        self._attr_available = True
        self._attr_should_poll = False

    @property
    def native_value(self) -> str | None:
        """Return the comarca name."""
        return self._comarca_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Configuration sensors are always available
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:map"


class MeteocatMunicipalityLatitudeSensor(SensorEntity):
    """Sensor showing municipality latitude.
    
    Data obtained from configuration (entry.data) - no API calls needed.
    Only created if latitude data is available from API during setup.
    """

    _attr_attribution = ATTRIBUTION
    _attr_native_unit_of_measurement = "\u00b0"

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        municipality_code: str,
    ) -> None:
        """Initialize the municipality latitude sensor."""
        self._attr_available = True
        # Do NOT call super().__init__(coordinator) to avoid linkage to API status
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._municipality_code = municipality_code
        self._latitude = entry.data.get("municipality_lat")
        
        self._attr_unique_id = f"{entry.entry_id}_municipality_latitude"
        self._attr_has_entity_name = True
        self._attr_translation_key = "latitude"
        
        # Set explicit entity_id
        base_name = entity_name.lower().replace(" ", "_")
        self.entity_id = f"sensor.{base_name}_municipality_latitude"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Predicci\u00f3 Municipi",
        }
        
        # Municipality sensors provide location information
        # self._attr_entity_category = EntityCategory.CONFIG  # Removed to show in sensors group
        self._attr_entity_registry_enabled_default = True
        self._attr_available = True

    @property
    def native_value(self) -> float | None:
        """Return the municipality latitude."""
        return self._latitude

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Configuration sensors are always available
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:latitude"


class MeteocatMunicipalityLongitudeSensor(SensorEntity):
    """Sensor showing municipality longitude.
    
    Data obtained from configuration (entry.data) - no API calls needed.
    Only created if longitude data is available from API during setup.
    """

    _attr_attribution = ATTRIBUTION
    _attr_native_unit_of_measurement = "\u00b0"

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        municipality_code: str,
    ) -> None:
        """Initialize the municipality longitude sensor."""
        self._attr_available = True
        # Do NOT call super().__init__(coordinator) to avoid linkage to API status
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._municipality_code = municipality_code
        self._longitude = entry.data.get("municipality_lon")
        
        self._attr_unique_id = f"{entry.entry_id}_municipality_longitude"
        self._attr_has_entity_name = True
        self._attr_translation_key = "longitude"
        
        # Set explicit entity_id
        base_name = entity_name.lower().replace(" ", "_")
        self.entity_id = f"sensor.{base_name}_municipality_longitude"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Predicci\u00f3 Municipi",
        }
        
        # Municipality sensors provide location information
        # self._attr_entity_category = EntityCategory.CONFIG  # Removed to show in sensors group
        self._attr_entity_registry_enabled_default = True
        self._attr_available = True

    @property
    def native_value(self) -> float | None:
        """Return the municipality longitude."""
        return self._longitude

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Configuration sensors are always available
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:longitude"


class MeteocatProvinciaNameSensor(SensorEntity):
    """Sensor showing province name.
    
    Data obtained from configuration (entry.data) - no API calls needed.
    Only created if province data is available from API during setup.
    """

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        municipality_code: str,
    ) -> None:
        """Initialize the provincia name sensor."""
        self._attr_available = True
        # Do NOT call super().__init__(coordinator) to avoid linkage to API status
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._municipality_code = municipality_code
        self._provincia_name = entry.data.get("provincia_name", "")
        
        self._attr_unique_id = f"{entry.entry_id}_provincia_name"
        self._attr_name = "Prov\u00edncia"
        
        # Set explicit entity_id
        base_name = entity_name.lower().replace(" ", "_")
        self.entity_id = f"sensor.{base_name}_provincia_name"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Predicci\u00f3 Municipi",
        }
        
        # Provincia name is configuration information
        # self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = True
        self._attr_available = True
        self._attr_should_poll = False

    @property
    def native_value(self) -> str | None:
        """Return the provincia name."""
        return self._provincia_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:map-marker-radius"


class MeteocatStationComarcaNameSensor(SensorEntity):
    """Sensor showing comarca name for a station.
    
    Data obtained from configuration (entry.data) - no API calls needed.
    Always available for stations.
    """

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        station_code: str,
    ) -> None:
        """Initialize the station comarca name sensor."""
        self._attr_available = True
        # Do NOT call super().__init__(coordinator) to avoid linkage to API status
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._station_code = station_code
        self._comarca_name = entry.data.get(CONF_COMARCA_NAME, "")
        
        self._attr_unique_id = f"{entry.entry_id}_station_comarca_name"
        self._attr_name = "Comarca"
        
        # Set explicit entity_id
        base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
        code_lower = station_code.lower()
        self.entity_id = f"sensor.{base_name}_{code_lower}_comarca_name"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA",
        }
        
        # Geographic sensors are configuration information
        # self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = True
        self._attr_available = True
        self._attr_should_poll = False

    @property
    def native_value(self) -> str | None:
        """Return the comarca name."""
        return self._comarca_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Configuration sensors are always available
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:map"


class MeteocatStationMunicipalityNameSensor(SensorEntity):
    """Sensor showing municipality name for a station.
    
    Data obtained from configuration (entry.data) - no API calls needed.
    Only created if municipality data is available from API during setup.
    """

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        station_code: str,
    ) -> None:
        """Initialize the station municipality name sensor."""
         # Do NOT call super().__init__(coordinator) to avoid linkage to API status
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._station_code = station_code
        self._municipality_name = entry.data.get("station_municipality_name", "")
        
        self._attr_unique_id = f"{entry.entry_id}_station_municipality_name"
        self._attr_name = "Municipi"
        
        # Set explicit entity_id
        base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
        code_lower = station_code.lower()
        self.entity_id = f"sensor.{base_name}_{code_lower}_municipality_name"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA",
        }
        
        # Geographic sensors are configuration information
        # self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = True
        self._attr_available = True
        self._attr_should_poll = False

    @property
    def native_value(self) -> str | None:
        """Return the municipality name."""
        return self._municipality_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Configuration sensors are always available
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:city"


class MeteocatStationProvinciaNameSensor(SensorEntity):
    """Sensor showing province name for a station.
    
    Data obtained from configuration (entry.data) - no API calls needed.
    Only created if province data is available from API during setup.
    """

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        station_code: str,
    ) -> None:
        """Initialize the station provincia name sensor."""
         # Do NOT call super().__init__(coordinator) to avoid linkage to API status
        
        self._entity_name = entity_name
        self._device_name = device_name
        self._station_code = station_code
        self._provincia_name = entry.data.get("station_provincia_name", "")
        
        self._attr_unique_id = f"{entry.entry_id}_station_provincia_name"
        self._attr_name = "Prov\u00edncia"
        
        # Set explicit entity_id
        base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
        code_lower = station_code.lower()
        self.entity_id = f"sensor.{base_name}_{code_lower}_provincia_name"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Meteocat Edici\u00f3 Comunit\u00e0ria",
            "model": "Estaci\u00f3 XEMA",
        }
        
        # Geographic sensors are configuration information
        # self._attr_entity_category = EntityCategory.CONFIG
        self._attr_available = True
        self._attr_entity_registry_enabled_default = True
        self._attr_should_poll = False

    @property
    def native_value(self) -> str | None:
        """Return the provincia name."""
        return self._provincia_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Configuration sensors are always available
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:map-marker-radius"




class MeteocatEstimatedDaysRemainingSensor(MeteocatQuotaSensor):
    """Sensor showing estimated days remaining for a plan."""

    _attr_icon = "mdi:calendar-clock"
    _attr_native_unit_of_measurement = "dies"
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
        """Initialize the estimated days remaining sensor."""
        super().__init__(coordinator, entry, plan_data, entity_name, device_name, mode, station_code)
        
        display_name, plan_id = self._normalize_plan_name(self._plan_name)
        self._attr_unique_id = f"{entry.entry_id}_quota_dies_estimats_{plan_id}"
        self._attr_name = f"Dies disponibles {display_name}"
        
        if mode == MODE_EXTERNAL and station_code:
            base_name = entity_name.replace(f" {station_code}", "").lower().replace(" ", "_")
            code_lower = station_code.lower()
            self.entity_id = f"sensor.{base_name}_{code_lower}_quota_dies_estimats_{plan_id}"
        else:
            base_name = entity_name.lower().replace(" ", "_")
            self.entity_id = f"sensor.{base_name}_quota_dies_estimats_{plan_id}"

    def _get_daily_consumption(self) -> int:
        """Calculate estimated daily consumption."""
        # Calculate updates per day based on configuration
        updates_per_day = 0
        if self.coordinator.update_time_1:
            updates_per_day += 1
        if self.coordinator.update_time_2:
            updates_per_day += 1
        if self.coordinator.update_time_3:
            updates_per_day += 1
            
        calls_per_update = 0
        plan_name_lower = self._plan_name.lower()
        
        if "xema" in plan_name_lower:
            if self._mode == MODE_EXTERNAL:
                calls_per_update = 1
        elif "predicci" in plan_name_lower:
            if self.coordinator.enable_forecast_daily:
                calls_per_update += 1
            if self.coordinator.enable_forecast_hourly:
                calls_per_update += 1
        elif "quota" in plan_name_lower:
            calls_per_update = 1
            
        return updates_per_day * calls_per_update

    @property
    def native_value(self) -> float | None:
        """Return the estimated days remaining."""
        available = None
        if self.coordinator.data and self.coordinator.data.get("quotes"):
            quotes = self.coordinator.data["quotes"]
            if isinstance(quotes, dict) and "plans" in quotes:
                for plan in quotes.get("plans", []):
                    if plan.get("nom") == self._plan_name:
                        available = plan.get("consultesRestants")
                        break
        
        if available is None:
            return None
            
        daily_consumption = self._get_daily_consumption()
        
        if daily_consumption == 0:
            return 9999 # Infinite
            
        return round(available / daily_consumption, 1)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = super().extra_state_attributes
        attrs["consum_diari_estimat"] = self._get_daily_consumption()
        return attrs

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:calendar-clock"


class MeteocatUTCISensor(CoordinatorEntity[MeteocatCoordinator], SensorEntity):
    """UTCI Sensor (Universal Thermal Climate Index)."""
    
    _attr_has_entity_name = True
    _attr_translation_key = "utci_index"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    # Icon for UTCI / Thermal sensation
    _attr_icon = "mdi:thermometer-alert"

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        device_name: str,
    ) -> None:
        """Initialize the UTCI sensor."""
        super().__init__(coordinator)
        
        self._entry = entry
        self._mode = entry.data.get(CONF_MODE)
        self._device_name = device_name
        self._attr_unique_id = f"{entry.entry_id}_utci"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": ATTRIBUTION,
        }

        # Local mode input entities
        self._source_temp = entry.data.get(CONF_SENSOR_TEMPERATURE)
        self._source_hum = entry.data.get(CONF_SENSOR_HUMIDITY)
        self._source_wind = entry.data.get(CONF_SENSOR_WIND_SPEED)

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await super().async_added_to_hass()
        
        # In local mode, we want to update instantly when source sensors change
        if self._mode == MODE_LOCAL and self._source_temp and self._source_hum and self._source_wind:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._source_temp, self._source_hum, self._source_wind],
                    self._handle_local_update
                )
            )
            # Initial calculation
            self._update_local_value()

    @callback
    def _handle_local_update(self, event: EventType) -> None:
        """Handle updates from local sensors."""
        self._update_local_value()
        self.async_write_ha_state()

    def _update_local_value(self) -> None:
        """Calculate UTCI from local sensors."""
        try:
            temp_state = self.hass.states.get(self._source_temp)
            hum_state = self.hass.states.get(self._source_hum)
            wind_state = self.hass.states.get(self._source_wind)

            if not temp_state or not hum_state or not wind_state:
                self._attr_native_value = None
                self._attr_available = False
                return

            # Check for unavailable states
            if (temp_state.state in ["unknown", "unavailable"] or 
                hum_state.state in ["unknown", "unavailable"] or 
                wind_state.state in ["unknown", "unavailable"]):
                self._attr_native_value = None
                self._attr_available = False
                return

            temp = float(temp_state.state)
            hum = float(hum_state.state)
            wind_kmh = float(wind_state.state) # Assuming km/h as requested by user

            self._attr_native_value = calculate_utci(temp, hum, wind_kmh)
            self._attr_available = True
            
        except (ValueError, TypeError):
            self._attr_native_value = None
            self._attr_available = False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Only relevant for XEMA stations
        if self._mode == MODE_EXTERNAL:
            self._update_external_value()
            self.async_write_ha_state()

    def _update_external_value(self) -> None:
        """Calculate UTCI from Meteocat data."""
        if not self.coordinator.data or "mesures" not in self.coordinator.data:
            self._attr_native_value = None
            self._attr_available = False
            return

        mesures = self.coordinator.data["mesures"]
        
        # Check if we have required variables (32: Temp, 33: Hum, 30: Wind)
        if 32 not in mesures or 33 not in mesures or 30 not in mesures:
            self._attr_native_value = None
            self._attr_available = False
            return

        try:
            temp = float(mesures[32]["valor"])
            hum = float(mesures[33]["valor"])
            wind_ms = float(mesures[30]["valor"])
            
            # Convert m/s to km/h
            wind_kmh = wind_ms * 3.6
            
            self._attr_native_value = calculate_utci(temp, hum, wind_kmh)
            self._attr_available = True
        except (ValueError, KeyError, TypeError):
            self._attr_native_value = None
            self._attr_available = False

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Custom logic for availability
        if self._mode == MODE_LOCAL:
            # Managed by _update_local_value setting _attr_available
            return self._attr_available
        else:
            # Managed by coordinator + data check
            return super().available and self._attr_available
