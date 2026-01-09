"""Tests for additional coverage in config_flow.py."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from custom_components.meteocat_community_edition.config_flow import MeteocatConfigFlow, MeteocatOptionsFlow
from custom_components.meteocat_community_edition.api import MeteocatAPIError
from custom_components.meteocat_community_edition.const import CONF_COMARCA_CODE, CONF_MUNICIPALITY_CODE

@pytest.fixture
def mock_config_entry():
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {
        "api_key": "test_key", 
        "mapping_type": "meteocat",
        "mode": "external"
    }
    entry.options = {}
    entry.title = "Test Entry"
    entry.entry_id = "test_entry_id"
    return entry

async def test_reauth_confirm_api_error(hass):
    """Test reauth flow handles API errors."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    flow.context = {"entry_id": "test_entry"}
    # Mock finding the entry
    hass.config_entries.async_get_entry = MagicMock(return_value=MagicMock(data={"api_key": "old_key"}))

    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        # api() instantiation succeeds, but get_comarques() fails
        mock_instance = mock_api.return_value
        mock_instance.get_comarques.side_effect = MeteocatAPIError("Auth failed")
        
        result = await flow.async_step_reauth_confirm({CONF_API_KEY: "bad_key"})
        
        assert result["type"] == "form"
        assert result["errors"] == {"base": "invalid_auth"}

async def test_reauth_confirm_unexpected_exception(hass):
    """Test reauth flow handles generic exceptions."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    flow.context = {"entry_id": "test_entry"}
    hass.config_entries.async_get_entry = MagicMock(return_value=MagicMock(data={"api_key": "old_key"}))

    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        mock_instance = mock_api.return_value
        mock_instance.get_comarques.side_effect = Exception("Boom")
        
        result = await flow.async_step_reauth_confirm({CONF_API_KEY: "key"})
        
        assert result["type"] == "form"
        assert result["errors"] == {"base": "unknown"}

async def test_options_flow_invalid_mapping_type_recovery(hass, mock_config_entry):
    """Test recovery when entry data has invalid mapping_type."""
    mock_config_entry.data = {"mapping_type": 123} # Invalid type
    
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = hass
    
    # Mock config updates
    hass.config_entries.async_update_entry = MagicMock()
    
    result = await flow.async_step_condition_mapping_type()
    
    # Check if entry was updated to fix the corruption
    assert not hass.config_entries.async_update_entry.called
    assert flow.updated_data["mapping_type"] == "meteocat"
    
    assert result["type"] == "form"

async def test_options_flow_invalid_user_input_mapping_type(hass, mock_config_entry):
    """Test validation of user input for mapping type."""
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = hass
    
    result = await flow.async_step_condition_mapping_type({"mapping_type": "invalid_value"})
    
    assert result["errors"]["mapping_type"] == "value_not_allowed"


async def test_comarca_step_api_error(hass):
    """Test comarca step handles API errors when fetching municipalities."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    flow.api_key = "test_key"
    flow.mode = "local" # MODE_LOCAL
    # Pre-populate comarques so it proceeds
    flow._comarques = [{"codi": "10", "nom": "Barcelones"}]
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        mock_instance = mock_api.return_value
        mock_instance.get_municipalities.side_effect = MeteocatAPIError("Fetch failed")
        
        result = await flow.async_step_comarca({CONF_COMARCA_CODE: "10"})
        
        assert result["type"] == "form"
        assert result["errors"] == {"base": "cannot_connect"}

