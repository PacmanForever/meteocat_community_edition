"""Data coordinator for Meteocat (Community Edition).

⚠️ CRITICAL: API Quota Management System ⚠️

This coordinator implements a CRITICAL scheduled update system to prevent API quota exhaustion.
DO NOT modify the update mechanism without understanding the quota implications.

Key Implementation Points:
1. update_interval=None - MUST remain None (no automatic polling)
2. _schedule_next_update() - MUST be called after first refresh
3. async_shutdown() - MUST be called on unload to prevent orphaned schedulers
4. Quotes API - MUST be called AFTER all other APIs for accurate consumption tracking
5. Scheduler cancellation - MUST cancel previous scheduler when rescheduling to avoid duplicates

Quota Usage (with default 06:00 and 14:00 updates):
- 2 scheduled updates per day per configured instance
- MODE_EXTERNAL: Queries XEMA and Forecast plans per update
- MODE_LOCAL: Queries Forecast plan per update
- Station data cached in entry.data to save 1 API call per HA restart
- Municipality/comarca/province names from config (no API calls needed)

Test Coverage: 17 comprehensive tests in tests/test_scheduled_updates.py
Last Reviewed: 2025-11-27
"""
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

try:
    from aiohttp import ClientError, ServerTimeoutError
except ImportError:
    # Fallback for potential future aiohttp changes
    from aiohttp.client_exceptions import ClientError, ServerTimeoutError

from .api import MeteocatAPI, MeteocatAPIError, MeteocatAuthError
from .const import (
    CONF_API_BASE_URL,
    CONF_API_KEY,
    CONF_MODE,
    CONF_MUNICIPALITY_CODE,
    CONF_STATION_CODE,
    CONF_UPDATE_TIME_1,
    CONF_UPDATE_TIME_2,
    CONF_UPDATE_TIME_3,
    CONF_ENABLE_FORECAST_DAILY,
    CONF_ENABLE_FORECAST_HOURLY,
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
    MODE_EXTERNAL,
    MODE_LOCAL,
)

_LOGGER = logging.getLogger(__name__)


class MeteocatCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for Meteocat data (handles both External and Local modes)."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.mode = entry.data.get(CONF_MODE, MODE_EXTERNAL)
        self.station_code = entry.data.get(CONF_STATION_CODE)
        self.municipality_code = entry.data.get(CONF_MUNICIPALITY_CODE)
        
        # If municipality code is not set (external mode), try to get it from station_municipality_code
        if not self.municipality_code and self.mode == MODE_EXTERNAL:
            self.municipality_code = entry.data.get("station_municipality_code")
        
        # Get update times from config or use defaults
        self.update_time_1 = entry.data.get(CONF_UPDATE_TIME_1, DEFAULT_UPDATE_TIME_1)
        self.update_time_2 = entry.data.get(CONF_UPDATE_TIME_2, DEFAULT_UPDATE_TIME_2)
        self.update_time_3 = entry.data.get(CONF_UPDATE_TIME_3, "")
        
        # Get forecast settings
        self.enable_forecast_daily = entry.data.get(CONF_ENABLE_FORECAST_DAILY, True)
        self.enable_forecast_hourly = entry.data.get(CONF_ENABLE_FORECAST_HOURLY, False)
        
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
        
        self.last_successful_update_time: datetime | None = None
        self.next_scheduled_update: datetime | None = None
        self._previous_next_update: datetime | None = None
        self._scheduled_update_remover = None
        self._retry_remover = None
        self._is_retry_update = False
        self._is_first_refresh = True
        
        # Station specific attributes
        self.station_data: dict[str, Any] = entry.data.get("_station_data", {})
        self.last_forecast_update: datetime | None = None
        self.next_forecast_update: datetime | None = None
        
        name = f"{DOMAIN}_{entry.entry_id}"
        if self.mode == MODE_EXTERNAL and self.station_code:
            name = f"{DOMAIN}_{self.station_code}"
        elif self.mode == MODE_LOCAL:
            name = f"{DOMAIN}_forecast_{entry.entry_id}"

        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=None,  # ⚠️ CRITICAL: Must be None to prevent quota exhaustion
        )

    @callback
    def _schedule_next_update(self) -> None:
        """Schedule the next automatic update."""
        if self._scheduled_update_remover:
            self._scheduled_update_remover()
            self._scheduled_update_remover = None
        
        now = dt_util.now()
        
        if self.mode == MODE_EXTERNAL:
            # External Mode: Hourly updates
            # Schedule for the next hour top (e.g. 10:00, 11:00)
            next_update = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            
            # Calculate next forecast update for display/logic
            self._calculate_next_forecast_update(now)
        else:
            # Local Mode: Scheduled times only
            today = now.date()
            
            update_times_list = [self.update_time_1, self.update_time_2]
            if self.update_time_3:
                update_times_list.append(self.update_time_3)
                
            update_datetimes = [
                dt_util.as_local(
                    datetime.combine(today, time.fromisoformat(update_time))
                )
                for update_time in update_times_list
                if update_time and update_time.strip()
            ]
            
            next_update = None
            for update_dt in sorted(update_datetimes):
                if update_dt > now:
                    next_update = update_dt
                    break
            
            if next_update is None:
                tomorrow = today + timedelta(days=1)
                sorted_times = sorted([t for t in update_times_list if t and t.strip()])
                if sorted_times:
                    next_update = dt_util.as_local(
                        datetime.combine(tomorrow, time.fromisoformat(sorted_times[0]))
                    )
        
        if not next_update:
            _LOGGER.warning("Could not calculate next update time. Automatic updates disabled.")
            self.next_scheduled_update = None
            return

        self.next_scheduled_update = next_update
        
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

    def _calculate_next_forecast_update(self, now: datetime) -> None:
        """Calculate the next scheduled forecast update (External Mode)."""
        today = now.date()
        
        update_times_list = [self.update_time_1, self.update_time_2]
        if self.update_time_3:
            update_times_list.append(self.update_time_3)
            
        update_datetimes = [
            dt_util.as_local(
                datetime.combine(today, time.fromisoformat(update_time))
            )
            for update_time in update_times_list
            if update_time and update_time.strip()
        ]
        
        next_forecast = None
        for update_dt in sorted(update_datetimes):
            if update_dt > now:
                next_forecast = update_dt
                break
        
        if next_forecast is None:
            tomorrow = today + timedelta(days=1)
            sorted_times = sorted([t for t in update_times_list if t and t.strip()])
            if sorted_times:
                next_forecast = dt_util.as_local(
                    datetime.combine(tomorrow, time.fromisoformat(sorted_times[0]))
                )
        
        self.next_forecast_update = next_forecast

    async def _async_scheduled_update(self, now: datetime) -> None:
        """Handle scheduled update."""
        _LOGGER.info("Running scheduled update at %s", now)
        self._schedule_next_update()
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Clean up when shutting down."""
        if self._scheduled_update_remover:
            self._scheduled_update_remover()
            self._scheduled_update_remover = None
        if self._retry_remover:
            self._retry_remover()
            self._retry_remover = None

    @callback
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is temporary and should trigger a retry."""
        if isinstance(error, MeteocatAuthError):
            return False
        if isinstance(error, (ServerTimeoutError, ClientError)):
            return True
        if isinstance(error, MeteocatAPIError):
            error_msg = str(error).lower()
            if any(code in error_msg for code in ['500', '502', '503']):
                return True
            if any(code in error_msg for code in ['404', '400']):
                return False
        return False

    async def _schedule_retry_update(self, delay_seconds: int = 60) -> None:
        """Schedule a retry update after a delay."""
        if self._retry_remover:
            self._retry_remover()
            self._retry_remover = None
        
        retry_time = dt_util.utcnow() + timedelta(seconds=delay_seconds)
        _LOGGER.info("Scheduling retry update in %d seconds at %s", delay_seconds, retry_time)
        
        self._retry_remover = async_track_point_in_utc_time(
            self.hass,
            self._async_retry_update,
            retry_time,
        )

    async def _async_retry_update(self, now: datetime) -> None:
        """Handle retry update after a temporary failure."""
        _LOGGER.info("Running retry update at %s", now)
        self._is_retry_update = True
        try:
            await self.async_request_refresh()
        finally:
            self._is_retry_update = False
            self._retry_remover = None

    def _fire_events(self, current_next_update: datetime | None) -> None:
        """Fire events after update."""
        # Fire event if next update time changed
        if current_next_update != self._previous_next_update:
            next_update_event_data = {
                EVENT_ATTR_MODE: self.mode,
                EVENT_ATTR_TIMESTAMP: dt_util.now().isoformat(),
                EVENT_ATTR_NEXT_UPDATE: current_next_update.isoformat() if current_next_update else None,
                EVENT_ATTR_PREVIOUS_UPDATE: self._previous_next_update.isoformat() if self._previous_next_update else None,
            }
            
            if self.mode == MODE_EXTERNAL and self.station_code:
                next_update_event_data[EVENT_ATTR_STATION_CODE] = self.station_code
            
            if self.municipality_code:
                next_update_event_data[EVENT_ATTR_MUNICIPALITY_CODE] = self.municipality_code
            
            try:
                device_registry = dr.async_get(self.hass)
                device = device_registry.async_get_device(
                    identifiers={(DOMAIN, self.entry.entry_id)}
                )
                if device and device.id:
                    next_update_event_data["device_id"] = device.id
            except (AttributeError, ValueError) as err:
                _LOGGER.debug("Could not get device_id: %s", err)
            
            self.hass.bus.fire(EVENT_NEXT_UPDATE_CHANGED, next_update_event_data)
            self._previous_next_update = current_next_update
        
        # Fire event to notify about data update
        event_data = {
            EVENT_ATTR_MODE: self.mode,
            EVENT_ATTR_TIMESTAMP: dt_util.now().isoformat(),
        }
        
        if self.mode == MODE_EXTERNAL and self.station_code:
            event_data[EVENT_ATTR_STATION_CODE] = self.station_code
        
        if self.municipality_code:
            event_data[EVENT_ATTR_MUNICIPALITY_CODE] = self.municipality_code
        
        try:
            device_registry = dr.async_get(self.hass)
            device = device_registry.async_get_device(
                identifiers={(DOMAIN, self.entry.entry_id)}
            )
            if device and device.id:
                event_data["device_id"] = device.id
        except (AttributeError, ValueError) as err:
            _LOGGER.debug("Could not get device_id: %s", err)
        
        self.hass.bus.fire(EVENT_DATA_UPDATED, event_data)

    async def async_refresh_measurements(self) -> None:
        """Force refresh of measurements only."""
        self._force_measurements = True
        await self.async_request_refresh()

    async def async_refresh_forecast(self) -> None:
        """Force refresh of forecast only."""
        self._force_forecast = True
        await self.async_request_refresh()

    def _should_fetch_forecast(self) -> bool:
        """Check if forecast should be fetched based on current time."""
        # Always fetch on first refresh or if missing data
        if self._is_first_refresh or not self.data or not self.data.get("forecast"):
            _LOGGER.debug("Fetching forecast because data is missing or first refresh")
            return True
            
        now = dt_util.now()
        
        update_times = [self.update_time_1, self.update_time_2]
        if self.update_time_3:
            update_times.append(self.update_time_3)
            
        for time_str in update_times:
            if not time_str:
                continue
            try:
                update_time = time.fromisoformat(time_str)
                # If we are in the same hour as the update time
                if now.hour == update_time.hour:
                    _LOGGER.debug("Fetching forecast because hour %s matches update time %s", now.hour, time_str)
                    return True
            except ValueError:
                continue
        
        _LOGGER.debug("Not fetching forecast. Hour %s does not match any update time %s", now.hour, update_times)
        return False

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all data (External + Local)."""
        
        # Check forced update flags
        force_measurements = getattr(self, "_force_measurements", False)
        force_forecast = getattr(self, "_force_forecast", False)
        
        # Reset flags
        self._force_measurements = False
        self._force_forecast = False
        
        try:
            tasks = {}
            
            # Determine what to fetch
            fetch_measurements = False
            fetch_forecast = False
            
            if self.mode == MODE_EXTERNAL:
                if force_measurements or force_forecast:
                    # Manual update via specific button
                    fetch_measurements = force_measurements
                    fetch_forecast = force_forecast
                else:
                    # Scheduled or generic update
                    fetch_measurements = True
                    fetch_forecast = self._should_fetch_forecast()
            else:
                # Local Mode: Always fetch forecast on update
                fetch_forecast = True
                fetch_measurements = False
            
            if self.mode == MODE_EXTERNAL and self.station_code and fetch_measurements:
                tasks["measurements"] = self.api.get_station_measurements(self.station_code)
                
                entry_updates = {}
                if not self.station_data:
                    stations = await self.api.get_stations()
                    for station in stations:
                        if station.get("codi") == self.station_code:
                            self.station_data = station
                            break
                    if self.station_data:
                        entry_updates["_station_data"] = self.station_data
                
                if not self.municipality_code and self.station_data:
                    self.municipality_code = await self.api.find_municipality_for_station(
                        self.station_data
                    )
                    if self.municipality_code:
                        entry_updates["station_municipality_code"] = self.municipality_code
                
                if entry_updates:
                    new_data = {**self.entry.data, **entry_updates}
                    if new_data != self.entry.data:
                        self.hass.config_entries.async_update_entry(
                            self.entry,
                            data=new_data
                        )
            
            if self.municipality_code and fetch_forecast:
                if self.enable_forecast_daily:
                    tasks["forecast"] = self.api.get_municipal_forecast(
                        self.municipality_code
                    )
                if self.enable_forecast_hourly:
                    tasks["forecast_hourly"] = self.api.get_hourly_forecast(
                        self.municipality_code
                    )
                
                # Update last forecast update time if we are attempting to fetch
                self.last_forecast_update = dt_util.utcnow()
            
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            
            # Initialize data with previous values if available to preserve forecast
            data: dict[str, Any] = self.data.copy() if self.data else {
                "station": self.station_data if self.mode == MODE_EXTERNAL else None,
                "municipality_code": self.municipality_code,
            }
            
            has_retryable_error = False
            for key, result in zip(tasks.keys(), results):
                if isinstance(result, Exception):
                    _LOGGER.warning("Error fetching %s: %s", key, result)
                    if isinstance(result, MeteocatAuthError):
                        raise result
                    # If fetch failed, keep old data if available, or set to None
                    if key not in data:
                        data[key] = None
                    
                    if not self._is_retry_update and self._is_retryable_error(result):
                        has_retryable_error = True
                else:
                    data[key] = result
            
            if not self._is_retry_update:
                # Only fetch quotes when fetching forecast to save quota
                # OR if quotes are missing (e.g. failed previously)
                should_fetch_quotes = fetch_forecast or not data.get("quotes")
                
                if should_fetch_quotes:
                    try:
                        data["quotes"] = await self.api.get_quotes()
                    except MeteocatAPIError as err:
                        if "429" in str(err) or "Rate limit exceeded" in str(err):
                            _LOGGER.warning("Quota exceeded (429). Setting remaining requests to 0.")
                            # If we have previous quotes, use them as a template but set remaining to 0
                            old_quotes = data.get("quotes")
                            if old_quotes and isinstance(old_quotes, dict) and "plans" in old_quotes:
                                new_plans = []
                                for plan in old_quotes.get("plans", []):
                                    new_plan = plan.copy()
                                    new_plan["consultesRestants"] = 0
                                    new_plans.append(new_plan)
                                data["quotes"] = {
                                    "client": old_quotes.get("client", {}),
                                    "plans": new_plans
                                }
                            else:
                                _LOGGER.warning("Quota exceeded and no previous data available to construct zero-quota state.")
                                if "quotes" not in data:
                                    data["quotes"] = None
                        else:
                            _LOGGER.warning("Error fetching quotes: %s", err)
                            # Keep old quotes if available
                            if "quotes" not in data:
                                data["quotes"] = None
                    except Exception as err:
                        _LOGGER.warning("Error fetching quotes: %s", err)
                        # Keep old quotes if available
                        if "quotes" not in data:
                            data["quotes"] = None
            else:
                # On retry, don't fetch quotes to save calls, keep old
                if "quotes" not in data:
                    data["quotes"] = None
            
            if has_retryable_error:
                _LOGGER.warning("Retryable error detected, scheduling retry in 60 seconds")
                await self._schedule_retry_update(delay_seconds=60)
                raise UpdateFailed("Temporary error - retry scheduled")
            
            critical_fields = []
            if self.mode == MODE_EXTERNAL and fetch_measurements:
                critical_fields.append("measurements")
            if self.municipality_code:
                # Only check forecast if we tried to fetch it or if it's missing
                if fetch_forecast or not data.get("forecast"):
                    if self.enable_forecast_daily:
                        critical_fields.append("forecast")
                    if self.enable_forecast_hourly:
                        critical_fields.append("forecast_hourly")
            
            missing_data = [field for field in critical_fields if data.get(field) is None]
            if missing_data:
                error_msg = f"Missing critical data: {', '.join(missing_data)}"
                if self._is_first_refresh:
                    _LOGGER.warning(
                        "%s - Setup will complete, data will be fetched on next scheduled update",
                        error_msg
                    )
                else:
                    _LOGGER.error(error_msg)
                    raise UpdateFailed(error_msg)
            
            self._is_first_refresh = False
            self._fire_events(self.next_scheduled_update)
            
            self.last_successful_update_time = dt_util.utcnow()
            return data
        
        except MeteocatAuthError as err:
            _LOGGER.error("Authentication failed: %s", err)
            raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
        
        except (MeteocatAPIError, ClientError, ServerTimeoutError, asyncio.TimeoutError) as err:
            if not self._is_retry_update and self._is_retryable_error(err):
                _LOGGER.warning("Retryable error: %s. Scheduling retry in 60 seconds", err)
                await self._schedule_retry_update(delay_seconds=60)
                raise UpdateFailed(f"Temporary error - retry scheduled: {err}") from err
            raise UpdateFailed(f"Error communicating with Meteocat API: {err}") from err

# Alias for backward compatibility (if needed by tests, but we should update tests)
MeteocatBaseCoordinator = MeteocatCoordinator
MeteocatForecastCoordinator = MeteocatCoordinator
MeteocatLegacyCoordinator = MeteocatCoordinator
