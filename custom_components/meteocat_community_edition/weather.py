"""Weather entity for Meteocat (Community Edition).

This module provides a Weather entity for MODE_EXTERNAL that combines:
- Current measurements from the station
- Forecast data (hourly and daily)

The weather entity is only created in MODE_EXTERNAL.
MODE_LOCAL uses sensor entities for forecast data.
"""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.weather import (
    Forecast,
    SingleCoordinatorWeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    ATTRIBUTION, 
    METEOCAT_CONDITION_MAP, 
    CONF_STATION_NAME, 
    CONF_MUNICIPALITY_NAME,
    DOMAIN,
    CONF_SENSOR_TEMPERATURE,
    CONF_SENSOR_HUMIDITY,
    CONF_SENSOR_PRESSURE,
    CONF_SENSOR_WIND_SPEED,
    CONF_SENSOR_WIND_BEARING,
    CONF_SENSOR_WIND_GUST,
    CONF_SENSOR_VISIBILITY,
    CONF_SENSOR_UV_INDEX,
    CONF_SENSOR_OZONE,
    CONF_SENSOR_CLOUD_COVERAGE,
    CONF_SENSOR_DEW_POINT,
    CONF_SENSOR_APPARENT_TEMPERATURE,
    CONF_SENSOR_RAIN,
)
from .coordinator import MeteocatCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteocat weather entity."""
    from .const import CONF_MODE, MODE_EXTERNAL
    
    # Only create weather entity in XEMA mode
    mode = entry.data.get(CONF_MODE, MODE_EXTERNAL)
    _LOGGER.info("Weather platform setup - mode: %s", mode)
    
    coordinator: MeteocatCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    if mode == MODE_EXTERNAL:
        _LOGGER.info("Creating weather entity for station: %s", entry.data.get(CONF_STATION_NAME))
        async_add_entities([MeteocatWeather(coordinator, entry)])
    else: # MODE_LOCAL
        _LOGGER.info("Creating local weather entity for municipality: %s", entry.data.get(CONF_MUNICIPALITY_NAME))
        async_add_entities([MeteocatLocalWeather(coordinator, entry)])



class MeteocatWeather(SingleCoordinatorWeatherEntity[MeteocatCoordinator]):
    """Representation of a Meteocat weather entity.
    
    Combines station measurements with forecast data:
    - Current conditions: from station measurements (XEMA API)
    - Forecasts: hourly (72h) and daily (8 days) from Forecast API
    
    Only available in MODE_EXTERNAL.
    """

    @property
    def native_wind_speed(self) -> float | None:
        """Return the current wind speed in km/h from API data (variable code 30)."""
        measurements = self.coordinator.data.get("measurements")
        if not measurements or not isinstance(measurements, list) or not measurements:
            return None
        station_data = measurements[0]
        variables = station_data.get("variables", [])
        for variable in variables:
            if variable.get("codi") == 30:  # Wind speed
                lectures = variable.get("lectures", [])
                if lectures:
                    valor = lectures[-1].get("valor")
                    try:
                        return round(float(valor) * 3.6, 1)  # Convert m/s to km/h
                    except (TypeError, ValueError):
                        return None
        return None

    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
        
        from .const import (
            CONF_STATION_CODE,
            CONF_ENABLE_FORECAST_DAILY,
            CONF_ENABLE_FORECAST_HOURLY,
        )
        
        # Determine supported features based on configuration (check options first, then data)
        self._attr_supported_features = 0
        
        enable_daily = entry.options.get(CONF_ENABLE_FORECAST_DAILY, entry.data.get(CONF_ENABLE_FORECAST_DAILY, True))
        if enable_daily:
            self._attr_supported_features |= WeatherEntityFeature.FORECAST_DAILY
            
        enable_hourly = entry.options.get(CONF_ENABLE_FORECAST_HOURLY, entry.data.get(CONF_ENABLE_FORECAST_HOURLY, False))
        if enable_hourly:
            self._attr_supported_features |= WeatherEntityFeature.FORECAST_HOURLY
        
        station_code = entry.data.get(CONF_STATION_CODE, "")
        station_name = entry.data[CONF_STATION_NAME]
        
        self._attr_attribution = f"Estació {station_name} + Predicció Meteocat"
        
        # Visual name without code, but entity_id will include code
        self._attr_name = station_name
        self._attr_unique_id = f"{entry.entry_id}_weather"
        # Set entity_id explicitly to include station code
        self.entity_id = f"weather.{station_name.lower().replace(' ', '_')}_{station_code.lower()}"
        self._entry = entry
        
        # Set device info to group with sensors
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{station_name} {station_code}",
            "manufacturer": "Meteocat Edició Comunitària",
            "model": "Estació Externa",
        }

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        measurements = self.coordinator.data.get("measurements")
        if not measurements or not isinstance(measurements, list) or not measurements:
            return None
        
        # API returns list of stations, get first one
        station_data = measurements[0]
        variables = station_data.get("variables", [])
        
        # Find temperature measurement (variable code 32)
        for variable in variables:
            if variable.get("codi") == 32:  # Temperature
                lectures = variable.get("lectures", [])
                if lectures:
                    valor = lectures[-1].get("valor")
                    try:
                        return float(valor)
                    except (TypeError, ValueError):
                        return None
        
        return None

    @property
    def humidity(self) -> float | None:
        """Return the current humidity."""
        measurements = self.coordinator.data.get("measurements")
        if not measurements or not isinstance(measurements, list) or not measurements:
            return None
        
        # API returns list of stations, get first one
        station_data = measurements[0]
        variables = station_data.get("variables", [])
        
        # Find humidity measurement (variable code 33)
        for variable in variables:
            if variable.get("codi") == 33:  # Humidity
                lectures = variable.get("lectures", [])
                if lectures:
                    valor = lectures[-1].get("valor")
                    try:
                        return float(valor)
                    except (TypeError, ValueError):
                        return None
        
        return None

    @property
    def native_pressure(self) -> float | None:
        """Return the current pressure."""
        measurements = self.coordinator.data.get("measurements")
        if not measurements or not isinstance(measurements, list) or not measurements:
            return None
        
        # API returns list of stations, get first one
        station_data = measurements[0]
        variables = station_data.get("variables", [])
        
        # Find pressure measurement (variable code 34)
        for variable in variables:
            if variable.get("codi") == 34:  # Pressure
                lectures = variable.get("lectures", [])
                if lectures:
                    valor = lectures[-1].get("valor")
                    try:
                        return float(valor)
                    except (TypeError, ValueError):
                        return None
        
        return None


    @property
    def wind_bearing(self) -> float | None:
        """Return the current wind bearing."""
        measurements = self.coordinator.data.get("measurements")
        if not measurements or not isinstance(measurements, list) or not measurements:
            return None
        
        # API returns list of stations, get first one
        station_data = measurements[0]
        variables = station_data.get("variables", [])
        
        # Find wind direction measurement (variable code 31)
        for variable in variables:
            if variable.get("codi") == 31:  # Wind direction
                lectures = variable.get("lectures", [])
                if lectures:
                    valor = lectures[-1].get("valor")
                    try:
                        return float(valor)
                    except (TypeError, ValueError):
                        return None
        
        return None

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        # For XEMA mode: use measurements
        measurements = self.coordinator.data.get("measurements")
        if measurements and isinstance(measurements, list) and measurements:
            station_data = measurements[0]
            variables = station_data.get("variables", [])
            
            for var in variables:
                # Check for sky state variable (code 35)
                if var.get("codi") == 35:
                    lectures = var.get("lectures", [])
                    if lectures:
                        last_reading = lectures[-1]
                        estat_code = last_reading.get("valor")
                        if estat_code is not None:
                            condition = METEOCAT_CONDITION_MAP.get(estat_code, "cloudy")
                            
                            # Convert sunny to clear-night if sun is below horizon
                            if condition == "sunny" and self._is_night():
                                return "clear-night"
                            
                            return condition
        
        # For MODE_LOCAL: use forecast
        forecast = self.coordinator.data.get("forecast")
        if not forecast:
            return None
        
        # Get first day's data
        dies = forecast.get("dies", [])
        if not dies:
            return None
        
        first_day = dies[0]
        variables = first_day.get("variables", {})
        
        # Get sky state (simple object with valor)
        estat_cel = variables.get("estatCel", {})
        if isinstance(estat_cel, dict):
            estat_code = estat_cel.get("valor")
            if estat_code is not None:
                condition = METEOCAT_CONDITION_MAP.get(estat_code, "cloudy")
                
                # Convert sunny to clear-night if sun is below horizon
                if condition == "sunny" and self._is_night():
                    return "clear-night"
                
                return condition
        
        return None

    def _is_night(self) -> bool:
        """Check if sun is below horizon."""
        station = self.coordinator.data.get("station")
        if not station:
            return False
        
        coords = station.get("coordenades", {})
        latitude = coords.get("latitud")
        longitude = coords.get("longitud")
        
        if not latitude or not longitude:
            return False
        
        # Use Home Assistant's sun helper
        from homeassistant.helpers.sun import get_astral_event_date
        from homeassistant.const import SUN_EVENT_SUNSET, SUN_EVENT_SUNRISE
        
        now = dt_util.now()
        today = now.date()
        
        try:
            sunset = get_astral_event_date(
                self.hass, SUN_EVENT_SUNSET, today
            )
            sunrise = get_astral_event_date(
                self.hass, SUN_EVENT_SUNRISE, today
            )
            
            if sunset and sunrise:
                return now < sunrise or now > sunset
        except Exception as err:
            _LOGGER.warning("Error calculating sun position: %s", err)
        
        return False

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast (72 hours)."""
        forecast_hourly = self.coordinator.data.get("forecast_hourly")
        if not forecast_hourly:
            return None
        
        forecasts: list[Forecast] = []
        
        dies = forecast_hourly.get("dies", [])
        for dia in dies:
            variables = dia.get("variables", {})
            
            # Get hourly variables with their values arrays
            # Try different key names as the API might vary or has been inconsistent in docs/mocks
            temp_data = variables.get("temp", {}) or variables.get("temperatura", {})
            estat_cel_data = variables.get("estatCel", {}) or variables.get("estat", {})
            precip_data = variables.get("precipitacio", {}) or variables.get("precipitació", {})
            
            temp_valors = temp_data.get("valors", temp_data.get("valor", []))
            estat_valors = estat_cel_data.get("valors", estat_cel_data.get("valor", []))
            precip_valors = precip_data.get("valors", precip_data.get("valor", []))
            
            # Build dictionaries by timestamp
            temp_dict = {h.get("data"): h.get("valor") for h in temp_valors}
            estat_dict = {h.get("data"): h.get("valor") for h in estat_valors}
            precip_dict = {h.get("data"): h.get("valor") for h in precip_valors}
            
            # Get all unique timestamps
            all_times = set(temp_dict.keys()) | set(estat_dict.keys()) | set(precip_dict.keys())
            
            for time_str in sorted(all_times):
                if time_str:
                    forecast_item: Forecast = {
                        "datetime": time_str,
                    }
                    
                    if time_str in temp_dict:
                        try:
                            forecast_item["native_temperature"] = float(temp_dict[time_str])
                        except (ValueError, TypeError):
                            pass
                    
                    if time_str in estat_dict:
                        condition = METEOCAT_CONDITION_MAP.get(estat_dict[time_str], "cloudy")
                        forecast_item["condition"] = condition
                    
                    if time_str in precip_dict:
                        try:
                            forecast_item["native_precipitation"] = float(precip_dict[time_str])
                        except (ValueError, TypeError):
                            pass
                    
                    forecasts.append(forecast_item)
        
        return forecasts[:72]  # Limit to 72 hours

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast (8 days)."""
        forecast = self.coordinator.data.get("forecast")
        if not forecast:
            return None
        
        forecasts: list[Forecast] = []
        
        dies = forecast.get("dies", [])[:8]  # Limit to 8 days
        for dia in dies:
            data = dia.get("data")
            if not data:
                continue
            
            variables = dia.get("variables", {})
            
            forecast_item: Forecast = {
                "datetime": data,
            }
            
            # Temperature min/max (simple objects with valor)
            tmin = variables.get("tmin", {})
            if isinstance(tmin, dict):
                valor = tmin.get("valor")
                if valor:
                    try:
                        forecast_item["native_templow"] = float(valor)
                    except (ValueError, TypeError):
                        pass
            
            tmax = variables.get("tmax", {})
            if isinstance(tmax, dict):
                valor = tmax.get("valor")
                if valor:
                    try:
                        forecast_item["native_temperature"] = float(valor)
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
                if valor:
                    try:
                        # Store as percentage (0-100)
                        forecast_item["precipitation_probability"] = float(valor)
                    except (ValueError, TypeError):
                        pass
            
            forecasts.append(forecast_item)
        
        return forecasts


class MeteocatLocalWeather(MeteocatWeather):
    """Representation of a Meteocat weather entity for Local Mode.
    
    Combines local sensor measurements with forecast data:
    - Current conditions: from configured Home Assistant sensors
    - Forecasts: hourly (72h) and daily (8 days) from Forecast API
    """

    @property
    def extra_state_attributes(self) -> dict:
        """Return all configured sensor values as extra state attributes."""
        attrs = {}
        sensors = [
            ("ozone", "ozone"),
            ("pressure", "pressure"),
            ("wind_speed", "wind_speed"),
            ("wind_bearing", "wind_bearing"),
            ("wind_gust", "wind_gust"),
            ("rain", "rain"),
            ("visibility", "visibility"),
            ("uv_index", "uv_index"),
            ("cloud_coverage", "cloud_coverage"),
            ("dew_point", "dew_point"),
            ("apparent_temp", "apparent_temperature"),
        ]
        for sensor_key, attr_name in sensors:
            value = self._get_sensor_value(sensor_key)
            if value is not None:
                attrs[attr_name] = value
        return attrs

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the weather entity."""
        SingleCoordinatorWeatherEntity.__init__(self, coordinator)
        from .const import (
            CONF_ENABLE_FORECAST_DAILY,
            CONF_ENABLE_FORECAST_HOURLY,
        )
        self._attr_supported_features = 0
        
        enable_daily = entry.options.get(CONF_ENABLE_FORECAST_DAILY, entry.data.get(CONF_ENABLE_FORECAST_DAILY, True))
        if enable_daily:
            self._attr_supported_features |= WeatherEntityFeature.FORECAST_DAILY
            
        enable_hourly = entry.options.get(CONF_ENABLE_FORECAST_HOURLY, entry.data.get(CONF_ENABLE_FORECAST_HOURLY, False))
        if enable_hourly:
            self._attr_supported_features |= WeatherEntityFeature.FORECAST_HOURLY
        self._entry = entry
        municipality_name = entry.data.get(CONF_MUNICIPALITY_NAME, "Estació Local")
        self._attr_attribution = f"Estació {municipality_name} + Predicció Meteocat"
        self._attr_name = municipality_name
        self._attr_unique_id = f"{entry.entry_id}_weather_local"
        self.entity_id = f"weather.{self._attr_name.lower().replace(' ', '_')}_local"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": self._attr_name,
            "manufacturer": "Meteocat Edició Comunitària",
            "model": "Estació Local",
        }
        def get_conf(key):
            val = entry.data.get(key)
            if isinstance(val, list):
                return val[0] if val else None
            return val
        self._sensors = {
            "temp": get_conf(CONF_SENSOR_TEMPERATURE),
            "humidity": get_conf(CONF_SENSOR_HUMIDITY),
            "pressure": get_conf(CONF_SENSOR_PRESSURE),
            "wind_speed": get_conf(CONF_SENSOR_WIND_SPEED),
            "wind_bearing": get_conf(CONF_SENSOR_WIND_BEARING),
            "wind_gust": get_conf(CONF_SENSOR_WIND_GUST),
            "visibility": get_conf(CONF_SENSOR_VISIBILITY),
            "uv_index": get_conf(CONF_SENSOR_UV_INDEX),
            "ozone": get_conf(CONF_SENSOR_OZONE),
            "cloud_coverage": get_conf(CONF_SENSOR_CLOUD_COVERAGE),
            "dew_point": get_conf(CONF_SENSOR_DEW_POINT),
            "apparent_temp": get_conf(CONF_SENSOR_APPARENT_TEMPERATURE),
            "rain": get_conf(CONF_SENSOR_RAIN),
        }
        # Read mapping config
        self._mapping_type = entry.data.get("mapping_type", "meteocat")
        if self._mapping_type not in ["meteocat", "custom"]:
            _LOGGER.warning("Invalid mapping_type '%s' found in weather entity, using 'meteocat'", self._mapping_type)
            self._mapping_type = "meteocat"
        self._custom_condition_mapping = entry.data.get("custom_condition_mapping")
        self._local_condition_entity = entry.data.get("local_condition_entity")

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        await super().async_added_to_hass()
        
        # Subscribe to state changes for all configured sensors
        sensors_to_track = [
            entity_id 
            for entity_id in self._sensors.values() 
            if entity_id
        ]
        
        if sensors_to_track:
            from homeassistant.helpers.event import async_track_state_change_event
            
            async def async_sensor_state_listener(event):
                """Handle sensor state changes."""
                self.async_write_ha_state()
                
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, sensors_to_track, async_sensor_state_listener
                )
            )

    def _get_sensor_value(self, sensor_type: str) -> float | None:
        """Get value from a configured sensor."""
        entity_id = self._sensors.get(sensor_type)
        if not entity_id:
            return None
            
        state = self.hass.states.get(entity_id)
        if not state or state.state in ("unknown", "unavailable"):
            return None
            
        try:
            return float(state.state)
        except ValueError:
            return None

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._get_sensor_value("temp")

    @property
    def humidity(self) -> float | None:
        """Return the current humidity."""
        return self._get_sensor_value("humidity")

    @property
    def native_precipitation(self) -> float | None:
        """Return the current precipitation."""
        return self._get_sensor_value("rain")

    @property
    def native_precipitation_unit(self) -> str:
        """Return the precipitation unit."""
        return UnitOfPrecipitationDepth.MILLIMETERS

    @property
    def condition(self) -> str | None:
        """Return the current condition, supporting custom mapping and entity."""
        # 1. If a local condition entity is configured, use its state
        if self._local_condition_entity:
            state = self.hass.states.get(self._local_condition_entity)
            if state and state.state not in ("unknown", "unavailable"):
                raw_value = state.state
                _LOGGER.debug("Local condition entity state: %s", raw_value)
                # Try to convert to int for mapping
                try:
                    estat_code = int(raw_value)
                    _LOGGER.debug("Converted to int: %s", estat_code)
                    # Apply mapping if configured
                    if self._mapping_type == "custom" and self._custom_condition_mapping:
                        mapping = self._custom_condition_mapping
                        _LOGGER.debug("Using custom mapping: %s", mapping)
                        # Custom mapping uses string keys
                        condition = mapping.get(str(estat_code))
                        _LOGGER.debug("Custom mapping lookup for '%s': %s", str(estat_code), condition)
                    else:
                        from .const import METEOCAT_CONDITION_MAP
                        mapping = METEOCAT_CONDITION_MAP
                        _LOGGER.debug("Using default mapping")
                        # Default mapping uses integer keys
                        condition = mapping.get(estat_code)
                        _LOGGER.debug("Default mapping lookup for %s: %s", estat_code, condition)
                    
                    if condition:
                        _LOGGER.debug("Returning mapped condition: %s", condition)
                        if condition == "sunny" and self._is_night():
                            return "clear-night"
                        return condition
                    else:
                        _LOGGER.debug("Condition not found in mapping, returning None")
                        # Return None when mapping fails - better than guessing
                        return None
                except (ValueError, TypeError):
                    _LOGGER.debug("Could not convert to int, checking if raw_value is valid condition")
                    # Not a number, check if it's already a valid condition
                    from homeassistant.components.weather import (
                        ATTR_CONDITION_SUNNY, ATTR_CONDITION_PARTLYCLOUDY, ATTR_CONDITION_CLOUDY,
                        ATTR_CONDITION_RAINY, ATTR_CONDITION_POURING, ATTR_CONDITION_LIGHTNING,
                        ATTR_CONDITION_LIGHTNING_RAINY, ATTR_CONDITION_HAIL, ATTR_CONDITION_SNOWY,
                        ATTR_CONDITION_SNOWY_RAINY, ATTR_CONDITION_FOG, ATTR_CONDITION_WINDY,
                        ATTR_CONDITION_WINDY_VARIANT, ATTR_CONDITION_CLEAR_NIGHT, ATTR_CONDITION_EXCEPTIONAL
                    )
                    valid_conditions = [
                        ATTR_CONDITION_SUNNY, ATTR_CONDITION_PARTLYCLOUDY, ATTR_CONDITION_CLOUDY,
                        ATTR_CONDITION_RAINY, ATTR_CONDITION_POURING, ATTR_CONDITION_LIGHTNING,
                        ATTR_CONDITION_LIGHTNING_RAINY, ATTR_CONDITION_HAIL, ATTR_CONDITION_SNOWY,
                        ATTR_CONDITION_SNOWY_RAINY, ATTR_CONDITION_FOG, ATTR_CONDITION_WINDY,
                        ATTR_CONDITION_WINDY_VARIANT, ATTR_CONDITION_CLEAR_NIGHT, ATTR_CONDITION_EXCEPTIONAL
                    ]
                    if raw_value in valid_conditions:
                        if raw_value == "sunny" and self._is_night():
                            return "clear-night"
                        return raw_value
                    _LOGGER.debug("Raw value is not a valid condition, returning None")
                    return None  # fallback

        # 2. If a rain sensor is present and >0, return rainy
        rain_value = self._get_sensor_value("rain")
        if rain_value is not None and rain_value > 0:
            return "rainy"

        # 3. Use forecast or default logic, but allow custom mapping
        forecast = self.coordinator.data.get("forecast")
        if forecast:
            dies = forecast.get("dies", [])
            if dies:
                variables = dies[0].get("variables", {})
                estat_cel = variables.get("estatCel", {})
                if isinstance(estat_cel, dict):
                    estat_code = estat_cel.get("valor")
                    if estat_code is not None:
                        # Choose mapping
                        if self._mapping_type == "custom" and self._custom_condition_mapping:
                            mapping = self._custom_condition_mapping
                            # Custom mapping uses string keys
                            condition = mapping.get(str(estat_code), "cloudy")
                        else:
                            from .const import METEOCAT_CONDITION_MAP
                            mapping = METEOCAT_CONDITION_MAP
                            # Default mapping uses integer keys
                            condition = mapping.get(estat_code, "cloudy")
                        if condition == "sunny" and self._is_night():
                            return "clear-night"
                        return condition

        # 4. Fallback to super (default) logic
        condition = super().condition
        if condition == "sunny" and self._is_night():
            return "clear-night"
        return condition

    @property
    def native_pressure(self) -> float | None:
        """Return the current pressure."""
        return self._get_sensor_value("pressure")

    @property
    def native_wind_speed(self) -> float | None:
        """Return the current wind speed from the configured sensor (in km/h)."""
        return self._get_sensor_value("wind_speed")

    @property
    def wind_bearing(self) -> float | None:
        """Return the current wind bearing from the configured sensor."""
        return self._get_sensor_value("wind_bearing")


    # Remove ozone property to avoid serialization issues. If ozone is needed, add to extra_state_attributes instead.
        
    @property
    def cloud_coverage(self) -> float | None:
        """Return the current cloud coverage."""
        return self._get_sensor_value("cloud_coverage")
        
    @property
    def native_dew_point(self) -> float | None:
        """Return the current dew point."""
        return self._get_sensor_value("dew_point")
        
    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the current apparent temperature."""
        return self._get_sensor_value("apparent_temp")

    def _is_night(self) -> bool:
        """Check if sun is below horizon."""
        # Use Home Assistant's sun helper (uses HA location)
        from homeassistant.helpers.sun import get_astral_event_date
        from homeassistant.const import SUN_EVENT_SUNSET, SUN_EVENT_SUNRISE
        
        now = dt_util.now()
        today = now.date()
        
        try:
            sunset = get_astral_event_date(
                self.hass, SUN_EVENT_SUNSET, today
            )
            sunrise = get_astral_event_date(
                self.hass, SUN_EVENT_SUNRISE, today
            )
            
            if sunset and sunrise:
                return now < sunrise or now > sunset
        except Exception as err:
            _LOGGER.warning("Error calculating sun position: %s", err)
        
        return False
