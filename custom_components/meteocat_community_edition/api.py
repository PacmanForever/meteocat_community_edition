"""API Client for Meteocat."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

import aiohttp

from .const import (
    API_TIMEOUT,
    DEFAULT_API_BASE_URL,
    ENDPOINT_COMARQUES,
    ENDPOINT_FORECAST_HOURLY,
    ENDPOINT_FORECAST_MUNICIPAL,
    ENDPOINT_MUNICIPALITIES,
    ENDPOINT_QUOTES,
    ENDPOINT_UV_INDEX,
    ENDPOINT_XEMA_MEASUREMENTS,
    ENDPOINT_XEMA_STATIONS,
)

_LOGGER = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2  # Exponential backoff: 1s, 2s, 4s


class MeteocatAPIError(Exception):
    """Base exception for Meteocat API errors."""


class MeteocatAuthError(MeteocatAPIError):
    """Exception for authentication errors (401, 403)."""


class MeteocatAPI:
    """Class to interact with Meteocat API."""

    def __init__(
        self,
        api_key: str,
        session: aiohttp.ClientSession,
        base_url: str = DEFAULT_API_BASE_URL,
    ) -> None:
        """Initialize the API client."""
        self.api_key = api_key
        self.session = session
        self.base_url = base_url.rstrip("/")

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        retry_count: int = 0,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a request to the Meteocat API with retry logic."""
        url = f"{self.base_url}{endpoint}"
        headers = {"x-api-key": self.api_key}
        
        # Debug: Log request details (mask API key)
        masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if len(self.api_key) > 8 else "***"
        _LOGGER.debug("API Request: %s %s (key: %s, attempt: %d/%d)", 
                     method, url, masked_key, retry_count + 1, MAX_RETRIES)

        try:
            async with asyncio.timeout(API_TIMEOUT):
                async with self.session.request(
                    method, url, headers=headers, params=params
                ) as response:
                    _LOGGER.debug("API Response status: %s for %s", response.status, url)
                    
                    # Handle authentication errors (don't retry)
                    if response.status in (401, 403):
                        _LOGGER.error(
                            "Authentication error %s for %s - API key may be invalid or expired. "
                            "Key length: %d, URL: %s",
                            response.status,
                            endpoint,
                            len(self.api_key),
                            url
                        )
                        raise MeteocatAuthError(
                            f"Authentication failed with status {response.status}. "
                            "Please check your API key."
                        )
                    
                    # Handle rate limiting (429) - retry with backoff
                    if response.status == 429:
                        if retry_count < MAX_RETRIES:
                            retry_after = int(response.headers.get("Retry-After", RETRY_BACKOFF_FACTOR ** retry_count))
                            _LOGGER.warning(
                                "Rate limited (429) for %s. Retrying after %d seconds (attempt %d/%d)",
                                endpoint, retry_after, retry_count + 1, MAX_RETRIES
                            )
                            await asyncio.sleep(retry_after)
                            return await self._request(method, endpoint, params, retry_count + 1)
                        raise MeteocatAPIError(f"Rate limit exceeded for {endpoint} after {MAX_RETRIES} retries")
                    
                    response.raise_for_status()
                    
                    # Read raw bytes and decode as UTF-8
                    raw_data = await response.read()
                    text = raw_data.decode('utf-8')
                    import json
                    return json.loads(text)
                    
        except MeteocatAuthError:
            # Re-raise auth errors without retry
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            # Retry on network errors with exponential backoff
            if retry_count < MAX_RETRIES:
                backoff_time = RETRY_BACKOFF_FACTOR ** retry_count
                _LOGGER.warning(
                    "Request failed for %s: %s. Retrying in %d seconds (attempt %d/%d)",
                    endpoint, err, backoff_time, retry_count + 1, MAX_RETRIES
                )
                await asyncio.sleep(backoff_time)
                return await self._request(method, endpoint, params, retry_count + 1)
            
            # Max retries exceeded
            error_msg = f"Timeout connecting to Meteocat API" if isinstance(err, asyncio.TimeoutError) else f"Error connecting to Meteocat API: {err}"
            _LOGGER.error("%s after %d retries", error_msg, MAX_RETRIES)
            raise MeteocatAPIError(error_msg) from err

    async def get_comarques(self) -> list[dict[str, Any]]:
        """Get list of comarques (counties)."""
        _LOGGER.debug("Fetching comarques list")
        return await self._request("GET", ENDPOINT_COMARQUES)

    async def get_stations(self) -> list[dict[str, Any]]:
        """Get list of all weather stations."""
        _LOGGER.debug("Fetching stations list")
        return await self._request("GET", ENDPOINT_XEMA_STATIONS)

    async def get_stations_by_comarca(self, comarca_code: str) -> list[dict[str, Any]]:
        """Get weather stations filtered by comarca."""
        all_stations = await self.get_stations()
        # Filter stations by comarca code
        return [
            station
            for station in all_stations
            if station.get("comarca", {}).get("codi") == comarca_code
        ]

    async def get_station_measurements(
        self, station_code: str
    ) -> dict[str, Any]:
        """Get current measurements for a station."""
        _LOGGER.debug("Fetching measurements for station %s", station_code)
        # API requires date: /xema/v1/estacions/mesurades/{codi}/{any}/{mes}/{dia}
        now = datetime.now()
        endpoint = f"/xema/v1/estacions/mesurades/{station_code}/{now.year}/{now.month:02d}/{now.day:02d}"
        return await self._request("GET", endpoint)

    async def get_municipalities(self) -> list[dict[str, Any]]:
        """Get list of municipalities."""
        _LOGGER.debug("Fetching municipalities list")
        return await self._request("GET", ENDPOINT_MUNICIPALITIES)

    async def get_municipal_forecast(
        self, municipality_code: str
    ) -> dict[str, Any]:
        """Get municipal forecast (daily 8 days)."""
        _LOGGER.debug("Fetching municipal forecast for %s", municipality_code)
        endpoint = f"{ENDPOINT_FORECAST_MUNICIPAL}/{municipality_code}"
        return await self._request("GET", endpoint)

    async def get_hourly_forecast(
        self, municipality_code: str
    ) -> dict[str, Any]:
        """Get hourly forecast (72 hours)."""
        _LOGGER.debug("Fetching hourly forecast for %s", municipality_code)
        endpoint = f"{ENDPOINT_FORECAST_HOURLY}/{municipality_code}"
        return await self._request("GET", endpoint)

    async def get_uv_index(
        self, municipality_code: str
    ) -> dict[str, Any]:
        """Get UV index forecast for municipality."""
        _LOGGER.debug("Fetching UV index for %s", municipality_code)
        endpoint = f"{ENDPOINT_UV_INDEX}/{municipality_code}"
        return await self._request("GET", endpoint)

    async def get_quotes(self) -> dict[str, Any]:
        """Get API quota usage information."""
        _LOGGER.debug("Fetching API quota information")
        return await self._request("GET", ENDPOINT_QUOTES)

    async def find_municipality_for_station(
        self, station: dict[str, Any]
    ) -> str | None:
        """Find the municipality code for a given station based on coordinates."""
        try:
            municipalities = await self.get_municipalities()
            
            # Get station coordinates
            station_lat = station.get("coordenades", {}).get("latitud")
            station_lon = station.get("coordenades", {}).get("longitud")
            
            if not station_lat or not station_lon:
                _LOGGER.warning("Station %s has no coordinates", station.get("codi"))
                return None
            
            # Find the closest municipality
            # For simplicity, we'll use the municipality name matching
            # In a real implementation, you might want to use geospatial distance
            station_name = station.get("nom", "").lower()
            
            for municipality in municipalities:
                muni_name = municipality.get("nom", "").lower()
                if muni_name in station_name or station_name in muni_name:
                    return municipality.get("codi")
            
            # If no match found, return the first municipality in the comarca
            comarca_code = station.get("comarca", {}).get("codi")
            for municipality in municipalities:
                if municipality.get("comarca", {}).get("codi") == comarca_code:
                    return municipality.get("codi")
            
            _LOGGER.warning(
                "Could not find municipality for station %s", station.get("codi")
            )
            return None
            
        except MeteocatAPIError as err:
            _LOGGER.error("Error finding municipality for station: %s", err)
            return None