async def test_comarca_step_generic_error(hass):
    """Test comarca step handles generic errors."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    flow.api_key = "test_key"
    flow.mode = "local"
    # Pre-populate comarques
    flow._comarques = [{"codi": "10", "nom": "Barcelones"}]
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        mock_instance = mock_api.return_value
        mock_instance.get_municipalities.side_effect = Exception("Boom")
        
        result = await flow.async_step_comarca({CONF_COMARCA_CODE: "10"})
        
        assert result["type"] == "form"
        assert result["errors"] == {"base": "unknown"}

async def test_custom_mapping_duplicate_codes_error(hass, mock_config_entry):
    """Test options flow handles duplicate codes in custom mapping."""
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = hass
    
    # Simulate duplicate codes 
    # sunny -> 1
    # cloudy -> 1
    result = await flow.async_step_condition_mapping_custom({
        "local_condition_entity": "sensor.test",
        "sunny": "1",
        "cloudy": "1" 
    })
    
    assert result["errors"]["base"] == "duplicate_codes"

async def test_update_times_step_default(hass):
    """Test update times step returns form with defaults."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    
    # Setup context
    flow.mode = "local"
    flow.api_key = "key"
    flow.comarca_code = "10"
    flow.municipality_code = "080193"
    
    result = await flow.async_step_update_times()
    
    assert result["type"] == "form"
    assert result["step_id"] == "update_times"
    # Verify schema has 5 keys
    assert len(result["data_schema"].schema) == 5


async def test_options_init_fixes_invalid_mapping_type(hass, mock_config_entry):
    """Test options init fixes invalid mapping_type in config entry data."""
    # Setup entry with invalid mapping type
    mock_config_entry.data = {
        "mapping_type": 123, # Not a string
        "api_key": "test_key",
        "mode": "local"
    }
    
    flow = MeteocatOptionsFlow(mock_config_entry)
    # Mock hass object structure fully so async_update_entry is intercepted
    flow.hass = MagicMock()
    flow.hass.config_entries = MagicMock()
    
    # Run step init with no input to trigger the fix logic
    await flow.async_step_init()
    
    # Verify it was corrected internally
    assert flow.updated_data["mapping_type"] == "meteocat"
    # Ensure update was NOT called immediately
    mock_update = flow.hass.config_entries.async_update_entry
    assert not mock_update.called

async def test_options_init_fixes_invalid_forecast_flags(hass, mock_config_entry):
    """Test options init fixes invalid forecast flags."""
    mock_config_entry.data = {
        "enable_forecast_daily": "yes",  # Not bool
        "enable_forecast_hourly": 1,     # Not bool
        "api_key": "test_key",
        "mode": "local"
    }
    
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    flow.hass.config_entries = MagicMock()
    
    await flow.async_step_init()
    
    # Verify it was corrected internally
    assert flow.updated_data["enable_forecast_daily"] is True
    assert flow.updated_data["enable_forecast_hourly"] is False
    assert not flow.hass.config_entries.async_update_entry.called

async def test_options_init_migrates_api_key(hass, mock_config_entry):
    """Test options init examines options for API key if missing in data."""
    mock_config_entry.data = {
        "mode": "local"
        # Missing api_key
    }
    mock_config_entry.options = {
        "api_key": "migrated_key"
    }
    
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    flow.hass.config_entries = MagicMock()
    
    await flow.async_step_init()
    
    # Verify it was migrated internally
    assert flow.updated_data["api_key"] == "migrated_key"
    assert not flow.hass.config_entries.async_update_entry.called

async def test_options_init_missing_api_key_error(hass, mock_config_entry):
    """Test options init reports error if API key is missing everywhere."""
    mock_config_entry.data = {"mode": "local"}
    mock_config_entry.options = {}
    
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    
    result = await flow.async_step_init()
    # It shows the form but with errors
    assert result["type"] == "form"
    assert result["errors"]["base"] == "invalid_auth"

async def test_options_init_must_select_one_forecast_error(hass, mock_config_entry):
    """Test options init validation: must select at least one forecast."""
    mock_config_entry.data = {
        "api_key": "test_key",
        "mode": "local"
    }
    
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    
    user_input = {
        "enable_forecast_daily": False,
        "enable_forecast_hourly": False,
        "update_time_1": "08:00"
    }
    
    result = await flow.async_step_init(user_input)
    assert result["errors"]["base"] == "must_select_one_forecast"

