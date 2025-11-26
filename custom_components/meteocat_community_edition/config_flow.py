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
    DEFAULT_API_BASE_URL,
    DEFAULT_UPDATE_TIME_1,
    DEFAULT_UPDATE_TIME_2,
    DOMAIN,
    MODE_MUNICIPI,
    MODE_MUNICIPI_LABEL,
    MODE_ESTACIO,
    MODE_ESTACIO_LABEL,
)

_LOGGER = logging.getLogger(__name__)


def is_valid_time_format(time_str: str) -> bool:
    """Validate time format HH:MM."""
    import re
    time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
    return bool(time_pattern.match(time_str)) if time_str else False


def validate_update_times(time1: str, time2: str) -> dict[str, str]:
    """Validate update times format and uniqueness."""
    import re
    
    errors = {}
    time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
    
    if not time1 or not time1.strip():
        errors["update_time_1"] = "required"
    elif not time_pattern.match(time1):
        errors["update_time_1"] = "invalid_time_format"
    
    if not time2 or not time2.strip():
        errors["update_time_2"] = "required"
    elif not time_pattern.match(time2):
        errors["update_time_2"] = "invalid_time_format"
    
    # Only check if they're equal if both are valid
    if not errors and time1 == time2:
        errors["update_time_2"] = "times_must_differ"
    
    return errors


class MeteocatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Meteocat (Community Edition)."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.api_key: str | None = None
        self.mode: str | None = None
        self.comarca_code: str | None = None
        self.comarca_name: str | None = None
        self.station_code: str | None = None
        self.station_name: str | None = None
        self.municipality_code: str | None = None
        self.municipality_name: str | None = None
        self.api_base_url: str = DEFAULT_API_BASE_URL
        self.update_time_1: str = DEFAULT_UPDATE_TIME_1
        self.update_time_2: str = DEFAULT_UPDATE_TIME_2
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
            # Get endpoint URL (default to production if not provided or empty)
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
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(
                        CONF_API_BASE_URL,
                        default=DEFAULT_API_BASE_URL,
                        description={"suggested_value": DEFAULT_API_BASE_URL}
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

        return self.async_show_form(
            step_id="mode",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODE, default=MODE_ESTACIO): vol.In({
                        MODE_ESTACIO: MODE_ESTACIO_LABEL,
                        MODE_MUNICIPI: MODE_MUNICIPI_LABEL,
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
                
                if self.mode == MODE_ESTACIO:
                    # Fetch stations for selected comarca
                    self._stations = await api.get_stations_by_comarca(self.comarca_code)
                    
                    if not self._stations:
                        errors["base"] = "no_stations"
                    else:
                        return await self.async_step_station()
                else:
                    # Fetch municipalities for selected comarca
                    all_municipalities = await api.get_municipalities()
                    self._municipalities = [
                        muni for muni in all_municipalities
                        if muni.get("comarca", {}).get("codi") == self.comarca_code
                    ]
                    
                    if not self._municipalities:
                        errors["base"] = "no_municipalities"
                    else:
                        return await self.async_step_municipality()
                    
            except MeteocatAPIError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
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
            
            # Find station name
            _LOGGER.debug("Looking for station with code: %s", self.station_code)
            _LOGGER.debug("Available stations: %s", [s.get("codi") for s in self._stations])
            for station in self._stations:
                if station.get("codi") == self.station_code:
                    self.station_name = station.get("nom")
                    _LOGGER.debug("Found station name: %s", self.station_name)
                    break
            
            if not self.station_name:
                _LOGGER.warning("Station name not found for code %s, using default", self.station_code)
                self.station_name = f"Station {self.station_code}"
            
            # Check if station already configured
            await self.async_set_unique_id(self.station_code)
            self._abort_if_unique_id_configured()

            # Set title placeholders for area assignment screen
            self.context["title_placeholders"] = {"name": f"{self.station_name} {self.station_code}"}

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
            
            # Find municipality name
            for municipality in self._municipalities:
                if municipality.get("codi") == self.municipality_code:
                    self.municipality_name = municipality.get("nom")
                    break
            
            # Check if municipality already configured
            await self.async_set_unique_id(f"municipal_{self.municipality_code}")
            self._abort_if_unique_id_configured()

            # Set title placeholders for area assignment screen
            self.context["title_placeholders"] = {"name": self.municipality_name}

            # Go to update times configuration
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
            
            # Validate times
            time_errors = validate_update_times(time1, time2)
            errors.update(time_errors)
            
            if not errors:
                self.update_time_1 = time1
                self.update_time_2 = time2
                
                # Create the config entry based on mode
                if self.mode == MODE_ESTACIO:
                    _LOGGER.info("Creating entry with title: %s %s", self.station_name, self.station_code)
                    return self.async_create_entry(
                        title=f"{self.station_name} {self.station_code}",
                        data={
                            CONF_API_KEY: self.api_key,
                            CONF_MODE: MODE_ESTACIO,
                            CONF_STATION_CODE: self.station_code,
                            CONF_STATION_NAME: self.station_name,
                            CONF_COMARCA_CODE: self.comarca_code,
                            CONF_COMARCA_NAME: self.comarca_name,
                            CONF_UPDATE_TIME_1: self.update_time_1,
                            CONF_UPDATE_TIME_2: self.update_time_2,
                        },
                        options={
                            CONF_API_BASE_URL: self.api_base_url,
                        },
                    )
                else:  # MODE_MUNICIPI
                    return self.async_create_entry(
                        title=self.municipality_name,
                        data={
                            CONF_API_KEY: self.api_key,
                            CONF_MODE: MODE_MUNICIPI,
                            CONF_MUNICIPALITY_CODE: self.municipality_code,
                            CONF_MUNICIPALITY_NAME: self.municipality_name,
                            CONF_COMARCA_CODE: self.comarca_code,
                            CONF_COMARCA_NAME: self.comarca_name,
                            CONF_UPDATE_TIME_1: self.update_time_1,
                            CONF_UPDATE_TIME_2: self.update_time_2,
                        },
                        options={
                            CONF_API_BASE_URL: self.api_base_url,
                        },
                    )

        return self.async_show_form(
            step_id="update_times",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_TIME_1,
                        default=DEFAULT_UPDATE_TIME_1
                    ): str,
                    vol.Required(
                        CONF_UPDATE_TIME_2,
                        default=DEFAULT_UPDATE_TIME_2
                    ): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> MeteocatOptionsFlow:
        """Get the options flow for this handler."""
        return MeteocatOptionsFlow(config_entry)


class MeteocatOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Meteocat (Community Edition)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Validate update times if they're being changed
            time1 = user_input.get(CONF_UPDATE_TIME_1, "").strip()
            time2 = user_input.get(CONF_UPDATE_TIME_2, "").strip()
            
            time_errors = validate_update_times(time1, time2)
            errors.update(time_errors)
            
            if not errors:
                # Update both options and data
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={**self.config_entry.data, CONF_UPDATE_TIME_1: time1, CONF_UPDATE_TIME_2: time2},
                    options=user_input,
                )
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_API_BASE_URL,
                        default=self.config_entry.options.get(
                            CONF_API_BASE_URL, DEFAULT_API_BASE_URL
                        ),
                    ): str,
                    vol.Required(
                        CONF_UPDATE_TIME_1,
                        default=self.config_entry.data.get(
                            CONF_UPDATE_TIME_1, DEFAULT_UPDATE_TIME_1
                        ),
                    ): str,
                    vol.Required(
                        CONF_UPDATE_TIME_2,
                        default=self.config_entry.data.get(
                            CONF_UPDATE_TIME_2, DEFAULT_UPDATE_TIME_2
                        ),
                    ): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> FlowResult:
        """Handle re-authentication when API key is invalid or expired."""
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
                api_base_url = self.config_entry.data.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL)
                api = MeteocatAPI(new_api_key, session, api_base_url)
                
                # Test the new API key
                await api.get_comarques()
                
                # Update the config entry with new API key
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={**self.config_entry.data, CONF_API_KEY: new_api_key}
                )
                
                # Reload the config entry to apply new credentials
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                
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
