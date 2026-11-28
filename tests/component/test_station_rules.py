"""Tests for station threshold rules and their configured actions."""
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteocat_community_edition.const import (
    CONF_API_KEY,
    CONF_ENABLE_FORECAST_DAILY,
    CONF_ENABLE_FORECAST_HOURLY,
    CONF_MODE,
    CONF_SENSOR_HUMIDITY,
    CONF_SENSOR_TEMPERATURE,
    CONF_STATION_RULES,
    CONF_UPDATE_TIME_1,
    DOMAIN,
    MODE_EXTERNAL,
    MODE_LOCAL,
)
from custom_components.meteocat_community_edition.coordinator import (
    MeteocatCoordinator,
)
from custom_components.meteocat_community_edition.station_rules import (
    StationRuleManager,
    condition_matches,
    external_measurement_value,
)


@pytest.mark.parametrize(
    ("value", "operator", "threshold", "expected"),
    [
        (26, ">", 25, True),
        (25, ">", 25, False),
        (25, ">=", 25, True),
        (-1, "<", 0, True),
        (0, "<=", 0, True),
    ],
)
def test_condition_matches(value, operator, threshold, expected):
    assert condition_matches(value, operator, threshold) is expected


def test_external_measurement_value_uses_sensor_semantics():
    measurements = [
        {
            "variables": [
                {"codi": 32, "lectures": [{"valor": 24.1}, {"valor": "25.2"}]},
                {
                    "codi": 35,
                    "lectures": [
                        {"valor": 0.4},
                        {"valor": None},
                        {"valor": "0.3"},
                    ],
                },
            ]
        }
    ]

    assert external_measurement_value(measurements, "32") == 25.2
    assert external_measurement_value(measurements, "35") == 0.7
    assert external_measurement_value(measurements, "34") is None
    assert external_measurement_value(None, "32") is None


@pytest.mark.asyncio
async def test_external_rules_fire_only_when_condition_crosses_up(hass: HomeAssistant):
    calls: list[str] = []

    async def record_action(call):
        calls.append(call.data["value"])

    hass.services.async_register("test", "record_action", record_action)
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY: "test-key", CONF_MODE: MODE_EXTERNAL},
        options={
            CONF_STATION_RULES: [
                {
                    "id": "hot",
                    "parameter": "32",
                    "operator": ">",
                    "threshold": 25,
                    "actions": [
                        {
                            "action": "test.record_action",
                            "data": {"value": "temperature threshold"},
                        }
                    ],
                }
            ]
        },
    )
    entry.add_to_hass(hass)
    manager = StationRuleManager(hass, entry)

    def update_temperature(value):
        manager.process_external_measurements(
            [{"variables": [{"codi": 32, "lectures": [{"valor": value}]}]}]
        )

    update_temperature(27)
    update_temperature(30)
    await hass.async_block_till_done()
    assert calls == []

    update_temperature(24)
    update_temperature(26)
    update_temperature(28)
    await hass.async_block_till_done()
    assert calls == ["temperature threshold"]

    update_temperature(25)
    update_temperature(26)
    await hass.async_block_till_done()
    assert calls == ["temperature threshold", "temperature threshold"]


