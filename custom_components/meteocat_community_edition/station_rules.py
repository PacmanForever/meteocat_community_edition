"""Evaluate station rules and execute their configured actions."""
from __future__ import annotations

import asyncio
import logging
import math
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Context, Event, HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.script import Script

from .const import (
    CONF_MODE,
    CONF_SENSOR_APPARENT_TEMPERATURE,
    CONF_SENSOR_CLOUD_COVERAGE,
    CONF_SENSOR_DEW_POINT,
    CONF_SENSOR_HUMIDITY,
    CONF_SENSOR_OZONE,
    CONF_SENSOR_PRESSURE,
    CONF_SENSOR_RAIN_INTENSITY,
    CONF_SENSOR_TEMPERATURE,
    CONF_SENSOR_UV_INDEX,
    CONF_SENSOR_VISIBILITY,
    CONF_SENSOR_WIND_BEARING,
    CONF_SENSOR_WIND_GUST,
    CONF_SENSOR_WIND_SPEED,
    CONF_STATION_RULES,
    DOMAIN,
    MODE_EXTERNAL,
    MODE_LOCAL,
    XEMA_VARIABLES,
)

_LOGGER = logging.getLogger(__name__)
_LOCAL_PARAMETERS = (
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
_OPERATORS = {">", ">=", "<", "<="}


def _numeric_value(value: Any) -> float | None:
    """Return a finite numeric value, or None for invalid sensor states."""
    if isinstance(value, bool):
        return None
    try:
        numeric_value = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return numeric_value if math.isfinite(numeric_value) else None


def condition_matches(value: float, operator: str, threshold: float) -> bool:
    """Check a numeric value against a configured comparison."""
    if operator == ">":
        return value > threshold
    if operator == ">=":
        return value >= threshold
    if operator == "<":
        return value < threshold
    if operator == "<=":
        return value <= threshold
    raise ValueError(f"Unsupported station rule operator: {operator}")


def external_measurement_value(measurements: Any, variable_code: str) -> float | None:
    """Extract the value exposed by the matching Meteocat measurement sensor."""
    if not isinstance(measurements, list) or not measurements:
        return None
    station = measurements[0]
    if not isinstance(station, dict):
        return None
    variables = station.get("variables")
    if not isinstance(variables, list):
        return None

    for variable in variables:
        if not isinstance(variable, dict) or str(variable.get("codi")) != variable_code:
            continue
        lectures = variable.get("lectures")
        if not isinstance(lectures, list) or not lectures:
            return None

        if variable_code == str(XEMA_VARIABLES["precipitation"]):
            total = 0.0
            for reading in lectures:
                if isinstance(reading, dict):
                    numeric_value = _numeric_value(reading.get("valor"))
                    if numeric_value is not None:
                        total += numeric_value
            return round(total, 1)

        latest_reading = lectures[-1]
        if isinstance(latest_reading, dict):
            return _numeric_value(latest_reading.get("valor"))
        return None
    return None


class StationRuleManager:
    """Track station parameter conditions and run actions on false-to-true edges."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.mode = entry.data.get(CONF_MODE, MODE_EXTERNAL)
        configured_rules = (entry.options or {}).get(CONF_STATION_RULES, [])
        self._rules: list[dict[str, Any]] = []
        if isinstance(configured_rules, list):
            for rule in configured_rules:
                if not isinstance(rule, dict):
                    continue
                rule_id = rule.get("id")
                parameter = rule.get("parameter")
                operator = rule.get("operator")
                threshold = _numeric_value(rule.get("threshold"))
                actions = rule.get("actions")
                if (
                    not isinstance(rule_id, str)
                    or not isinstance(parameter, str)
                    or not isinstance(operator, str)
                    or operator not in _OPERATORS
                    or threshold is None
                    or not isinstance(actions, list)
                    or not actions
                ):
                    _LOGGER.warning(
                        "Skipping invalid station rule in config entry %s",
                        entry.entry_id,
                    )
                    continue
                try:
                    actions = cv.SCRIPT_SCHEMA(actions)
                except vol.Invalid:
                    _LOGGER.warning(
                        "Skipping station rule with invalid actions in config entry %s",
                        entry.entry_id,
                    )
                    continue
                self._rules.append(
                    {
                        "id": rule_id,
                        "parameter": parameter,
                        "operator": operator,
                        "threshold": threshold,
                        "actions": actions,
                    }
                )

        self._last_conditions: dict[str, bool | None] = {
            rule["id"]: None for rule in self._rules
        }
        self._action_locks: dict[str, asyncio.Lock] = {}
        self._remove_local_listener: Any = None

    def async_setup(self) -> None:
        """Subscribe to local source sensors and capture their initial values."""
        if self.mode != MODE_LOCAL:
            return

        entity_ids = {
            entity_id
            for rule in self._rules
            if rule["parameter"] in _LOCAL_PARAMETERS
            if isinstance(
                entity_id := self._local_entity_id(rule["parameter"]), str
            )
        }
        if not entity_ids:
            return

        self._remove_local_listener = async_track_state_change_event(
            self.hass, list(entity_ids), self._async_handle_local_state_change
        )
        for entity_id in entity_ids:
            self._process_local_value(entity_id, self.hass.states.get(entity_id))

    @callback
    def _async_handle_local_state_change(self, event: Event) -> None:
        entity_id = event.data.get("entity_id")
        if not isinstance(entity_id, str):
            return
        self._process_local_value(entity_id, event.data.get("new_state"))

    def _process_local_value(self, entity_id: str, state: Any) -> None:
        value = _numeric_value(getattr(state, "state", None))
        for rule in self._rules:
            if (
                rule["parameter"] in _LOCAL_PARAMETERS
                and self._local_entity_id(rule["parameter"]) == entity_id
            ):
                self._observe(rule, value)

    def _local_entity_id(self, parameter: str) -> str | None:
        """Return the configured entity ID for a local parameter."""
        entity_id = self.entry.data.get(parameter)
        if isinstance(entity_id, list):
            entity_id = entity_id[0] if entity_id else None
        return entity_id if isinstance(entity_id, str) else None

    def process_external_measurements(self, measurements: Any) -> None:
        """Evaluate external rules after a successful measurements refresh."""
        if self.mode != MODE_EXTERNAL:
            return
        for rule in self._rules:
            if rule["parameter"].isdigit():
                value = external_measurement_value(
                    measurements, rule["parameter"]
                )
                self._observe(rule, value)

    def _observe(self, rule: dict[str, Any], value: float | None) -> None:
        rule_id = rule["id"]
        if value is None:
            self._last_conditions[rule_id] = None
            return

        condition = condition_matches(value, rule["operator"], rule["threshold"])
        previous_condition = self._last_conditions[rule_id]
        if previous_condition is False and condition:
            self._schedule_actions(rule)
        self._last_conditions[rule_id] = condition

    def _schedule_actions(self, rule: dict[str, Any]) -> None:
        self.entry.async_create_background_task(
            self.hass,
            self._async_run_actions(rule),
            name=f"{DOMAIN} station rule {rule['id']}",
        )

    async def _async_run_actions(self, rule: dict[str, Any]) -> None:
        """Execute a rule's action sequence without overlapping itself."""
        rule_id = rule["id"]
        lock = self._action_locks.setdefault(rule_id, asyncio.Lock())
        async with lock:
            sequence = cv.SCRIPT_SCHEMA(rule["actions"])
            script = Script(
                self.hass,
                sequence,
                f"{DOMAIN} station rule {rule_id}",
                DOMAIN,
            )
            await script.async_run(context=Context())

    def async_unload(self) -> None:
        """Remove local sensor subscriptions."""
        if self._remove_local_listener is not None:
            self._remove_local_listener()
            self._remove_local_listener = None
