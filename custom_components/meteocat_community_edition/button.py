"""Button platform for Meteocat (Community Edition)."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_MODE, DOMAIN, MODE_LOCAL, MODE_EXTERNAL
from .coordinator import MeteocatCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteocat button entities."""
    coordinator: MeteocatCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    from .const import CONF_MUNICIPALITY_NAME, CONF_STATION_NAME
    
    mode = entry.data.get(CONF_MODE, MODE_EXTERNAL)

    if mode == MODE_EXTERNAL:
        station_code = entry.data.get("station_code")
        station_name = entry.data.get(CONF_STATION_NAME, f"Station {station_code}")
        entity_name = station_name
        device_name = f"{station_name} {station_code}"
    else:  # MODE_LOCAL
        municipality_code = entry.data.get("municipality_code")
        entity_name = entry.data.get(CONF_MUNICIPALITY_NAME, f"Municipality {municipality_code}")
        device_name = entity_name
    
    buttons = []
    
    if mode == MODE_EXTERNAL:
        # External mode: Two buttons (Measurements and Forecast)
        buttons.append(
            MeteocatRefreshMeasurementsButton(coordinator, entry, entity_name, device_name, mode)
        )
        buttons.append(
            MeteocatRefreshForecastButton(coordinator, entry, entity_name, device_name, mode)
        )
    else:
        # Local mode: One button (Forecast)
        buttons.append(
            MeteocatRefreshForecastButton(coordinator, entry, entity_name, device_name, mode)
        )
    
    async_add_entities(buttons)


class MeteocatRefreshMeasurementsButton(CoordinatorEntity[MeteocatCoordinator], ButtonEntity):
    """Button to manually refresh Meteocat measurements."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        mode: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_translation_key = "refresh_measurements"
        self._attr_unique_id = f"{entry.entry_id}_refresh_measurements"
        self._attr_has_entity_name = True
        self._entity_name = entity_name
        self._device_name = device_name
        self._mode = mode
        self._entry = entry
        self._attr_icon = "mdi:refresh"
        # Generate entity_id based on mode
        base_name = entity_name.lower().replace(" ", "_")
        if mode == MODE_EXTERNAL:
            station_code = entry.data.get("station_code", "").lower()
            code_lower = station_code.replace(" ", "_")
            self.entity_id = f"button.{base_name}_{code_lower}_refresh_measurements"
        else:  # Should not happen for measurements button, but safe fallback
            self.entity_id = f"button.{base_name}_refresh_measurements"
        # Set device info to group with sensors and weather entity
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": "Meteocat Edició Comunitària",
            "model": "Estació Externa",
        }

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:refresh"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Always available to allow manual refresh even if API is down
        return True

    async def async_press(self) -> None:
        """Handle the button press."""
        if hasattr(self.coordinator, "async_refresh_measurements"):
            await self.coordinator.async_refresh_measurements()
        else:
            await self.coordinator.async_request_refresh()


class MeteocatRefreshForecastButton(CoordinatorEntity[MeteocatCoordinator], ButtonEntity):
    """Button to manually refresh Meteocat forecast."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MeteocatCoordinator,
        entry: ConfigEntry,
        entity_name: str,
        device_name: str,
        mode: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_translation_key = "refresh_forecast"
        self._attr_unique_id = f"{entry.entry_id}_refresh_forecast"
        self._attr_has_entity_name = True
        self._entity_name = entity_name
        self._device_name = device_name
        self._mode = mode
        self._entry = entry
        self._attr_icon = "mdi:refresh"
        
        # Generate entity_id based on mode
        base_name = entity_name.lower().replace(" ", "_")
        if mode == MODE_EXTERNAL:
            station_code = entry.data.get("station_code", "").lower()
            code_lower = station_code.replace(" ", "_")
            self.entity_id = f"button.{base_name}_{code_lower}_refresh_forecast"
        else:  # MODE_LOCAL
            self.entity_id = f"button.{base_name}_refresh_forecast"
        
        # Set device info to group with sensors and weather entity
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": "Meteocat Edició Comunitària",
            "model": "Estació Externa" if mode == MODE_EXTERNAL else "Estació Local",
        }

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:refresh"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Always available to allow manual refresh even if API is down
        return True

    async def async_press(self) -> None:
        """Handle the button press."""
        if hasattr(self.coordinator, "async_refresh_forecast"):
            await self.coordinator.async_refresh_forecast()
        else:
            await self.coordinator.async_request_refresh()