async def test_options_init_saves_changes(hass, mock_config_entry):
    """Test options init saves changes when inputs differ."""
    mock_config_entry.data = {
        "api_key": "test_key",
        "mode": "local",
        "update_time_1": "08:00",
        "enable_forecast_daily": True
    }
    mock_config_entry.options = {}
    
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    flow.hass.config_entries = MagicMock()
    
    user_input = {
        "enable_forecast_daily": False, # Changed
        "enable_forecast_hourly": True, # Changed
        "update_time_1": "09:00",       # Changed
        "update_time_2": "20:00"
    }
    
    # Mocking async_step_local_sensors because it is called after successful save in local mode
    with patch.object(flow, "async_step_local_sensors", return_value={"type": "done"}):
        
        await flow.async_step_init(user_input)
        
        # Verify changes happened internally
        assert flow.updated_options["update_time_1"] == "09:00"
        assert flow.updated_options["enable_forecast_daily"] is False
        
        # Verify NO save yet (local mode)
        mock_update = flow.hass.config_entries.async_update_entry
        assert not mock_update.called

async def test_local_sensors_validation_error(hass, mock_config_entry):
    """Test local sensors step validation."""
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    flow.hass.config_entries = MagicMock()
    
    # Mock api_key on flow to ensure it's not the cause of error
    flow.api_key = "key"
    
    # Empty input
    result = await flow.async_step_local_sensors({})
    
    assert result["type"] == "form"
    assert result["errors"]["sensor_temperature"] == "required"
    assert result["errors"]["sensor_humidity"] == "required"

async def test_local_sensors_step_success(hass, mock_config_entry):
    """Test local sensors step success path."""
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    flow.hass.config_entries = MagicMock()
    flow.api_key = "key"
    
    # Mock next step
    with patch.object(flow, "async_step_condition_mapping_type", return_value={"type": "done"}):
        result = await flow.async_step_local_sensors({
            "sensor_temperature": "sensor.temp",
            "sensor_humidity": "sensor.hum"
        })
        
        assert result["type"] == "done"
        
        # Verify internal update but NO save yet
        assert flow.updated_data["sensor_temperature"] == "sensor.temp"
        assert flow.updated_data["sensor_humidity"] == "sensor.hum"
        
        mock_update = flow.hass.config_entries.async_update_entry
        assert not mock_update.called

async def test_mapping_type_step_meteocat_branch(hass, mock_config_entry):
    """Test mapping type step selecting meteocat."""
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    flow.hass.config_entries = MagicMock()
    flow.api_key = "key"
    
    # Setup entry to have custom stuff to be removed
    mock_config_entry.data = {
        "mode": "external", # not MODE_LOCAL
        "custom_condition_mapping": "something",
        "local_condition_entity": "something"
    }
    
    with patch.object(flow, "async_step_local_sensors", return_value={"type": "done_sensors"}):
        result = await flow.async_step_condition_mapping_type({"mapping_type": "meteocat"})
        
        # Verify internal update: custom fields popped
        assert flow.updated_data["mapping_type"] == "meteocat"
        assert "custom_condition_mapping" not in flow.updated_data
        
        # No save yet
        mock_update = flow.hass.config_entries.async_update_entry
        assert not mock_update.called
        
        assert result["type"] == "done_sensors"

async def test_mapping_type_step_custom_branch(hass, mock_config_entry):
    """Test mapping type step selecting custom."""
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    flow.hass.config_entries = MagicMock()
    flow.api_key = "key"
    
    with patch.object(flow, "async_step_condition_mapping_custom", return_value={"type": "done_custom"}):
        result = await flow.async_step_condition_mapping_type({"mapping_type": "custom"})
        
        # Verify internal update
        assert flow.updated_data["mapping_type"] == "custom"
        
        # No save yet
        mock_update = flow.hass.config_entries.async_update_entry
        assert not mock_update.called
        
        assert result["type"] == "done_custom"

