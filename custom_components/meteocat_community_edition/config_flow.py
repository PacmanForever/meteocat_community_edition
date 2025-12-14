"""Config flow for Meteocat (Community Edition) integration."""
from __future__ import annotations

from collections import OrderedDict
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MeteocatAPI, MeteocatAPIError
from .const import (
    CONF_API_BASE_URL,
    CONF_API_KEY,
    CONF_COMARCA_CODE,
    CONF_COMARCA_NAME,
    CONF_MODE,
    CONF_MUNICIPALITY_CODE,
    CONF_MUNICIPALITY_NAME,
    CONF_STATION_CODE,
    CONF_STATION_NAME,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    CONF_UPDATE_TIME_3,
    CONF_ENABLE_FORECAST_DAILY,
    CONF_ENABLE_FORECAST_HOURLY,
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
    DEFAULT_API_BASE_URL,
    DEFAULT_UPDATE_TIME_1,
    DEFAULT_UPDATE_TIME_2,
    DOMAIN,
    MODE_LOCAL,
    MODE_LOCAL_LABEL,
    MODE_EXTERNAL,
    MODE_EXTERNAL_LABEL,
)

_LOGGER = logging.getLogger(__name__)


def is_valid_time_format(time_str: str) -> bool:
    """Validate time format HH:MM."""
    import re
    time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
    return bool(time_pattern.match(time_str)) if time_str else False


def validate_update_times(time1: str, time2: str, time3: str) -> dict[str, str]:
    """Validate update times format and uniqueness."""
    import re
    
    errors = {}
    time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
    
    if not time1 or not time1.strip():
        errors["update_time_1"] = "required"
    elif not time_pattern.match(time1):
        errors["update_time_1"] = "invalid_time_format"
    
    if time2 and time2.strip():
        if not time_pattern.match(time2):
            errors["update_time_2"] = "invalid_time_format"
    
    if time3 and time3.strip():
        if not time_pattern.match(time3):
            errors["update_time_3"] = "invalid_time_format"
    
    # Check for duplicates if times are valid
    times = []
    if not errors.get("update_time_1"):
        times.append(time1)
    if time2 and time2.strip() and not errors.get("update_time_2"):
        times.append(time2)
    if time3 and time3.strip() and not errors.get("update_time_3"):
        times.append(time3)
    
    if len(times) != len(set(times)):
        errors["base"] = "times_must_differ"
    
    return errors




class MeteocatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Meteocat (Community Edition)."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        super().__init__()
        self.api_key: str | None = None
        self.mode: str | None = None
        self.comarca_code: str | None = None
        self.comarca_name: str | None = None
        self.station_code: str | None = None
        self.station_name: str | None = None
        self.entry: config_entries.ConfigEntry | None = None
        self._comarques: list[dict[str, Any]] = []
        self.api_base_url: str = DEFAULT_API_BASE_URL

    async def async_step_condition_mapping_type(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step 1: Select mapping type only."""
        import voluptuous as vol
        errors = {}
        if user_input is not None:
            mapping_type = user_input.get("mapping_type")
            if not mapping_type:
                errors["mapping_type"] = "required"
            elif mapping_type not in ["meteocat", "custom"]:
                errors["mapping_type"] = "value_not_allowed"
            elif mapping_type == "meteocat":
                latest_input = getattr(self, '_local_sensors_input', None) or getattr(self, '_update_times_input', {})
                entry_data = dict(latest_input)
                entry_data["mapping_type"] = "meteocat"
                entry_data[CONF_MODE] = self.mode  # Add the selected mode
                # Add municipality and comarca data for sensors
                if hasattr(self, 'municipality_code') and self.municipality_code:
                    entry_data[CONF_MUNICIPALITY_CODE] = self.municipality_code
                if hasattr(self, 'municipality_name'):
                    entry_data[CONF_MUNICIPALITY_NAME] = self.municipality_name
                if hasattr(self, 'comarca_code') and self.comarca_code:
                    entry_data[CONF_COMARCA_CODE] = self.comarca_code
                if hasattr(self, 'comarca_name'):
                    entry_data[CONF_COMARCA_NAME] = self.comarca_name
                # Add API key and base URL
                entry_data[CONF_API_KEY] = self.api_key
                entry_data[CONF_API_BASE_URL] = self.api_base_url
                if hasattr(self, 'municipality_lat') and self.municipality_lat is not None:
                    entry_data["municipality_lat"] = self.municipality_lat
                if hasattr(self, 'municipality_lon') and self.municipality_lon is not None:
                    entry_data["municipality_lon"] = self.municipality_lon
                if hasattr(self, 'provincia_code') and self.provincia_code:
                    entry_data["provincia_code"] = self.provincia_code
                if hasattr(self, 'provincia_name') and self.provincia_name:
                    entry_data["provincia_name"] = self.provincia_name
                return self.async_create_entry(
                    title=self.municipality_name,
                    data=entry_data,
                    options={CONF_API_BASE_URL: self.api_base_url},
                )
            elif mapping_type == "custom":
                return await self.async_step_condition_mapping_custom()

        from homeassistant.helpers import selector
        schema = vol.Schema({
            vol.Required(
                "mapping_type",
                default="meteocat",
                description={"suggested_value": "mapping_type_label"}
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": "meteocat", "label": "Meteocat"},
                        {"value": "custom", "label": "Personalitzat"}
                    ]
                )
            ),
        })
        return self.async_show_form(
            step_id="condition_mapping_type",
            data_schema=schema,
            errors=errors,
            description_placeholders={"description": "mapping_description"},
        )

    async def async_step_condition_mapping_custom(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step 2: Custom mapping config (entity + mapping)."""
        from homeassistant.helpers import selector
        import voluptuous as vol
        errors = {}
        example_mapping = self.hass.data.get(DOMAIN, {}).get("mapping_example", "0: clear-night\n1: sunny\n2: partlycloudy\n3: cloudy\n4: rainy\n5: pouring\n6: lightning\n7: lightning-rainy\n8: snowy\n9: snowy-rainy\n10: fog\n11: hail\n12: windy\n13: windy-variant\n14: exceptional")
        if user_input is not None:
            local_entity = user_input.get("local_condition_entity")
            custom_mapping = user_input.get("custom_condition_mapping")
            if not local_entity or local_entity == "":
                errors["local_condition_entity"] = "required"
            if not custom_mapping or custom_mapping == "":
                errors["custom_condition_mapping"] = "required"
            if not errors:
                # Parse the mapping
                try:
                    parsed_mapping = self._parse_condition_mapping(custom_mapping)
                except ValueError as e:
                    if "Invalid condition" in str(e):
                        errors["custom_condition_mapping"] = "invalid_condition"
                    else:
                        errors["custom_condition_mapping"] = "invalid_format"
                else:
                    latest_input = getattr(self, '_local_sensors_input', None) or getattr(self, '_update_times_input', {})
                    entry_data = dict(latest_input)
                    entry_data["mapping_type"] = "custom"
                    entry_data["custom_condition_mapping"] = parsed_mapping
                    entry_data["local_condition_entity"] = local_entity
                    entry_data[CONF_MODE] = self.mode  # Add the selected mode
                    # Add municipality and comarca data for sensors
                    if hasattr(self, 'municipality_code') and self.municipality_code:
                        entry_data[CONF_MUNICIPALITY_CODE] = self.municipality_code
                    if hasattr(self, 'municipality_name'):
                        entry_data[CONF_MUNICIPALITY_NAME] = self.municipality_name
                    if hasattr(self, 'comarca_code') and self.comarca_code:
                        entry_data[CONF_COMARCA_CODE] = self.comarca_code
                    if hasattr(self, 'comarca_name'):
                        entry_data[CONF_COMARCA_NAME] = self.comarca_name
                    # Add API key and base URL
                    entry_data[CONF_API_KEY] = self.api_key
                    entry_data[CONF_API_BASE_URL] = self.api_base_url
                    if hasattr(self, 'municipality_lat') and self.municipality_lat is not None:
                        entry_data["municipality_lat"] = self.municipality_lat
                    if hasattr(self, 'municipality_lon') and self.municipality_lon is not None:
                        entry_data["municipality_lon"] = self.municipality_lon
                    if hasattr(self, 'provincia_code') and self.provincia_code:
                        entry_data["provincia_code"] = self.provincia_code
                    if hasattr(self, 'provincia_name') and self.provincia_name:
                        entry_data["provincia_name"] = self.provincia_name
                    return self.async_create_entry(
                        title=self.municipality_name,
                        data=entry_data,
                        options={CONF_API_BASE_URL: self.api_base_url},
                    )

        schema = vol.Schema({
            vol.Required(
                "local_condition_entity"
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", multiple=False)
            ),
            vol.Required(
                "custom_condition_mapping",
                default=example_mapping
            ): selector.ObjectSelector(),
        })
        return self.async_show_form(
            step_id="condition_mapping_custom",
            data_schema=schema,
            errors=errors,
            description_placeholders={"description": "mapping_description"},
        )

    def _parse_condition_mapping(self, text: str) -> dict[str, str]:
        """Parse condition mapping from text format: key: value"""
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
        
        lines = text.strip().split('\n')
        mapping = {}
        for line in lines:
            line = line.strip()
            if not line or not ':' in line:
                continue
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if key and value:
                if value not in valid_conditions:
                    raise ValueError(f"Invalid condition '{value}'. Must be one of: {', '.join(valid_conditions)}")
                mapping[key] = value
        if not mapping:
            raise ValueError("Empty mapping")
        return mapping

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> FlowResult:
        """Handle re-authentication when API key is invalid or expired."""
        self.entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle re-authentication confirmation."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            new_api_key = user_input[CONF_API_KEY].strip()
            
            # Validate new API key
            try:
                session = async_get_clientsession(self.hass)
                # Use existing base URL or default
                api_base_url = DEFAULT_API_BASE_URL
                if self.entry:
                    api_base_url = self.entry.data.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL)
                
                api = MeteocatAPI(new_api_key, session, api_base_url)
                
                # Test the new API key
                await api.get_comarques()
                
                # Update the config entry with new API key
                if self.entry:
                    self.hass.config_entries.async_update_entry(
                        entry=self.entry,
                        data={**self.entry.data, CONF_API_KEY: new_api_key}
                    )
                    
                    # Reload the config entry to apply new credentials
                    await self.hass.config_entries.async_reload(self.entry.entry_id)
                
                return self.async_abort(reason="reauth_successful")
                
            except MeteocatAPIError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during reauth")
                errors["base"] = "unknown"
        
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
            }),
            description_placeholders={
                "error_info": "Your API key has expired or is invalid. Please enter a new valid API key."
            },
            errors=errors,
        )
        self.municipality_code: str | None = None
        self.municipality_name: str | None = None
        self.api_base_url: str = DEFAULT_API_BASE_URL
        self.update_time_1: str = DEFAULT_UPDATE_TIME_1
        self.update_time_2: str = DEFAULT_UPDATE_TIME_2
        self.update_time_3: str = ""
        self.enable_forecast_daily: bool = True
        self.enable_forecast_hourly: bool = False
        self._comarques: list[dict[str, Any]] = []
        self._stations: list[dict[str, Any]] = []
        self._municipalities: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - ask for API key and optionally endpoint."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.api_key = user_input[CONF_API_KEY]
            # Get endpoint URL (default to production if not provided or empty, or from existing entry)
            endpoint_url = user_input.get(CONF_API_BASE_URL, "").strip()
            self.api_base_url = endpoint_url if endpoint_url else DEFAULT_API_BASE_URL
            
            # Strip whitespace from API key (common user error)
            self.api_key = self.api_key.strip()
            
            # Validate API key by trying to fetch comarques
            try:
                session = async_get_clientsession(self.hass)
                api = MeteocatAPI(self.api_key, session, self.api_base_url)
                self._comarques = await api.get_comarques()
                
                if not self._comarques:
                    errors["base"] = "no_comarques"
                else:
                    return await self.async_step_mode()
                    
            except MeteocatAPIError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_KEY,
                        default=self.entry.data.get(CONF_API_KEY, "") if self.entry else ""
                    ): str,
                } | {
                    vol.Optional(
                        CONF_API_BASE_URL,
                        default=self.entry.data.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL) if self.entry else DEFAULT_API_BASE_URL,
                        description={"suggested_value": self.entry.data.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL) if self.entry else DEFAULT_API_BASE_URL}
                    ): str,
                }
            ),
            errors=errors,
        )

    async def async_step_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the mode selection step - XEMA station or municipal forecasts."""
        if user_input is not None:
            self.mode = user_input[CONF_MODE]
            return await self.async_step_comarca()

        external_label = MODE_EXTERNAL_LABEL
        local_label = MODE_LOCAL_LABEL

        return self.async_show_form(
            step_id="mode",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODE, default=MODE_EXTERNAL): vol.In({
                        MODE_EXTERNAL: external_label,
                        MODE_LOCAL: local_label,
                    }),
                }
            ),
        )

    async def async_step_comarca(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the comarca selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.comarca_code = user_input[CONF_COMARCA_CODE]
            
            # Find comarca name
            for comarca in self._comarques:
                if comarca.get("codi") == self.comarca_code:
                    self.comarca_name = comarca.get("nom")
                    break
            
            # Decide next step based on mode
            try:
                session = async_get_clientsession(self.hass)
                api = MeteocatAPI(self.api_key, session, self.api_base_url)
                
                if self.mode == MODE_EXTERNAL:
                    # Fetch stations for selected comarca
                    _LOGGER.debug("Fetching stations for comarca: %s", self.comarca_code)
                    self._stations = await api.get_stations_by_comarca(self.comarca_code)
                    
                    if not self._stations:
                        _LOGGER.warning("No stations found for comarca: %s", self.comarca_code)
                        errors["base"] = "no_stations"
                    else:
                        _LOGGER.debug("Found %d stations for comarca: %s", len(self._stations), self.comarca_code)
                        return await self.async_step_station()
                else:
                    # Fetch municipalities for selected comarca
                    _LOGGER.debug("Fetching municipalities for comarca: %s", self.comarca_code)
                    all_municipalities = await api.get_municipalities()
                    self._municipalities = [
                        muni for muni in all_municipalities
                        if muni.get("comarca", {}).get("codi") == self.comarca_code
                    ]
                    
                    if not self._municipalities:
                        _LOGGER.warning("No municipalities found for comarca: %s", self.comarca_code)
                        errors["base"] = "no_municipalities"
                    else:
                        _LOGGER.debug("Found %d municipalities for comarca: %s", len(self._municipalities), self.comarca_code)
                        return await self.async_step_municipality()
                    
            except MeteocatAPIError as err:
                _LOGGER.error("API error while fetching data for comarca %s: %s", self.comarca_code, err)
                errors["base"] = "cannot_connect"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error while fetching data for comarca %s: %s", self.comarca_code, err)
                errors["base"] = "unknown"
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Create comarca options
        comarca_options = OrderedDict(
            (comarca.get("codi"), comarca.get("nom"))
            for comarca in sorted(self._comarques, key=lambda x: x.get("nom", "").lower())
        )

        return self.async_show_form(
            step_id="comarca",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_COMARCA_CODE): vol.In(comarca_options),
                }
            ),
            errors=errors,
        )

    async def async_step_station(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the station selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.station_code = user_input[CONF_STATION_CODE]
            
            # Find station name and extract all relevant data
            _LOGGER.debug("Looking for station with code: %s", self.station_code)
            _LOGGER.debug("Available stations: %s", [s.get("codi") for s in self._stations])
            for station in self._stations:
                if station.get("codi") == self.station_code:
                    self.station_name = station.get("nom")
                    _LOGGER.debug("Found station name: %s", self.station_name)
                    # Save complete station data for coordinate sensors
                    # This prevents API calls when quota is exhausted
                    self.station_data = station
                    # Extract municipality if available
                    # Saved to entry.data to avoid API calls during runtime
                    municipi = station.get("municipi", {})
                    if isinstance(municipi, dict):
                        self.station_municipality_code = municipi.get("codi")
                        self.station_municipality_name = municipi.get("nom")
                    # Extract province if available (might be in comarca or municipi)
                    # Saved to entry.data to avoid API calls during runtime
                    provincia = station.get("provincia", {})
                    if isinstance(provincia, dict):
                        self.station_provincia_code = provincia.get("codi")
                        self.station_provincia_name = provincia.get("nom")
                    break
            
            if not self.station_name:
                _LOGGER.warning("Station name not found for code %s, using default", self.station_code)
                self.station_name = f"Station {self.station_code}"
            
            # Check if station already configured
            await self.async_set_unique_id(self.station_code)
            self._abort_if_unique_id_configured()

            # Set title placeholders for area assignment screen
            try:
                self.context.update({"title_placeholders": {"name": f"{self.station_name} {self.station_code}"}})
            except TypeError:
                # Context is immutable in some cases (like tests), skip setting placeholders
                pass

            # Go to update times configuration
            return await self.async_step_update_times()

        # Create station options
        station_options = OrderedDict(
            (station.get("codi"), station.get("nom"))
            for station in sorted(self._stations, key=lambda x: x.get("nom", "").lower())
        )

        return self.async_show_form(
            step_id="station",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STATION_CODE): vol.In(station_options),
                }
            ),
            errors=errors,
        )

    async def async_step_municipality(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the municipality selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.municipality_code = user_input[CONF_MUNICIPALITY_CODE]
            _LOGGER.debug("Selected municipality code: %s", self.municipality_code)
            
            # Find municipality and extract all relevant data
            for municipality in self._municipalities:
                if municipality.get("codi") == self.municipality_code:
                    self.municipality_name = municipality.get("nom")
                    _LOGGER.debug("Found municipality name: %s", self.municipality_name)
                    # Extract coordinates if available
                    # Saved to entry.data to avoid API calls during runtime
                    coordenades = municipality.get("coordenades", {})
                    self.municipality_lat = coordenades.get("latitud")
                    self.municipality_lon = coordenades.get("longitud")
                    # Extract province if available
                    # Saved to entry.data to avoid API calls during runtime
                    provincia = municipality.get("provincia", {})
                    self.provincia_code = provincia.get("codi")
                    self.provincia_name = provincia.get("nom")
                    
                    # Fallback: if province not found in municipality, try to get it from comarca
                    if not self.provincia_name and self._comarques:
                        _LOGGER.debug("Province not found in municipality, checking comarca %s", self.comarca_code)
                        for comarca in self._comarques:
                            if comarca.get("codi") == self.comarca_code:
                                provincia = comarca.get("provincia", {})
                                if provincia:
                                    self.provincia_code = provincia.get("codi")
                                    self.provincia_name = provincia.get("nom")
                                    _LOGGER.debug("Found province in comarca: %s", self.provincia_name)
                                break
                    break
            
            # Check if municipality already configured
            unique_id = f"municipal_{self.municipality_code}"
            _LOGGER.debug("Setting unique_id: %s", unique_id)
            await self.async_set_unique_id(unique_id)
            _LOGGER.debug("Checking if unique_id is already configured")
            self._abort_if_unique_id_configured()

            # Go to update times configuration (don't update context here to avoid flow issues)
            return await self.async_step_update_times()

        # Create municipality options
        municipality_options = OrderedDict(
            (muni.get("codi"), muni.get("nom"))
            for muni in sorted(self._municipalities, key=lambda x: x.get("nom", "").lower())
        )

        return self.async_show_form(
            step_id="municipality",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MUNICIPALITY_CODE): vol.In(municipality_options),
                }
            ),
            errors=errors,
        )

    async def async_step_update_times(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the update times configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            time1 = user_input.get(CONF_UPDATE_TIME_1, "").strip()
            time2 = user_input.get(CONF_UPDATE_TIME_2, "").strip()
            time3 = user_input.get(CONF_UPDATE_TIME_3, "").strip()
            enable_daily = user_input.get(CONF_ENABLE_FORECAST_DAILY, True)
            enable_hourly = user_input.get(CONF_ENABLE_FORECAST_HOURLY, False)
            
            # Validate times
            time_errors = validate_update_times(time1, time2, time3)
            errors.update(time_errors)
            
            # Validate forecast selection (only for local mode)
            if self.mode == MODE_LOCAL and not enable_daily and not enable_hourly:
                errors["base"] = "must_select_one_forecast"
            
            if not errors:
                self.update_time_1 = time1
                self.update_time_2 = time2
                self.update_time_3 = time3
                self.enable_forecast_daily = enable_daily
                self.enable_forecast_hourly = enable_hourly
                
                # Create the config entry based on mode
                # All metadata saved here to avoid runtime API calls
                if self.mode == MODE_EXTERNAL:
                    _LOGGER.info("Creating entry with title: %s %s", self.station_name, self.station_code)
                    entry_data = {
                        CONF_MODE: MODE_EXTERNAL,  # Add mode for external station
                        CONF_API_KEY: self.api_key,
                        CONF_MODE: MODE_EXTERNAL,
                        CONF_STATION_CODE: self.station_code,
                        CONF_STATION_NAME: self.station_name,
                        CONF_COMARCA_CODE: self.comarca_code,
                        CONF_COMARCA_NAME: self.comarca_name,
                        CONF_UPDATE_TIME_1: self.update_time_1,
                        CONF_UPDATE_TIME_2: self.update_time_2,
                        CONF_UPDATE_TIME_3: self.update_time_3,
                        CONF_ENABLE_FORECAST_DAILY: self.enable_forecast_daily,
                        CONF_ENABLE_FORECAST_HOURLY: self.enable_forecast_hourly,
                    }
                    # Save station data for coordinate sensors (prevents API calls when quota exhausted)
                    if hasattr(self, 'station_data') and self.station_data:
                        entry_data["_station_data"] = self.station_data
                    # Add municipality if available
                    if hasattr(self, 'station_municipality_code') and self.station_municipality_code:
                        entry_data["station_municipality_code"] = self.station_municipality_code
                    if hasattr(self, 'station_municipality_name') and self.station_municipality_name:
                        entry_data["station_municipality_name"] = self.station_municipality_name
                    # Add province if available
                    if hasattr(self, 'station_provincia_code') and self.station_provincia_code:
                        entry_data["station_provincia_code"] = self.station_provincia_code
                    if hasattr(self, 'station_provincia_name') and self.station_provincia_name:
                        entry_data["station_provincia_name"] = self.station_provincia_name
                    
                    return self.async_create_entry(
                        title=f"{self.station_name} {self.station_code}",
                        data=entry_data,
                        options={
                            CONF_API_BASE_URL: self.api_base_url,
                        },
                    )
                else:  # MODE_LOCAL
                    return await self.async_step_local_sensors()

        return self.async_show_form(
            step_id="update_times",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_UPDATE_TIME_1, default=DEFAULT_UPDATE_TIME_1): str,
                    vol.Optional(CONF_UPDATE_TIME_2, default=DEFAULT_UPDATE_TIME_2): str,
                    vol.Optional(CONF_UPDATE_TIME_3): str,
                    vol.Required(CONF_ENABLE_FORECAST_DAILY, default=True): bool,
                    vol.Required(CONF_ENABLE_FORECAST_HOURLY, default=False): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_local_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Pantalla de selecció de sensors locals. Després, mapping."""
        from homeassistant.helpers import selector
        import voluptuous as vol
        
        errors = {}
        
        if user_input is not None:
            # Validate required fields
            temp_sensor = user_input.get(CONF_SENSOR_TEMPERATURE)
            hum_sensor = user_input.get(CONF_SENSOR_HUMIDITY)
            
            if not temp_sensor or temp_sensor == "":
                errors[CONF_SENSOR_TEMPERATURE] = "required"
            if not hum_sensor or hum_sensor == "":
                errors[CONF_SENSOR_HUMIDITY] = "required"
                
            if not errors:
                # Desa els sensors locals seleccionats per passar-los a la pantalla de mapping
                self._local_sensors_input = user_input
                return await self.async_step_condition_mapping_type()

        return self.async_show_form(
            step_id="local_sensors",
            data_schema=vol.Schema({
                vol.Required(CONF_SENSOR_TEMPERATURE): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
                ),
                vol.Required(CONF_SENSOR_HUMIDITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="humidity")
                ),
                vol.Optional(CONF_SENSOR_PRESSURE): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class=["pressure", "atmospheric_pressure"])
                ),
                vol.Optional(CONF_SENSOR_WIND_SPEED): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="wind_speed")
                ),
                vol.Optional(CONF_SENSOR_WIND_BEARING): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Optional(CONF_SENSOR_WIND_GUST): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="wind_speed")
                ),
                vol.Optional(CONF_SENSOR_RAIN): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Optional(CONF_SENSOR_VISIBILITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Optional(CONF_SENSOR_UV_INDEX): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Optional(CONF_SENSOR_OZONE): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Optional(CONF_SENSOR_CLOUD_COVERAGE): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Optional(CONF_SENSOR_DEW_POINT): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
                ),
                vol.Optional(CONF_SENSOR_APPARENT_TEMPERATURE): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
                ),
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return MeteocatOptionsFlow(config_entry)


class MeteocatOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Meteocat (Community Edition)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry
        super().__init__()

    @property
    def config_entry(self):
        """Return the config entry."""
        return self._config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Validate update times if they're being changed
            time1 = user_input.get(CONF_UPDATE_TIME_1, "").strip()
            time2 = user_input.get(CONF_UPDATE_TIME_2, "").strip()
            time3 = user_input.get(CONF_UPDATE_TIME_3, "").strip()
            enable_daily = user_input.get(CONF_ENABLE_FORECAST_DAILY, True)
            enable_hourly = user_input.get(CONF_ENABLE_FORECAST_HOURLY, False)
            
            time_errors = validate_update_times(time1, time2, time3)
            errors.update(time_errors)
            
            # Validate forecast selection (only for local mode)
            mode = self.config_entry.data.get(CONF_MODE)
            if mode == MODE_LOCAL and not enable_daily and not enable_hourly:
                errors["base"] = "must_select_one_forecast"
            
            if not errors:
                # Ensure API key is preserved in data (migration from old entries where it might be in options)
                api_key = self.config_entry.data.get(CONF_API_KEY) or self.config_entry.options.get(CONF_API_KEY)
                
                # Validate that API key exists
                if not api_key:
                    errors["base"] = "invalid_auth"
                else:
                    # Update both options and data
                    # Using kwargs for forward compatibility with future HA versions
                    self.hass.config_entries.async_update_entry(
                        entry=self.config_entry,
                        data={
                            **self.config_entry.data, 
                            CONF_API_KEY: api_key,
                        },
                        options={
                            **self.config_entry.options,
                            CONF_API_KEY: api_key,  # Also store in options for safety
                            CONF_UPDATE_TIME_1: time1, 
                            CONF_UPDATE_TIME_2: time2,
                            CONF_UPDATE_TIME_3: time3,
                            CONF_ENABLE_FORECAST_DAILY: enable_daily,
                            CONF_ENABLE_FORECAST_HOURLY: enable_hourly,
                        },
                    )
                    
                    if mode == MODE_LOCAL:
                        return await self.async_step_sensors()
                    else:
                        return self.async_create_entry(title="", data={})

        # Prepare description placeholders
        description_placeholders = {}
        mode = self.config_entry.data.get(CONF_MODE)
        description_placeholders["measurements_info"] = ""

        # Ensure options is not None
        options = self.config_entry.options or {}

        # Build schema
        schema_dict = {
            vol.Required(
                CONF_UPDATE_TIME_1,
                default=self.config_entry.data.get(
                    CONF_UPDATE_TIME_1, DEFAULT_UPDATE_TIME_1
                ),
            ): str,
            vol.Optional(
                CONF_UPDATE_TIME_2,
                default=self.config_entry.data.get(
                    CONF_UPDATE_TIME_2, DEFAULT_UPDATE_TIME_2
                ),
            ): str,
            vol.Optional(
                CONF_UPDATE_TIME_3,
                default=self.config_entry.data.get(
                    CONF_UPDATE_TIME_3
                ) or vol.UNDEFINED,
            ): str,
            vol.Required(
                CONF_ENABLE_FORECAST_DAILY,
                default=self.config_entry.data.get(
                    CONF_ENABLE_FORECAST_DAILY, True
                ),
            ): bool,
            vol.Required(
                CONF_ENABLE_FORECAST_HOURLY,
                default=self.config_entry.data.get(
                    CONF_ENABLE_FORECAST_HOURLY, False
                ),
            ): bool,
        }

        # Add mapping type selector for local mode
        if mode == MODE_LOCAL:
            pass  # Mapping type moved to separate step

        # Prepare title placeholders
        title_placeholders = {}
        if mode == MODE_LOCAL:
            title_placeholders["name"] = "estació local"
        else:
            station_name = self.config_entry.data.get(CONF_STATION_NAME, "")
            station_code = self.config_entry.data.get(CONF_STATION_CODE, "")
            if station_name and station_code:
                title_placeholders["name"] = f"{station_name} {station_code}"
            else:
                title_placeholders["name"] = station_name or station_code or ""

        # Set title placeholders in context for the flow (if context is mutable)
        try:
            self.context["title_placeholders"] = title_placeholders
        except (TypeError, AttributeError):
            # Context is immutable in some cases (like tests), skip setting placeholders
            pass

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
            description_placeholders=description_placeholders,
            errors=errors,
        )

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the sensors options."""
        from homeassistant.helpers import selector
        import voluptuous as vol
        
        errors = {}
        
        # Get current values
        data = self.config_entry.data
        
        if user_input is not None:
            # Validate required fields
            temp_sensor = user_input.get(CONF_SENSOR_TEMPERATURE)
            hum_sensor = user_input.get(CONF_SENSOR_HUMIDITY)
            
            if not temp_sensor or temp_sensor == "":
                errors[CONF_SENSOR_TEMPERATURE] = "required"
            if not hum_sensor or hum_sensor == "":
                errors[CONF_SENSOR_HUMIDITY] = "required"
                
            if not errors:
                # Helper to ensure we store strings, not lists
                def get_entity_id(key):
                    val = user_input.get(key)
                    if isinstance(val, list):
                        return val[0] if val else None
                    return val

                # Ensure API key is preserved in data
                api_key = self.config_entry.data.get(CONF_API_KEY) or self.config_entry.options.get(CONF_API_KEY)

                # Update entry with sensors
                self.hass.config_entries.async_update_entry(
                    entry=self.config_entry,
                    data={
                        **self.config_entry.data,
                        CONF_API_KEY: api_key,
                        CONF_SENSOR_TEMPERATURE: get_entity_id(CONF_SENSOR_TEMPERATURE),
                        CONF_SENSOR_HUMIDITY: get_entity_id(CONF_SENSOR_HUMIDITY),
                        CONF_SENSOR_PRESSURE: get_entity_id(CONF_SENSOR_PRESSURE),
                        CONF_SENSOR_WIND_SPEED: get_entity_id(CONF_SENSOR_WIND_SPEED),
                        CONF_SENSOR_WIND_BEARING: get_entity_id(CONF_SENSOR_WIND_BEARING),
                        CONF_SENSOR_WIND_GUST: get_entity_id(CONF_SENSOR_WIND_GUST),
                        CONF_SENSOR_VISIBILITY: get_entity_id(CONF_SENSOR_VISIBILITY),
                        CONF_SENSOR_UV_INDEX: get_entity_id(CONF_SENSOR_UV_INDEX),
                        CONF_SENSOR_OZONE: get_entity_id(CONF_SENSOR_OZONE),
                        CONF_SENSOR_CLOUD_COVERAGE: get_entity_id(CONF_SENSOR_CLOUD_COVERAGE),
                        CONF_SENSOR_DEW_POINT: get_entity_id(CONF_SENSOR_DEW_POINT),
                        CONF_SENSOR_APPARENT_TEMPERATURE: get_entity_id(CONF_SENSOR_APPARENT_TEMPERATURE),
                        CONF_SENSOR_RAIN: get_entity_id(CONF_SENSOR_RAIN),
                    }
                )
                return await self.async_step_condition_mapping_type()

        return self.async_show_form(
            step_id="sensors",
            data_schema=vol.Schema({
                vol.Required(CONF_SENSOR_TEMPERATURE, description={"suggested_value": data.get(CONF_SENSOR_TEMPERATURE)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="temperature", multiple=False)
                ),
                vol.Required(CONF_SENSOR_HUMIDITY, description={"suggested_value": data.get(CONF_SENSOR_HUMIDITY)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="humidity", multiple=False)
                ),
                vol.Optional(CONF_SENSOR_PRESSURE, description={"suggested_value": data.get(CONF_SENSOR_PRESSURE)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class=["pressure", "atmospheric_pressure"], multiple=False)
                ),
                vol.Optional(CONF_SENSOR_WIND_SPEED, description={"suggested_value": data.get(CONF_SENSOR_WIND_SPEED)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="wind_speed", multiple=False)
                ),
                vol.Optional(CONF_SENSOR_WIND_BEARING, description={"suggested_value": data.get(CONF_SENSOR_WIND_BEARING)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", multiple=False)
                ),
                vol.Optional(CONF_SENSOR_WIND_GUST, description={"suggested_value": data.get(CONF_SENSOR_WIND_GUST)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="wind_speed", multiple=False)
                ),
                vol.Optional(CONF_SENSOR_VISIBILITY, description={"suggested_value": data.get(CONF_SENSOR_VISIBILITY)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", multiple=False)
                ),
                vol.Optional(CONF_SENSOR_UV_INDEX, description={"suggested_value": data.get(CONF_SENSOR_UV_INDEX)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", multiple=False)
                ),
                vol.Optional(CONF_SENSOR_OZONE, description={"suggested_value": data.get(CONF_SENSOR_OZONE)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", multiple=False)
                ),
                vol.Optional(CONF_SENSOR_CLOUD_COVERAGE, description={"suggested_value": data.get(CONF_SENSOR_CLOUD_COVERAGE)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", multiple=False)
                ),
                vol.Optional(CONF_SENSOR_DEW_POINT, description={"suggested_value": data.get(CONF_SENSOR_DEW_POINT)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", multiple=False)
                ),
                vol.Optional(CONF_SENSOR_APPARENT_TEMPERATURE, description={"suggested_value": data.get(CONF_SENSOR_APPARENT_TEMPERATURE)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", multiple=False)
                ),
                vol.Optional(CONF_SENSOR_RAIN, description={"suggested_value": data.get(CONF_SENSOR_RAIN)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", multiple=False)
                ),
            }),
            errors=errors,
        )

    async def async_step_condition_mapping_type(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step: Select mapping type for options flow."""
        from homeassistant.helpers import selector
        import voluptuous as vol
        errors = {}
        
        if user_input is not None:
            mapping_type = user_input.get("mapping_type", "meteocat")
            if mapping_type not in ["meteocat", "custom"]:
                errors["mapping_type"] = "value_not_allowed"
            elif mapping_type == "meteocat":
                # Update entry data with mapping type
                updated_data = dict(self.config_entry.data)
                updated_data["mapping_type"] = "meteocat"
                # Remove custom mapping fields if they exist
                updated_data.pop("custom_condition_mapping", None)
                updated_data.pop("local_condition_entity", None)
                
                self.hass.config_entries.async_update_entry(
                    entry=self.config_entry,
                    data=updated_data
                )
                
                # If sensors are already configured (local mode), close the flow
                # Otherwise, go to sensors configuration
                mode = self.config_entry.data.get(CONF_MODE)
                if mode == MODE_LOCAL and CONF_SENSOR_TEMPERATURE in self.config_entry.data:
                    return self.async_create_entry(title="", data={})
                else:
                    return await self.async_step_sensors()
                
            elif mapping_type == "custom":
                # Ensure API key is preserved in data before going to custom mapping
                api_key = self.config_entry.data.get(CONF_API_KEY) or self.config_entry.options.get(CONF_API_KEY)
                
                # Update entry data with API key preserved
                updated_data = dict(self.config_entry.data)
                updated_data[CONF_API_KEY] = api_key
                
                self.hass.config_entries.async_update_entry(
                    entry=self.config_entry,
                    data=updated_data
                )
                return await self.async_step_condition_mapping_custom()

        # Get current mapping type from entry data
        current_mapping_type = self.config_entry.data.get("mapping_type", "meteocat")
        
        schema = vol.Schema({
            vol.Required(
                "mapping_type",
                default=current_mapping_type
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": "meteocat", "label": "Meteocat"},
                        {"value": "custom", "label": "Personalitzat"}
                    ]
                )
            ),
        })
        return self.async_show_form(
            step_id="condition_mapping_type",
            data_schema=schema,
            errors=errors,
            description_placeholders={"description": "mapping_description"},
        )

    async def async_step_condition_mapping_custom(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step: Custom mapping config for options flow."""
        from homeassistant.helpers import selector
        import voluptuous as vol
        errors = {}
        
        # Get current custom mapping data
        current_entity = self.config_entry.data.get("local_condition_entity", "")
        current_mapping = self.config_entry.data.get("custom_condition_mapping", {})
        
        # Convert mapping dict back to string format for display
        current_mapping_str = ""
        if current_mapping:
            current_mapping_str = "\n".join([f"{k}: {v}" for k, v in current_mapping.items()])
        
        example_mapping = self.hass.data.get(DOMAIN, {}).get("mapping_example", "0: clear-night\n1: sunny\n2: partlycloudy\n3: cloudy\n4: rainy\n5: pouring\n6: lightning\n7: lightning-rainy\n8: snowy\n9: snowy-rainy\n10: fog\n11: hail\n12: windy\n13: windy-variant\n14: exceptional")
        
        if user_input is not None:
            # Validate required fields
            local_entity = user_input.get("local_condition_entity")
            custom_mapping = user_input.get("custom_condition_mapping")
            
            if not local_entity or local_entity == "":
                errors["local_condition_entity"] = "required"
            if not custom_mapping or custom_mapping == "":
                errors["custom_condition_mapping"] = "required"
                
            if not errors:
                # Parse the mapping
                try:
                    parsed_mapping = self._parse_condition_mapping(custom_mapping)
                except ValueError as e:
                    if "Invalid condition" in str(e):
                        errors["custom_condition_mapping"] = "invalid_condition"
                    else:
                        errors["custom_condition_mapping"] = "invalid_format"
                else:
                    # Ensure API key is preserved in data
                    api_key = self.config_entry.data.get(CONF_API_KEY) or self.config_entry.options.get(CONF_API_KEY)
                    
                    # Update entry data with custom mapping
                    updated_data = dict(self.config_entry.data)
                    updated_data[CONF_API_KEY] = api_key
                    updated_data["mapping_type"] = "custom"
                    updated_data["custom_condition_mapping"] = parsed_mapping
                    updated_data["local_condition_entity"] = local_entity
                    
                    self.hass.config_entries.async_update_entry(
                        entry=self.config_entry,
                        data=updated_data
                    )
                    
                    return self.async_create_entry(title="", data={})

        schema = vol.Schema({
            vol.Required(
                "local_condition_entity",
                description={"suggested_value": current_entity}
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", multiple=False)
            ),
            vol.Required(
                "custom_condition_mapping",
                description={"suggested_value": current_mapping_str or example_mapping}
            ): selector.ObjectSelector(),
        })
        return self.async_show_form(
            step_id="condition_mapping_custom",
            data_schema=schema,
            errors=errors,
            description_placeholders={"description": "custom_mapping_description"},
        )

    def _parse_condition_mapping(self, text: str) -> dict[str, str]:
        """Parse condition mapping from text format: key: value"""
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
        
        lines = text.strip().split('\n')
        mapping = {}
        for line in lines:
            line = line.strip()
            if not line or not ':' in line:
                continue
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if key and value:
                if value not in valid_conditions:
                    raise ValueError(f"Invalid condition '{value}'. Must be one of: {', '.join(valid_conditions)}")
                mapping[key] = value
        if not mapping:
            raise ValueError("Empty mapping")
        return mapping