@pytest.mark.asyncio
async def test_coordinator_evaluates_only_successful_measurement_refreshes(
    hass: HomeAssistant,
):
    calls: list[int] = []

    async def record_action(call):
        calls.append(call.data["value"])

    hass.services.async_register("test", "record_temperature", record_action)
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test-key",
            CONF_MODE: MODE_EXTERNAL,
            "station_code": "YM",
            "_station_data": {"codi": "YM"},
        },
        options={
            CONF_STATION_RULES: [
                {
                    "id": "hot",
                    "parameter": "32",
                    "operator": ">",
                    "threshold": 25,
                    "actions": [
                        {
                            "action": "test.record_temperature",
                            "data": {"value": 1},
                        }
                    ],
                }
            ]
        },
    )
    entry.add_to_hass(hass)
    coordinator = MeteocatCoordinator(hass, entry)
    coordinator.enable_forecast_daily = False
    coordinator.enable_forecast_hourly = False
    readings = iter((27, 24, 26))

    async def get_measurements(_station_code):
        value = next(readings)
        return [
            {
                "codi": "YM",
                "variables": [
                    {"codi": 32, "lectures": [{"valor": value}]}
                ],
            }
        ]

    coordinator.api.get_station_measurements = get_measurements
    coordinator.api.get_quotes = AsyncMock(return_value={})
    coordinator.api.find_municipality_for_station = AsyncMock(return_value=None)

    try:
        coordinator._force_measurements = True
        data = await coordinator._async_update_data()
        coordinator.data = data
        await hass.async_block_till_done()
        assert calls == []

        coordinator._force_forecast = True
        data = await coordinator._async_update_data()
        coordinator.data = data
        await hass.async_block_till_done()
        assert calls == []

        for expected_calls in (0, 1):
            coordinator._force_measurements = True
            data = await coordinator._async_update_data()
            coordinator.data = data
            await hass.async_block_till_done()
            assert len(calls) == expected_calls
    finally:
        await coordinator.async_shutdown()

    assert calls == [1]


@pytest.mark.asyncio
async def test_local_rules_ignore_initial_and_unavailable_values(hass: HomeAssistant):
    entity_id = "sensor.local_temperature"
    hass.states.async_set(entity_id, "-2")
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test-key",
            CONF_MODE: MODE_LOCAL,
            CONF_SENSOR_TEMPERATURE: entity_id,
        },
        options={
            CONF_STATION_RULES: [
                {
                    "id": "freezing",
                    "parameter": CONF_SENSOR_TEMPERATURE,
                    "operator": "<",
                    "threshold": 0,
                    "actions": [{"action": "homeassistant.update_entity"}],
                }
            ]
        },
    )
    entry.add_to_hass(hass)
    manager = StationRuleManager(hass, entry)
    schedule_actions = Mock()
    manager._schedule_actions = schedule_actions
    manager.async_setup()

    hass.states.async_set(entity_id, "-3")
    hass.states.async_set(entity_id, "unknown")
    hass.states.async_set(entity_id, "-2")
    hass.states.async_set(entity_id, "2")
    await hass.async_block_till_done()
    assert schedule_actions.call_count == 0

    hass.states.async_set(entity_id, "-1")
    await hass.async_block_till_done()
    assert schedule_actions.call_count == 1

    manager.async_unload()


@pytest.mark.asyncio
async def test_rule_runs_configured_home_assistant_actions(hass: HomeAssistant):
    calls: list[str] = []

    async def record_action(call):
        calls.append(call.data["value"])

    hass.services.async_register("test", "record_action", record_action)
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY: "test-key", CONF_MODE: MODE_EXTERNAL},
    )
    entry.add_to_hass(hass)
    manager = StationRuleManager(hass, entry)

    await manager._async_run_actions(
        {
            "id": "test-action",
            "actions": [
                {
                    "action": "test.record_action",
                    "data": {"value": "executed"},
                }
            ],
        }
    )

    assert calls == ["executed"]