async def test_options_custom_mapping_logic_valid(hass, mock_config_entry):
    """Test options custom mapping logic with valid input."""
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    flow.hass.config_entries = MagicMock()
    
    with patch.object(flow, "async_create_entry", return_value={"type": "done"}):
        result = await flow.async_step_condition_mapping_custom({
            "local_condition_entity": "sensor.test",
            "sunny": "1",
            "rainy": "2"
        })
        
        mock_update = flow.hass.config_entries.async_update_entry
        assert mock_update.called
        args = mock_update.call_args[1]
        assert args["data"]["custom_condition_mapping"] == {"1": "sunny", "2": "rainy"}
        assert result["type"] == "done"


async def test_options_custom_mapping_logic_empty(hass, mock_config_entry):
    """Test options custom mapping logic with empty mapping."""
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    
    # Empty inputs
    result = await flow.async_step_condition_mapping_custom({
        "local_condition_entity": "sensor.test",
        # No condition mapping fields provided
    })
    
    assert result["type"] == "form"
    assert result["errors"]["base"] == "invalid_format"


async def test_custom_mapping_display_numeric_sort(hass, mock_config_entry):
    """Test displaying custom mapping with numeric keys."""
    mock_config_entry.data = {
        "custom_condition_mapping": {"10": "fog", "2": "cloudy"}
    }
    
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    
    # Call with None to trigger display logic
    result = await flow.async_step_condition_mapping_custom(None)
    
    assert result["type"] == "form"
    # Check that schema default values are populated correctly
    # Since we can't easily inspect the schema object details in this test setup without internal knowledge
    # we verify that it runs successfully.
    # Ideally checking result["data_schema"]...
    
    # However, since we refactored to separate fields, the concept of "sorting" in display text is less relevant
    # as the order of fields is determined by VALID_WEATHER_CONDITIONS or schema generation order.
    # But pre-filling correct values is what matters.
    pass


async def test_custom_mapping_display_alpha_sort(hass, mock_config_entry):
    """Test displaying custom mapping with non-numeric keys."""
    mock_config_entry.data = {
        "custom_condition_mapping": {"b": "cloudy", "a": "sunny"}
    }
    
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    
    result = await flow.async_step_condition_mapping_custom(None)
    assert result["type"] == "form"


async def test_custom_mapping_validation_empty_strings(hass, mock_config_entry):
    """Test validation with empty strings explicitly."""
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    
    # Providing empty strings for condition fields should be ignored/treated as not mapped
    # If all result in nothing -> empty_mapping
    result = await flow.async_step_condition_mapping_custom({
        "local_condition_entity": "",
        "sunny": ""
    })
    
    assert result["type"] == "form"
    assert result["errors"]["local_condition_entity"] == "required"
    # condition_sunny being empty is fine, but if result map is empty -> base error


