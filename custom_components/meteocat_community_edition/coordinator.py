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
- MODE_ESTACIO: Queries XEMA and Forecast plans per update
- MODE_MUNICIPI: Queries Forecast plan per update
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
        
        # Try to load cached station data from entry.data to avoid extra API call on restart
        self.station_data: dict[str, Any] = entry.data.get("_station_data", {})
        self.last_successful_update_time: datetime | None = None
        self.next_scheduled_update: datetime | None = None
        self._previous_next_update: datetime | None = None
        self._scheduled_update_remover = None
        self._retry_remover = None  # For intelligent retry scheduling
        self._is_retry_update = False  # Track if current update is a retry
        self._is_first_refresh = True  # Track if this is the first refresh during setup
        
        # For XEMA mode, municipality code will be found from station
        # For MUNICIPAL mode, municipality code is already set
        if self.mode == MODE_MUNICIPI and not self.municipality_code:
            _LOGGER.error("Municipal mode requires municipality_code!")
        
        # ⚠️ CRITICAL: API QUOTA PRESERVATION ⚠️
        # update_interval MUST be None to disable automatic polling.
        # Automatic polling would cause updates every few minutes, exhausting the monthly
        # API quota in just a few days instead of lasting the full month.
        #
        # Updates will ONLY happen in these cases:
        # 1. On first setup (async_config_entry_first_refresh) - 1 time
        # 2. At scheduled times (via _schedule_next_update) - 2 times/day by default
        # 3. Manual button press (async_request_refresh) - user controlled
        #
        # DO NOT change update_interval to any value other than None without reviewing
        # quota calculations and updating tests in test_scheduled_updates.py
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.station_code}",
            update_interval=None,  # ⚠️ CRITICAL: Must be None to prevent quota exhaustion
        )

    @callback
    def _schedule_next_update(self) -> None:
        """Schedule the next automatic update at the configured time.
        
        ⚠️ CRITICAL: This method MUST be called after first refresh to enable scheduled updates.
        
        It calculates the next update time based on configured hours (update_time_1, update_time_2)
        and schedules an exact-time update using async_track_point_in_utc_time.
        
        IMPORTANT: Always cancels the previous scheduler to prevent duplicate scheduled updates,
        which would double the API quota consumption.
        
        Called from:
        - async_setup_entry in __init__.py (after first refresh)
        - _async_scheduled_update (after each scheduled update completes)
        """
        # ⚠️ CRITICAL: Cancel any existing scheduled update to prevent duplicates
        # Duplicate schedulers would double API quota consumption
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
        
        # Store the next scheduled update time for the sensor
        self.next_scheduled_update = next_update
        
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

    async def _async_scheduled_update(self, now: datetime) -> None:
        """Handle scheduled update."""
        _LOGGER.info("Running scheduled update at %s", now)
        await self.async_request_refresh()
        
        # Reschedule for the next update time
        self._schedule_next_update()

    async def async_shutdown(self) -> None:
        """Clean up when shutting down.
        
        ⚠️ CRITICAL: This method MUST be called when unloading the integration.
        
        Cancels any pending scheduled updates to prevent orphaned schedulers that would
        continue making API calls even after the integration is unloaded, wasting quota.
        
        Called from:
        - async_unload_entry in __init__.py
        """
        if self._scheduled_update_remover:
            self._scheduled_update_remover()
            self._scheduled_update_remover = None
        if self._retry_remover:
            self._retry_remover()
            self._retry_remover = None

    @callback
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is temporary and should trigger a retry.
        
        Returns True for temporary/transient errors:
        - Network timeouts and connection errors
        - Server errors (500, 502, 503)
        
        Returns False for permanent errors that won't benefit from retry:
        - Authentication errors (401, 403) - triggers reauth flow instead
        - Not found errors (404) - station/municipality doesn't exist
        - Rate limit (429) - already has retry logic with backoff in api.py
        """
        # Authentication errors should trigger reauth, not retry
        if isinstance(error, MeteocatAuthError):
            return False
        
        # Network/timeout errors are retryable
        if isinstance(error, (ServerTimeoutError, ClientError)):
            return True
        
        # Check for server errors in API error messages
        if isinstance(error, MeteocatAPIError):
            error_msg = str(error).lower()
            # Server errors are retryable
            if any(code in error_msg for code in ['500', '502', '503']):
                return True
            # Client errors (404, etc.) are not retryable
            if any(code in error_msg for code in ['404', '400']):
                return False
        
        # By default, don't retry unknown errors
        return False

    async def _schedule_retry_update(self, delay_seconds: int = 60) -> None:
        """Schedule a retry update after a delay.
        
        Only schedules retry for temporary/transient errors. Quota is preserved by:
        1. Only 1 retry attempt (no infinite retries)
        2. Quotes API is only called if retry succeeds
        3. Retry is skipped if already in retry mode
        
        Args:
            delay_seconds: Seconds to wait before retry (default: 60)
        """
        # Cancel any existing retry to prevent duplicates
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

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Meteocat API.
        
        ⚠️ CRITICAL: API Call Order for Accurate Quota Tracking
        
        The order of API calls is CRITICAL for accurate quota consumption tracking:
        1. Fetch all data APIs first (stations, measurements, forecasts, UV)
        2. Fetch quotes API LAST to reflect accurate consumption after all calls
        
        If quotes is fetched first, it won't include the consumption from this update,
        leading to incorrect quota reporting to users.
        
        API Calls per Update:
        - MODE_ESTACIO (first): get_stations(1) + measurements(1) + forecast(1) + hourly(1) + uv(1) + quotes(1) = 6 calls
        - MODE_ESTACIO (subsequent): measurements(1) + forecast(1) + hourly(1) + uv(1) + quotes(1) = 5 calls
        - MODE_MUNICIPI: forecast(1) + hourly(1) + uv(1) + quotes(1) = 4 calls
        
        Quota Exhaustion Handling:
        - During first refresh (_is_first_refresh=True): Tolerant to missing data
          - Allows integration setup to complete even if quotas exhausted
          - Data will be fetched on next scheduled update when quota available
        - During subsequent updates: Strict validation, fails if critical data missing
        
        Test Coverage: test_quotes_fetched_after_other_api_calls in test_scheduled_updates.py
        """
        
        # Capture timestamp at the START of the update (when button is pressed)
        self.last_successful_update_time = dt_util.utcnow()
        
        try:
            # Build tasks based on mode
            # ⚠️ CRITICAL: Quotes will be fetched AFTER these tasks complete
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
                        # Save station data to entry.data for persistence across HA restarts
                        updated_data = {**self.entry.data, "_station_data": self.station_data}
                        self.hass.config_entries.async_update_entry(
                            self.entry,
                            data=updated_data
                        )
                        
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
            
            # Process results and track if we have any retryable errors
            # Station should be None in MUNICIPI mode
            data: dict[str, Any] = {
                "station": self.station_data if self.mode == MODE_ESTACIO else None,
                "municipality_code": self.municipality_code,
            }
            
            has_retryable_error = False
            for key, result in zip(tasks.keys(), results):
                if isinstance(result, Exception):
                    _LOGGER.warning("Error fetching %s: %s", key, result)
                    # Authentication errors should be re-raised immediately
                    if isinstance(result, MeteocatAuthError):
                        raise result
                    data[key] = None
                    # Check if this is a retryable error and we're not already retrying
                    if not self._is_retry_update and self._is_retryable_error(result):
                        has_retryable_error = True
                else:
                    data[key] = result
            
            # ⚠️ CRITICAL: Fetch quotes AFTER all other API calls to get accurate consumption
            # This ensures the quota sensors show consumption that includes this update's calls
            # Test: test_quotes_fetched_after_other_api_calls
            # IMPORTANT: Skip quotes on retry to avoid double-counting quota consumption
            if not self._is_retry_update:
                try:
                    data["quotes"] = await self.api.get_quotes()
                except Exception as err:
                    _LOGGER.warning("Error fetching quotes: %s", err)
                    data["quotes"] = None
            else:
                # On retry, keep previous quotes data
                _LOGGER.debug("Skipping quotes fetch on retry to preserve quota accuracy")
                data["quotes"] = None
            
            # Schedule retry if we had retryable errors (only on first attempt, not on retry)
            if has_retryable_error:
                _LOGGER.warning("Retryable error detected, scheduling retry in 60 seconds")
                await self._schedule_retry_update(delay_seconds=60)
                # Don't fire events or return data if we have errors - wait for retry
                raise UpdateFailed("Temporary error - retry scheduled")
            
            # Check if we have all required data (no None values in critical fields)
            # During first refresh, be tolerant to missing data to allow setup even if quotas exhausted
            # Scheduled updates will fetch data when quota is available
            critical_fields = []
            if self.mode == MODE_ESTACIO:
                critical_fields = ["measurements"]
            # Forecasts and UV are important for both modes if municipality_code exists
            if self.municipality_code:
                critical_fields.extend(["forecast", "forecast_hourly", "uv_index"])
            
            missing_data = [field for field in critical_fields if data.get(field) is None]
            if missing_data:
                error_msg = f"Missing critical data: {', '.join(missing_data)}"
                if self._is_first_refresh:
                    # During first refresh, log warning but allow setup to complete
                    # Data will be fetched on next scheduled update when quota available
                    _LOGGER.warning(
                        "%s - Setup will complete, data will be fetched on next scheduled update",
                        error_msg
                    )
                else:
                    # On subsequent updates, fail if critical data missing
                    _LOGGER.error(error_msg)
                    raise UpdateFailed(error_msg)
            
            # Mark first refresh as complete
            self._is_first_refresh = False
            
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
        
        except (MeteocatAPIError, ClientError, ServerTimeoutError, asyncio.TimeoutError) as err:
            # Check if this is a retryable error and we're not already in retry mode
            if not self._is_retry_update and self._is_retryable_error(err):
                _LOGGER.warning("Retryable error: %s. Scheduling retry in 60 seconds", err)
                await self._schedule_retry_update(delay_seconds=60)
                raise UpdateFailed(f"Temporary error - retry scheduled: {err}") from err
            
            # Non-retryable or already retrying
            raise UpdateFailed(f"Error communicating with Meteocat API: {err}") from err
