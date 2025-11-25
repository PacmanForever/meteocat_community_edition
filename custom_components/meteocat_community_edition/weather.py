"""Weather entity for Meteocat (Community Edition)."""
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

from .const import ATTRIBUTION, CONDITION_MAP, CONF_STATION_NAME, DOMAIN
from .coordinator import MeteocatCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteocat weather entity."""
    from .const import CONF_MODE, MODE_ESTACIO
    
    # Only create weather entity in XEMA mode
    mode = entry.data.get(CONF_MODE, MODE_ESTACIO)
    _LOGGER.info("Weather platform setup - mode: %s", mode)
    
    if mode != MODE_ESTACIO:
        _LOGGER.debug("Skipping weather entity creation - mode is %s", mode)
        return
    
    coordinator: MeteocatCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    _LOGGER.info("Creating weather entity for station: %s", entry.data.get(CONF_STATION_NAME))
    async_add_entities([MeteocatWeather(coordinator, entry)])


class MeteocatWeather(SingleCoordinatorWeatherEntity[MeteocatCoordinator]):
    """Representation of a Meteocat weather entity."""

    _attr_attribution = ATTRIBUTION
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
        
        from .const import CONF_STATION_CODE
        station_code = entry.data.get(CONF_STATION_CODE, "")
        station_name = entry.data[CONF_STATION_NAME]
        
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
            "model": "Estació XEMA",
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
                    return lectures[-1].get("valor")
        
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
                    return lectures[-1].get("valor")
        
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
                    return lectures[-1].get("valor")
        
        return None

    @property
    def native_wind_speed(self) -> float | None:
        """Return the current wind speed."""
        measurements = self.coordinator.data.get("measurements")
        if not measurements or not isinstance(measurements, list) or not measurements:
            return None
        
        # API returns list of stations, get first one
        station_data = measurements[0]
        variables = station_data.get("variables", [])
        
        # Find wind speed measurement (variable code 30)
        for variable in variables:
            if variable.get("codi") == 30:  # Wind speed
                lectures = variable.get("lectures", [])
                if lectures:
                    return lectures[-1].get("valor")
        
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
                    return lectures[-1].get("valor")
        
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
                # Check for sky state variable (code 32)
                if var.get("codi") == 32:
                    lectures = var.get("lectures", [])
                    if lectures:
                        last_reading = lectures[-1]
                        estat_code = last_reading.get("valor")
                        if estat_code is not None:
                            condition = CONDITION_MAP.get(estat_code, "cloudy")
                            
                            # Convert sunny to clear-night if sun is below horizon
                            if condition == "sunny" and self._is_night():
                                return "clear-night"
                            
                            return condition
        
        # For MODE_MUNICIPI: use forecast
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
                condition = CONDITION_MAP.get(estat_code, "cloudy")
                
                # Convert sunny to clear-night if sun is below horizon
                if condition == "sunny" and self._is_night():
                    return "clear-night"
                
                return condition
        
        return None

    @property
    def uv_index(self) -> float | None:
        """Return the UV index."""
        uv_data = self.coordinator.data.get("uv_index")
        if not uv_data:
            return None
        
        # Get current or next UV index value
        dies = uv_data.get("dies", [])
        if not dies:
            return None
        
        now = dt_util.now()
        for dia in dies:
            uvi = dia.get("uvi", [])
            for hora in uvi:
                if not isinstance(hora, dict):
                    continue
                    
                hora_data = hora.get("data")
                if hora_data:
                    hora_dt = dt_util.parse_datetime(hora_data)
                    if hora_dt and hora_dt >= now:
                        return hora.get("valor")
        
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
                self.hass, SUN_EVENT_SUNSET, today, latitude, longitude
            )
            sunrise = get_astral_event_date(
                self.hass, SUN_EVENT_SUNRISE, today, latitude, longitude
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
                    forecast_item: Forecast = {
                        "datetime": time_str,
                    }
                    
                    if time_str in temp_dict:
                        try:
                            forecast_item["temperature"] = float(temp_dict[time_str])
                        except (ValueError, TypeError):
                            pass
                    
                    if time_str in estat_dict:
                        condition = CONDITION_MAP.get(estat_dict[time_str], "cloudy")
                        forecast_item["condition"] = condition
                    
                    if time_str in precip_dict:
                        try:
                            forecast_item["precipitation"] = float(precip_dict[time_str])
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
                        forecast_item["templow"] = float(valor)
                    except (ValueError, TypeError):
                        pass
            
            tmax = variables.get("tmax", {})
            if isinstance(tmax, dict):
                valor = tmax.get("valor")
                if valor:
                    try:
                        forecast_item["temperature"] = float(valor)
                    except (ValueError, TypeError):
                        pass
            
            # Condition (simple object with valor)
            estat_cel = variables.get("estatCel", {})
            if isinstance(estat_cel, dict):
                estat_code = estat_cel.get("valor")
                if estat_code is not None:
                    condition = CONDITION_MAP.get(estat_code, "cloudy")
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