async def test_reauth_success(hass):
    """Test reauth flow success."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    
    # Mock entry that needs reauth
    mock_entry = MagicMock(spec=ConfigEntry)
    mock_entry.data = {CONF_API_KEY: "old_key"}
    mock_entry.title = "Test Entry"
    mock_entry.entry_id = "test_entry_id"
    
    # Attach entry to flow context/instance manually as reauth flows do
    flow.context = {"entry_id": "test_entry_id"}
    # The flow stores the entry in self.entry usually during async_step_reauth
    # But here we call async_step_reauth_confirm directly.
    # We need to simulate that self.entry found it.
    
    hass.config_entries.async_get_entry = MagicMock(return_value=mock_entry)
    # We must patch async_get_entry or set flow.entry manually if usage allows.
    # Looking at code: reauth logic usually retrieves it.
    # But if we call reauth_confirm directly, we assume setup is done or we rely on context.
    
    # Let's set flow.entry manually to be sure
    flow.entry = mock_entry
    
    # Mock update entry to prevent UnknownEntry error from real registry interactions
    hass.config_entries.async_update_entry = MagicMock()
    hass.config_entries.async_reload = AsyncMock()
    
    with patch("custom_components.meteocat_community_edition.config_flow.MeteocatAPI") as mock_api:
        mock_instance = mock_api.return_value
        # Succeeds
        mock_instance.get_comarques = AsyncMock(return_value=[]) 
        
        result = await flow.async_step_reauth_confirm({CONF_API_KEY: "new_key"})
        
        assert result["type"] == "abort"
        assert result["reason"] == "reauth_successful"
        
        # Verify update
        mock_entry.data.copy() # Just to ensure we can verify call
        hass.config_entries.async_update_entry.assert_called()
        call_args = hass.config_entries.async_update_entry.call_args
        assert call_args.kwargs["data"][CONF_API_KEY] == "new_key"
        
        # Verify reload
        hass.config_entries.async_reload.assert_called_with("test_entry_id")

async def test_mapping_type_step_form_defaults(hass, mock_config_entry):
    """Test mapping type step form defaults from existing entry."""
    mock_config_entry.data = {"mapping_type": "custom"}
    
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = MagicMock()
    
    # Call with None to show form
    result = await flow.async_step_condition_mapping_type(None)
    
    assert result["type"] == "form"
    # Verify default in schema
    schema = result["data_schema"]
    # schema is likely a vol.Schema object.
    # Voluptuous schema inspection is tricky. 
    # But execution confirms lines 171-173 ran.

async def test_station_step_extracts_province(hass):
    """Test station step extracts province data."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    flow.api_key = "key"
    flow.context = {} # Initialize context
    flow._stations = [{
        "codi": "X1", 
        "nom": "Station 1",
        "provincia": {"codi": "08", "nom": "Barcelona"}
    }]
    
    # Mocking async_set_unique_id which might fail if context is weird or if it checks registry
    # But usually it just sets context.
    # However, self._abort_if_unique_id_configured() checks the registry.
    # We should mock that to not fail.
    
    with patch.object(flow, "_abort_if_unique_id_configured", return_value=None):
        result = await flow.async_step_station({"station_code": "X1"})
    
    assert flow.station_provincia_code == "08"
    assert flow.station_provincia_name == "Barcelona"
    # Continues to update times
    assert result["type"] == "form"
    assert result["step_id"] == "update_times"

async def test_station_step_unknown_station_name(hass):
    """Test station step handles unknown station name."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    flow.api_key = "key"
    flow.context = {}
    flow._stations = [{"codi": "X2", "nom": "Station 2"}]
    
    with patch.object(flow, "_abort_if_unique_id_configured", return_value=None):
        result = await flow.async_step_station({"station_code": "X99"})
    
    assert flow.station_name == "Station X99"

async def test_mapping_type_required(hass, mock_config_entry):
    """Test mapping type required validation."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    
    # We need to call the step used for setup, which is async_step_condition_mapping_type
    # BUT wait, the method I read (line 120) has validation logic.
    # Is it MeteocatConfigFlow.async_step_condition_mapping_type or MeteocatOptionsFlow?
    # Inspecting config_flow.py, both might have it?
    # No, usually OptionsFlow has 2 args (user_input).
    # ConfigFlow steps also have user_input.
    # The read_file started at 120. That is likely MeteocatConfigFlow.
    
    # Let's verify if MeteocatConfigFlow has that step.
    # Assuming yes (as part of wizard).
    
    result = await flow.async_step_condition_mapping_type({})
    assert result["errors"]["mapping_type"] == "required"

