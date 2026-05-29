"""Weather entity for Meteocat (Community Edition).

This module provides Weather entities for both modes:
- MODE_EXTERNAL: current station measurements plus Meteocat forecast data
- MODE_LOCAL: local Home Assistant sensor values plus Meteocat forecast data
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
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util
from homeassistant.helpers.event import async_track_sunrise, async_track_sunset

from .const import (
    ATTRIBUTION, 
    METEOCAT_CONDITION_MAP, 
    CONF_ENABLE_FORECAST_DAILY,
    CONF_ENABLE_FORECAST_HOURLY,
    CONF_STATION_NAME, 
    CONF_MUNICIPALITY_NAME,
    DOMAIN,
    CONF_SENSOR_TEMPERATURE,
    CONF_SENSOR_HUMIDITY,
    CONF_SENSOR_PRESSURE,
    CONF_SENSOR_RAIN_INTENSITY,
    CONF_SENSOR_WIND_SPEED,
    CONF_SENSOR_WIND_BEARING,
    CONF_SENSOR_WIND_GUST,
    CONF_SENSOR_VISIBILITY,
    CONF_SENSOR_UV_INDEX,
    CONF_SENSOR_OZONE,
    CONF_SENSOR_CLOUD_COVERAGE,
    CONF_SENSOR_DEW_POINT,
    CONF_SENSOR_APPARENT_TEMPERATURE,
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
        value = self._get_measurement_value(30)
        if value is not None:
             return round(value * 3.6, 1)  # Convert m/s to km/h
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
        
        self._attr_attribution = f"Estació {station_name} (externa) + Predicció Meteocat"
        
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

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await super().async_added_to_hass()
        
        # Track sun events to force update when sun sets/rises
        # This ensures the condition icon changes from sunny to clear-night instantly
        @callback
        def async_sun_event_listener(event):
            """Handle sun events."""
            self.async_write_ha_state()

        self.async_on_remove(async_track_sunrise(self.hass, async_sun_event_listener))
        self.async_on_remove(async_track_sunset(self.hass, async_sun_event_listener))

    def _get_measurement_value(self, code: int) -> float | None:
        """Get measurement value from coordinator data by variable code."""
        measurements = self.coordinator.data.get("measurements")
        if not measurements or not isinstance(measurements, list) or not measurements:
            return None
        
        # API returns list of stations, get first one
        station_data = measurements[0]
        variables = station_data.get("variables", [])
        
        for variable in variables:
            if variable.get("codi") == code:
                lectures = variable.get("lectures", [])
                if lectures:
                    valor = lectures[-1].get("valor")
                    try:
                        return float(valor)
                    except (TypeError, ValueError):
                        return None
        return None

    def _normalize_condition(self, condition: str | None) -> str | None:
        """Normalize the condition for night mode when needed."""
        if condition == "sunny" and self._is_night():
            return "clear-night"
        return condition

    def _map_condition_code(self, estat_code: Any) -> str | None:
        """Map a Meteocat sky state code to a Home Assistant weather condition."""
        return self._normalize_condition(METEOCAT_CONDITION_MAP.get(estat_code))

    def _get_condition_from_daily_forecast(self) -> str | None:
        """Get the current condition from daily forecast data."""
        forecast = self.coordinator.data.get("forecast")
        if not forecast:
            return None

        dies = forecast.get("dies", [])
        if not dies:
            return None

        first_day = dies[0]
        variables = first_day.get("variables", {})

        estat_cel = variables.get("estatCel", {}) or variables.get("estat", {})
        if isinstance(estat_cel, dict):
            estat_code = estat_cel.get("valor", estat_cel.get("codi"))
            if estat_code is not None:
                return self._map_condition_code(estat_code)

        return None

    def _get_condition_from_hourly_forecast(self) -> str | None:
        """Get the current condition from hourly forecast data."""
        forecast_hourly = self.coordinator.data.get("forecast_hourly")
        if not forecast_hourly:
            return None

        current_hour_utc = dt_util.utcnow().replace(minute=0, second=0, microsecond=0)

        dies = forecast_hourly.get("dies", [])
        for dia in dies:
            variables = dia.get("variables", {})
            estat_cel_data = variables.get("estatCel", {}) or variables.get("estat", {})
            estat_valors = estat_cel_data.get("valors", estat_cel_data.get("valor", []))

            if not isinstance(estat_valors, list):
                continue

            for entry in estat_valors:
                if not isinstance(entry, dict):
                    continue

                data_str = entry.get("data")
                if not data_str:
                    continue

                try:
                    entry_dt = dt_util.parse_datetime(data_str)
                    if not entry_dt:
                        continue
                except (TypeError, ValueError):
                    continue

                entry_dt_utc = dt_util.as_utc(entry_dt)
                if entry_dt_utc.replace(minute=0, second=0, microsecond=0) != current_hour_utc:
                    continue

                estat_code = entry.get("valor", entry.get("codi"))
                if estat_code is not None:
                    return self._map_condition_code(estat_code)

        return None

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._get_measurement_value(32)

    @property
    def humidity(self) -> float | None:
        """Return the current humidity."""
        return self._get_measurement_value(33)

    @property
    def native_pressure(self) -> float | None:
        """Return the current pressure."""
        return self._get_measurement_value(34)

    @property
    def wind_bearing(self) -> float | None:
        """Return the current wind bearing."""
        return self._get_measurement_value(31)

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        # XEMA measurements do not typically contain sky condition (symbol).
        # Variable 35 is precipitation, not sky state.
        # Use hourly forecast when configured, because it can change every hour.
        enable_hourly = self._entry.options.get(
            CONF_ENABLE_FORECAST_HOURLY,
            self._entry.data.get(CONF_ENABLE_FORECAST_HOURLY, False),
        )
        if enable_hourly:
            condition = self._get_condition_from_hourly_forecast()
            if condition is not None:
                return condition

        # Only fall back to daily forecast if daily data is configured.
        enable_daily = self._entry.options.get(
            CONF_ENABLE_FORECAST_DAILY,
            self._entry.data.get(CONF_ENABLE_FORECAST_DAILY, True),
        )
        if enable_daily:
            return self._get_condition_from_daily_forecast()

        return None

    def _is_night(self) -> bool:
        """Check if sun is below horizon using station coordinates if available."""
        # 1. Attempt to get station coordinates (Lat/Lon)
        lat = None
        lon = None
        
        # Try getting from ConfigEntry (Best source for fixed metadata)
        # Municipality flow saves: municipality_lat
        lat = self._entry.data.get("municipality_lat")
        lon = self._entry.data.get("municipality_lon")
        
        # If not found, check Station coordinates (External Mode)
        # Coordinator caches station data in: _station_data (hidden key) in entry
        if lat is None:
            station_data = self._entry.data.get("_station_data")
            if station_data:
                coords = station_data.get("coordenades", {})
                lat = coords.get("latitud")
                lon = coords.get("longitud")

        # If still not found, check live coordinator data (fallback)
        if lat is None and self.coordinator.data:
            # Check known keys used in coordinator
            for key in ["station", "station_metadata"]:
                station_data = self.coordinator.data.get(key)
                if station_data:
                    coords = station_data.get("coordenades", {})
                    lat = coords.get("latitud")
                    lon = coords.get("longitud")
                    if lat is not None:
                        break

        # 2. If we have coordinates, use Astral to calculate sun state
        if lat is not None and lon is not None:
            try:
                from astral import LocationInfo
                from astral.sun import sun
                
                # Use HA timezone context
                tz = dt_util.DEFAULT_TIME_ZONE
                
                # Create observer location
                loc = LocationInfo(
                    name="Meteocat Station",
                    region="Catalonia", 
                    timezone=str(tz),
                    latitude=lat,
                    longitude=lon
                )
                
                now = dt_util.now()
                
                # Calculate sun events for today
                s = sun(loc.observer, date=now.date(), tzinfo=tz)
                sunrise = s["sunrise"]
                sunset = s["sunset"]
                
                return now < sunrise or now > sunset
            except (ImportError, Exception):
                # Fallback on any calculation error
                pass

        # 3. Fallback to HA global location (Original logic)
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
                        condition = METEOCAT_CONDITION_MAP.get(estat_dict[time_str])
                        if condition:
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
            # Log keys for debugging forecast issues
            if _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug(
                    "Daily forecast for %s - Variable keys: %s", 
                    data, 
                    list(variables.keys())
                )
            
            forecast_item: Forecast = {
                "datetime": data,
            }
            
            # Temperature min/max (simple objects with valor)
            tmin = variables.get("tmin", {})
            if isinstance(tmin, dict):
                valor = tmin.get("valor")
                if valor is not None:
                    try:
                        forecast_item["native_templow"] = float(valor)
                    except (ValueError, TypeError):
                        pass
                else:
                    _LOGGER.debug("Daily forecast: tmin valor is None for day %s", data)
            
            tmax = variables.get("tmax", {})
            if isinstance(tmax, dict):
                valor = tmax.get("valor")
                if valor is not None:
                    try:
                        forecast_item["native_temperature"] = float(valor)
                    except (ValueError, TypeError):
                        pass
                else:
                    _LOGGER.debug("Daily forecast: tmax valor is None for day %s", data)
            
            # Condition (simple object with valor)
            estat_cel = variables.get("estatCel", {})
            if isinstance(estat_cel, dict):
                estat_code = estat_cel.get("valor")
                if estat_code is not None:
                    condition = METEOCAT_CONDITION_MAP.get(estat_code)
                    if condition:
                        forecast_item["condition"] = condition
            
            # Precipitation (simple object with valor, percentage)
            precip = variables.get("precipitacio", {})
            if isinstance(precip, dict):
                valor = precip.get("valor")
                if valor is not None:
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
            ("rain_intensity", "rain_intensity"),
            ("wind_speed", "wind_speed"),
            ("wind_bearing", "wind_bearing"),
            ("wind_gust", "wind_gust"),
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
        self._attr_attribution = f"Estació {municipality_name} (local) + Predicció Meteocat"
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
            "rain_intensity": get_conf(CONF_SENSOR_RAIN_INTENSITY),
            "wind_speed": get_conf(CONF_SENSOR_WIND_SPEED),
            "wind_bearing": get_conf(CONF_SENSOR_WIND_BEARING),
            "wind_gust": get_conf(CONF_SENSOR_WIND_GUST),
            "visibility": get_conf(CONF_SENSOR_VISIBILITY),
            "uv_index": get_conf(CONF_SENSOR_UV_INDEX),
            "ozone": get_conf(CONF_SENSOR_OZONE),
            "cloud_coverage": get_conf(CONF_SENSOR_CLOUD_COVERAGE),
            "dew_point": get_conf(CONF_SENSOR_DEW_POINT),
            "apparent_temp": get_conf(CONF_SENSOR_APPARENT_TEMPERATURE),
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

        if self._local_condition_entity and self._local_condition_entity not in sensors_to_track:
            sensors_to_track.append(self._local_condition_entity)
        
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

    def _resolve_mapped_condition(self, raw_value: str) -> str | None:
        """Resolve a condition from the configured local condition entity."""
        try:
            estat_code = int(raw_value)
            if self._mapping_type == "custom" and self._custom_condition_mapping:
                return self._custom_condition_mapping.get(str(estat_code))
            return METEOCAT_CONDITION_MAP.get(estat_code)
        except (TypeError, ValueError):
            pass

        valid_conditions = {
            "clear-night",
            "sunny",
            "partlycloudy",
            "cloudy",
            "rainy",
            "pouring",
            "lightning",
            "lightning-rainy",
            "hail",
            "snowy",
            "snowy-rainy",
            "fog",
            "windy",
            "windy-variant",
            "exceptional",
        }
        if raw_value in valid_conditions:
            return raw_value
        return None

    def _get_base_local_condition(self) -> str | None:
        """Return the condition coming from the configured local condition entity."""
        if not self._local_condition_entity:
            return None

        state = self.hass.states.get(self._local_condition_entity)
        if not state or state.state in ("unknown", "unavailable"):
            return None

        return self._resolve_mapped_condition(state.state)

    def _get_calculated_condition_override(self) -> str | None:
        """Return a calculated local condition override when required sensors are available."""
        rain_intensity = self._get_sensor_value("rain_intensity")
        wind_gust = self._get_sensor_value("wind_gust")
        humidity = self._get_sensor_value("humidity")
        temperature = self._get_sensor_value("temp")
        dew_point = self._get_sensor_value("dew_point")

        if rain_intensity is not None:
            if rain_intensity >= 50:
                return "lightning-rainy"
            if rain_intensity >= 10:
                return "pouring"
            if rain_intensity >= 1:
                return "rainy"

        if rain_intensity == 0 and wind_gust is not None and wind_gust > 20:
            return "windy"

        if (
            rain_intensity == 0
            and humidity is not None
            and humidity >= 95
            and temperature is not None
            and dew_point is not None
            and abs(temperature - dew_point) < 1
        ):
            return "fog"

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
    def native_precipitation_unit(self) -> str:
        """Return the precipitation unit."""
        return UnitOfPrecipitationDepth.MILLIMETERS

    @property
    def native_precipitation(self) -> float | None:
        """Return the current rain intensity from the configured local sensor."""
        return self._get_sensor_value("rain_intensity")

    @property
    def condition(self) -> str | None:
        """Return the current condition for local mode."""
        condition = self._get_calculated_condition_override()
        if condition is None:
            condition = self._get_base_local_condition()
        if condition is None:
            condition = self._get_condition_from_hourly_forecast()
        if condition is None:
            condition = self._get_condition_from_daily_forecast()
        if condition is None:
            condition = super().condition
        return self._normalize_condition(condition)

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
