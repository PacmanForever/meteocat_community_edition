
"""Test the Meteocat options flow with missing data."""
from unittest.mock import patch
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteocat_community_edition.const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_MODE,
    MODE_EXTERNAL,
    CONF_STATION_CODE,
    CONF_MUNICIPALITY_CODE,
)

@pytest.mark.asyncio
async def test_options_flow_init_missing_data(hass: HomeAssistant):
    """Test options flow initialization with minimal data."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_key",
            CONF_MODE: MODE_EXTERNAL,
            CONF_STATION_CODE: "YM",
            # Missing update times
        },
        options={}
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"
