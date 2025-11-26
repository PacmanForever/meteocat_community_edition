"""Data coordinator for Meteocat (Community Edition)."""
from __future__ import annotations

import asyncio
from datetime import datetime, time, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import MeteocatAPI, MeteocatAPIError, MeteocatAuthError
from .const import (
    CONF_API_BASE_URL,
    CONF_API_KEY,
    CONF_MODE,
    CONF_MUNICIPALITY_CODE,
    CONF_STATION_CODE,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    DEFAULT_API_BASE_URL,
    DEFAULT_UPDATE_TIME_1,
    DEFAULT_UPDATE_TIME_2,
    DOMAIN,
    EVENT_ATTR_MODE,
    EVENT_ATTR_MUNICIPALITY_CODE,
    EVENT_ATTR_NEXT_UPDATE,
    EVENT_ATTR_PREVIOUS_UPDATE,
    EVENT_ATTR_STATION_CODE,
    EVENT_ATTR_TIMESTAMP,
    EVENT_DATA_UPDATED,
    EVENT_NEXT_UPDATE_CHANGED,
    MODE_ESTACIO,
    MODE_MUNICIPI,
)

_LOGGER = logging.getLogger(__name__)


class MeteocatCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Meteocat data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.mode = entry.data.get(CONF_MODE, MODE_ESTACIO)  # Default to ESTACIO for backwards compatibility
        self.station_code = entry.data.get(CONF_STATION_CODE)
        self.municipality_code = entry.data.get(CONF_MUNICIPALITY_CODE)
        
        # Get update times from config or use defaults
        self.update_time_1 = entry.data.get(CONF_UPDATE_TIME_1, DEFAULT_UPDATE_TIME_1)
        self.update_time_2 = entry.data.get(CONF_UPDATE_TIME_2, DEFAULT_UPDATE_TIME_2)
        
        # Get API base URL from options or use default
        api_base_url = entry.options.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL)
        
        # Debug: Log API key (first/last 4 chars only for security)
        api_key = entry.data[CONF_API_KEY]
        if api_key:
            _LOGGER.debug(
                "Initializing coordinator with API key: %s...%s (length: %d)",
                api_key[:4] if len(api_key) > 4 else "***",
                api_key[-4:] if len(api_key) > 4 else "***",
                len(api_key)
            )
        else:
            _LOGGER.error("API key is empty or None!")
        
        session = async_get_clientsession(hass)
        self.api = MeteocatAPI(
            api_key,
            session,
            api_base_url,
        )
        
        self.station_data: dict[str, Any] = {}
        self.last_successful_update_time: datetime | None = None
        self._previous_next_update: datetime | None = None
        self._scheduled_update_remover = None
        
        # For XEMA mode, municipality code will be found from station
        # For MUNICIPAL mode, municipality code is already set
        if self.mode == MODE_MUNICIPI and not self.municipality_code:
            _LOGGER.error("Municipal mode requires municipality_code!")
        
        # IMPORTANT: Set update_interval to None to disable automatic polling
        # Updates will only happen:
        # 1. On first setup (async_config_entry_first_refresh)
        # 2. Manual button press (async_request_refresh)
        # 3. Scheduled updates (via async_track_time_interval)
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.station_code}",
            update_interval=None,  # Disable automatic polling to save API quota
        )

    def _schedule_next_update(self) -> None:
        """Schedule the next automatic update at the configured time."""
        # Cancel any existing scheduled update
        if self._scheduled_update_remover:
            self._scheduled_update_remover()
            self._scheduled_update_remover = None
        
        # Calculate next update time
        now = dt_util.now()
        today = now.date()
        
        update_datetimes = [
            dt_util.as_local(
                datetime.combine(today, time.fromisoformat(update_time))
            )
            for update_time in [self.update_time_1, self.update_time_2]
        ]
        
        # Find the next update time
        next_update = None
        for update_dt in update_datetimes:
            if update_dt > now:
                next_update = update_dt
                break
        
        # If no update today, use first update tomorrow
        if next_update is None:
            tomorrow = today + timedelta(days=1)
            next_update = dt_util.as_local(
                datetime.combine(tomorrow, time.fromisoformat(self.update_time_1))
            )
        
        # Schedule the update at the exact time
        self._scheduled_update_remover = async_track_point_in_utc_time(
            self.hass,
            self._async_scheduled_update,
            dt_util.as_utc(next_update),
        )
        
        _LOGGER.info(
            "Scheduled next automatic update at %s (in %s)",
            next_update,
            next_update - now,
        )

    @callback
    async def _async_scheduled_update(self, now: datetime) -> None:
        """Handle scheduled update."""
        _LOGGER.info("Running scheduled update at %s", now)
        await self.async_request_refresh()
        
        # Reschedule for the next update time
        self._schedule_next_update()

    async def async_shutdown(self) -> None:
        """Clean up when shutting down."""
        if self._scheduled_update_remover:
            self._scheduled_update_remover()
            self._scheduled_update_remover = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Meteocat API."""
        
        # Capture timestamp at the START of the update (when button is pressed)
        self.last_successful_update_time = dt_util.utcnow()
        
        try:
            # Build tasks based on mode (NOTE: quotes fetched AFTER other API calls)
            tasks = {}
            
            # ESTACIO mode: fetch station measurements and find municipality
            if self.mode == MODE_ESTACIO and self.station_code:
                tasks["measurements"] = self.api.get_station_measurements(self.station_code)
                
                # Get station info and municipality code on first run
                if not self.station_data:
                    stations = await self.api.get_stations()
                    for station in stations:
                        if station.get("codi") == self.station_code:
                            self.station_data = station
                            break
                    
                    if self.station_data:
                        self.municipality_code = await self.api.find_municipality_for_station(
                            self.station_data
                        )
            
            # Add forecast tasks if we have a municipality code (both modes)
            if self.municipality_code:
                tasks["forecast"] = self.api.get_municipal_forecast(
                    self.municipality_code
                )
                tasks["forecast_hourly"] = self.api.get_hourly_forecast(
                    self.municipality_code
                )
                tasks["uv_index"] = self.api.get_uv_index(self.municipality_code)
            
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            
            # Process results
            data: dict[str, Any] = {
                "station": self.station_data,
                "municipality_code": self.municipality_code,
            }
            
            for key, result in zip(tasks.keys(), results):
                if isinstance(result, Exception):
                    _LOGGER.warning("Error fetching %s: %s", key, result)
                    data[key] = None
                else:
                    data[key] = result
            
            # Fetch quotes AFTER all other API calls to get accurate consumption
            try:
                data["quotes"] = await self.api.get_quotes()
            except Exception as err:
                _LOGGER.warning("Error fetching quotes: %s", err)
                data["quotes"] = None
            
            # Calculate next scheduled update time
            now = dt_util.now()
            today = now.date()
            
            update_datetimes = [
                dt_util.as_local(
                    datetime.combine(today, time.fromisoformat(update_time))
                )
                for update_time in [self.update_time_1, self.update_time_2]
            ]
            
            # Find the next update time
            current_next_update = None
            for update_dt in update_datetimes:
                if update_dt > now:
                    current_next_update = update_dt
                    break
            
            # If no update today, use first update tomorrow
            if current_next_update is None:
                tomorrow = today + timedelta(days=1)
                current_next_update = dt_util.as_local(
                    datetime.combine(tomorrow, time.fromisoformat(self.update_time_1))
                )
            
            # Fire event if next update time changed
            if current_next_update != self._previous_next_update:
                next_update_event_data = {
                    EVENT_ATTR_MODE: self.mode,
                    EVENT_ATTR_TIMESTAMP: dt_util.now().isoformat(),
                    EVENT_ATTR_NEXT_UPDATE: current_next_update.isoformat() if current_next_update else None,
                    EVENT_ATTR_PREVIOUS_UPDATE: self._previous_next_update.isoformat() if self._previous_next_update else None,
                }
                
                # Add station code if in ESTACIO mode
                if self.mode == MODE_ESTACIO and self.station_code:
                    next_update_event_data[EVENT_ATTR_STATION_CODE] = self.station_code
                
                # Add municipality code if available
                if self.municipality_code:
                    next_update_event_data[EVENT_ATTR_MUNICIPALITY_CODE] = self.municipality_code
                
                # Add device_id for device triggers
                device_registry = dr.async_get(self.hass)
                device = device_registry.async_get_device(
                    identifiers={(DOMAIN, self.entry.entry_id)}
                )
                if device:
                    next_update_event_data["device_id"] = device.id
                
                self.hass.bus.fire(EVENT_NEXT_UPDATE_CHANGED, next_update_event_data)
                _LOGGER.debug("Fired event %s with data: %s", EVENT_NEXT_UPDATE_CHANGED, next_update_event_data)
                
                # Update previous value
                self._previous_next_update = current_next_update
            
            # Fire event to notify about data update
            event_data = {
                EVENT_ATTR_MODE: self.mode,
                EVENT_ATTR_TIMESTAMP: dt_util.now().isoformat(),
            }
            
            # Add station code if in ESTACIO mode
            if self.mode == MODE_ESTACIO and self.station_code:
                event_data[EVENT_ATTR_STATION_CODE] = self.station_code
            
            # Add municipality code if available
            if self.municipality_code:
                event_data[EVENT_ATTR_MUNICIPALITY_CODE] = self.municipality_code
            
            # Add device_id for device triggers
            device_registry = dr.async_get(self.hass)
            device = device_registry.async_get_device(
                identifiers={(DOMAIN, self.entry.entry_id)}
            )
            if device:
                event_data["device_id"] = device.id
            
            self.hass.bus.fire(EVENT_DATA_UPDATED, event_data)
            _LOGGER.debug("Fired event %s with data: %s", EVENT_DATA_UPDATED, event_data)
            
            return data
        
        except MeteocatAuthError as err:
            # Authentication errors should trigger re-authentication flow
            _LOGGER.error(
                "Authentication failed: %s. Please reconfigure the integration with a valid API key.", 
                err
            )
            raise ConfigEntryAuthFailed(
                f"Authentication failed: {err}. Please reconfigure with a valid API key."
            ) from err
            
        except MeteocatAPIError as err:
            raise UpdateFailed(f"Error communicating with Meteocat API: {err}") from err