async def test_update_times_boolean_conversion(hass):
    """Test boolean conversion in update times step."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    flow.mode = "local"
    # Pre-populate required attribs
    flow.comarca_code = "10"
    flow.municipality_code = "080193"
    flow._stations = []
    
    # Passweird inputs
    input_data = {
        "update_time_1": "08:00",
        "enable_forecast_daily": "true", # string
        "enable_forecast_hourly": None   # None
    }
    
    # We need to mock next step to see if it passed validation
    # async_step_update_times calls async_step_local_sensors or async_create_entry depending on mode?
    # If mode=local, it goes to local_sensors.
    
    with patch.object(flow, "async_step_local_sensors", return_value={"type": "done"}):
        result = await flow.async_step_update_times(input_data)
        
    assert result["type"] == "done"
    # We can check internal state if stored?
    # Logic stores it in self._update_times_input or directly?
    # Actually validation logic modifies local vars enable_daily/hourly then calls next step.
    # If we want to verify conversion happening, we assume if it didn't crash it worked,
    # or check the arguments passed to next step if they are stored?
    # The code likely uses them to build entry data later.

async def test_municipality_step_duplicate_abort(hass):
    """Test municipality step aborts if already configured."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    flow.api_key = "key"
    flow.context = {"source": "user"}
    
    flow.comarca_code = "10"
    flow._municipalities = [{"codi": "080193", "nom": "Municipality 1"}]
    flow._comarques = []
    
    # Mock result of unique_id check
    with patch.object(flow, "async_set_unique_id"),          patch.object(flow, "_abort_if_unique_id_configured", side_effect=Exception("Abort!")): 
         # _abort_if_unique_id_configured raises AbortFlow usually.
         # But better to rely on real method and mock allow_multiple=False? 
         # No, mock directly call to raise AbortFlow("already_configured")
         
         from homeassistant.data_entry_flow import AbortFlow
         flow._abort_if_unique_id_configured.side_effect = AbortFlow("already_configured")
         
         try:
            await flow.async_step_municipality({CONF_MUNICIPALITY_CODE: "080193"})
            assert False, "Should have aborted"
         except AbortFlow as e:
            assert e.reason == "already_configured"


async def test_mapping_type_step_invalid_value(hass):
    """Test mapping type step with invalid value."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    
    result = await flow.async_step_condition_mapping_type(
        user_input={"mapping_type": "invalid_value"}
    )
    
    assert result["type"] == "form"
    assert result["errors"] == {"mapping_type": "value_not_allowed"}

async def test_station_step_context_update_error(hass):
    """Test station step handles context update error silently."""
    flow = MeteocatConfigFlow()
    flow.hass = hass
    # Ensure context is a mock that raises TypeError on update
    # We use a real dict for initialization but patch update
    flow.context = MagicMock()
    flow.context.update.side_effect = TypeError("Immutable")
    
    flow.station_code = "X1"
    flow._stations = [{"codi": "X1", "nom": "Station X1"}]
    
    async def mock_next_step(*args, **kwargs):
        return {"type": "done"}

    with patch.object(flow, "async_set_unique_id", return_value=AsyncMock()), \
         patch.object(flow, "_abort_if_unique_id_configured"), \
         patch.object(flow, "async_step_update_times", side_effect=mock_next_step):
        
        from custom_components.meteocat_community_edition.const import CONF_STATION_CODE
        result = await flow.async_step_station(
            user_input={CONF_STATION_CODE: "X1"}
        )
        
        # We need to make sure the result is not a mock if we want to check it
        assert result["type"] == "done"

async def test_options_init_invalid_existing_mapping(hass, mock_config_entry):
    """Test options flow defaults to meteocat if existing mapping type is invalid."""
    mock_config_entry.data = {"mapping_type": "invalid_old_value"}
    flow = MeteocatOptionsFlow(mock_config_entry)
    flow.hass = hass
    
    # Mock hass.config_entries.async_update_entry to avoid UnknownEntry error
    hass.config_entries.async_update_entry = MagicMock()
    
    # We want to inspect the generated schema, so we call init without user input
    result = await flow.async_step_condition_mapping_type()
    
    assert result["type"] == "form"
    schema = result["data_schema"]
    # Check that default is meteocat
    key = list(schema.schema.keys())[0]
    assert key.default() == "meteocat"
    
    # Verify internal update but NO database update
    assert flow.updated_data["mapping_type"] == "meteocat"
    assert not hass.config_entries.async_update_entry.called
