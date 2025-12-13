"""Test translation files for Meteocat."""
import json
import os
import pytest

# Ensure modules are loaded for conftest patches
try:
    import custom_components.meteocat_community_edition.coordinator
    import custom_components.meteocat_community_edition.config_flow
except ImportError:
    pass

def load_translation(lang):
    """Load translation file."""
    if lang == "en":
        # For English, load strings.json from the component root
        path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "custom_components",
            "meteocat_community_edition",
            "strings.json",
        )
    else:
        path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "custom_components",
            "meteocat_community_edition",
            "translations",
            f"{lang}.json",
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_options_flow_description_content():
    """Test that options flow description is correct and does not contain 'advanced options'."""
    
    # Catalan
    ca = load_translation("ca")
    desc_ca = ca["config"]["step"]["update_times"]["description"]
    assert desc_ca == "Indica a quines hores vols que s'actualitzi:"
    assert "opcions avançades" not in desc_ca
    
    # Spanish
    es = load_translation("es")
    desc_es = es["config"]["step"]["update_times"]["description"]
    assert desc_es == "Indica a qué horas quieres que se actualice.'"
    assert "opciones avanzadas" not in desc_es
    
    # English
    en = load_translation("en")
    desc_en = en["config"]["step"]["update_times"]["description"]
    assert desc_en == "Configure data to download and update times.\n\n**Query Types**\n{measurements_info}"
    assert "advanced options" not in desc_en

def test_options_flow_sensors_labels():
    """Test that options flow sensors step has correct labels."""
    from custom_components.meteocat_community_edition.const import CONF_SENSOR_TEMPERATURE
    
    for lang in ["ca", "es", "en"]:
        data = load_translation(lang)
        sensors_data = data["config"]["step"]["local_sensors"]["data"]
        
        # Check that the key exists
        assert CONF_SENSOR_TEMPERATURE in sensors_data
        
        # Check that it has a value
        assert sensors_data[CONF_SENSOR_TEMPERATURE] is not None
        assert len(sensors_data[CONF_SENSOR_TEMPERATURE]) > 0
