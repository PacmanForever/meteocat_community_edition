"""Button platform for Meteocat (Community Edition)."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_MODE, DOMAIN, MODE_MUNICIPI, MODE_ESTACIO
from .coordinator import MeteocatCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteocat button entities."""
    coordinator: MeteocatCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    from .const import CONF_MUNICIPALITY_NAME, CONF_STATION_NAME
    
    mode = entry.data.get(CONF_MODE, MODE_ESTACIO)

    if mode == MODE_ESTACIO:
        station_code = entry.data.get("station_code")
        station_name = entry.data.get(CONF_STATION_NAME, f"Station {station_code}")
        entity_name = station_name
        device_name = f"{station_name} {station_code}"
    else:  # MODE_MUNICIPI
        municipality_code = entry.data.get("municipality_code")
        entity_name = entry.data.get(CONF_MUNICIPALITY_NAME, f"Municipality {municipality_code}")
        device_name = entity_name
    
    async_add_entities([
        MeteocatRefreshButton(coordinator, entry, entity_name, device_name, mode)
    ])


class MeteocatRefreshButton(CoordinatorEntity[MeteocatCoordinator], ButtonEntity):
    """Button to manually refresh Meteocat data."""

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
        self._attr_name = "Actualitzar dades"
        self._attr_unique_id = f"{entry.entry_id}_refresh"
        self._entity_name = entity_name
        self._device_name = device_name
        self._mode = mode
        self._entry = entry
        
        # Generate entity_id based on mode
        base_name = entity_name.lower().replace(" ", "_")
        if mode == MODE_ESTACIO:
            station_code = entry.data.get("station_code", "").lower()
            code_lower = station_code.replace(" ", "_")
            self.entity_id = f"button.{base_name}_{code_lower}_refresh"
        else:  # MODE_MUNICIPI
            self.entity_id = f"button.{base_name}_refresh"
        
        # Set device info to group with sensors and weather entity
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": "Meteocat Edició Comunitària",
            "model": "Estació XEMA" if mode == MODE_ESTACIO else "Predicció Municipi",
        }

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:refresh"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_request_refresh()