@pytest.mark.asyncio
async def test_external_options_flow_saves_station_rule(hass: HomeAssistant):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test-key",
            CONF_MODE: MODE_EXTERNAL,
            "station_code": "YM",
            "municipality_code": "081131",
        },
        options={},
    )
    entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = type(
        "CoordinatorStub",
        (),
        {
            "data": {
                "measurements": [
                    {
                        "variables": [
                            {"codi": 32, "lectures": [{"valor": 20}]},
                            {"codi": 35, "lectures": [{"valor": 1}]},
                        ]
                    }
                ]
            }
        },
    )()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_UPDATE_TIME_1: "06:00",
            CONF_ENABLE_FORECAST_DAILY: True,
            CONF_ENABLE_FORECAST_HOURLY: False,
        },
    )
    assert result["step_id"] == "station_rules"
    station_rules_schema = result["data_schema"].schema
    action_selector = next(
        selector
        for marker, selector in station_rules_schema.items()
        if str(marker) == "rule_action"
    )
    assert action_selector.config["mode"] == "dropdown"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"rule_action": "add"}
    )
    assert result["step_id"] == "station_rule"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"form_action": "cancel"}
    )
    assert result["step_id"] == "station_rules"
    assert entry.options.get(CONF_STATION_RULES, []) == []

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"rule_action": "add"}
    )
    assert result["step_id"] == "station_rule"
    rule_schema = result["data_schema"].schema
    parameter_selector = next(
        selector
        for marker, selector in rule_schema.items()
        if str(marker) == "parameter"
    )
    parameter_labels = {
        option["label"] for option in parameter_selector.config["options"]
    }
    assert parameter_labels == {"Temperature", "Daily precipitation"}
    operator_selector = next(
        selector
        for marker, selector in rule_schema.items()
        if str(marker) == "operator"
    )
    assert operator_selector.config["mode"] == "dropdown"
    with pytest.raises(InvalidData):
        await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                "form_action": "save",
                "parameter": "34",
                "operator": ">",
                "threshold": 25,
                "actions": [
                    {
                        "action": "homeassistant.update_entity",
                        "target": {"entity_id": "sensor.test"},
                    }
                ],
            },
        )

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "form_action": "save",
            "parameter": "32",
            "operator": ">",
            "threshold": 25,
            "actions": [
                {
                    "action": "homeassistant.update_entity",
                    "target": {"entity_id": "sensor.test"},
                }
            ],
        },
    )
    assert result["step_id"] == "station_rules"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"rule_action": "done"}
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    rule = entry.options[CONF_STATION_RULES][0]
    assert rule["parameter"] == "32"
    assert rule["operator"] == ">"
    assert rule["threshold"] == 25
    assert rule["actions"][0]["action"] == "homeassistant.update_entity"


@pytest.mark.asyncio
async def test_local_options_flow_saves_rule_for_configured_sensor(
    hass: HomeAssistant,
):
    hass.states.async_set(
        "sensor.outdoor_temperature",
        "20",
        {
            "friendly_name": "Davis Vue temperature",
            "unit_of_measurement": "°F",
        },
    )
    hass.states.async_set(
        "sensor.outdoor_humidity",
        "50",
        {
            "friendly_name": "Davis Vue humidity",
            "unit_of_measurement": "%",
        },
    )
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test-key",
            CONF_MODE: MODE_LOCAL,
            "municipality_code": "081131",
            CONF_SENSOR_TEMPERATURE: "sensor.outdoor_temperature",
            CONF_SENSOR_HUMIDITY: "sensor.outdoor_humidity",
            "mapping_type": "meteocat",
        },
        options={},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_UPDATE_TIME_1: "06:00",
            CONF_ENABLE_FORECAST_DAILY: True,
            CONF_ENABLE_FORECAST_HOURLY: False,
        },
    )
    assert result["step_id"] == "local_sensors"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_SENSOR_TEMPERATURE: "sensor.outdoor_temperature",
            CONF_SENSOR_HUMIDITY: "sensor.outdoor_humidity",
        },
    )
    assert result["step_id"] == "condition_mapping_type"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"mapping_type": "meteocat"}
    )
    assert result["step_id"] == "station_rules"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"rule_action": "add"}
    )
    assert result["step_id"] == "station_rule"
    rule_schema = result["data_schema"].schema
    parameter_selector = next(
        selector
        for marker, selector in rule_schema.items()
        if str(marker) == "parameter"
    )
    parameter_labels = {
        option["label"] for option in parameter_selector.config["options"]
    }
    assert parameter_labels == {"Temperature", "Relative humidity"}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "form_action": "save",
            "parameter": CONF_SENSOR_TEMPERATURE,
            "operator": "<",
            "threshold": 0,
            "actions": [
                {
                    "action": "homeassistant.update_entity",
                    "target": {"entity_id": "sensor.test"},
                }
            ],
        },
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"rule_action": "done"}
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_STATION_RULES][0]["parameter"] == (
        CONF_SENSOR_TEMPERATURE
    )
