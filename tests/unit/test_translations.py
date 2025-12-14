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
    # Get the absolute path to the custom_components directory
    test_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(os.path.dirname(test_dir))
    component_dir = os.path.join(project_root, "custom_components", "meteocat_community_edition")
    
    if lang == "en":
        # For English, load strings.json from the component root
        path = os.path.join(component_dir, "strings.json")
    else:
        path = os.path.join(component_dir, "translations", f"{lang}.json")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_options_flow_description_content():
    """Test that options flow description is correct and does not contain 'advanced options'."""
    
    # Catalan
    ca = load_translation("ca")
    desc_ca = ca["options"]["step"]["init"]["description"]
    assert desc_ca == "Indica a quines hores vols que s'actualitzi la predicció:"
    assert "opcions avançades" not in desc_ca
    
    # Spanish
    es = load_translation("es")
    desc_es = es["options"]["step"]["init"]["description"]
    assert desc_es == "Indica a qué horas quieres que se actualice.'"
    assert "opciones avanzadas" not in desc_es
    
    # English
    en = load_translation("en")
    desc_en = en["options"]["step"]["init"]["description"]
    assert desc_en == ""
    assert "advanced options" not in desc_en


def test_options_flow_title_content():
    """Test that options flow title is correct for external station configuration."""
    
    # Catalan
    ca = load_translation("ca")
    title_ca = ca["options"]["step"]["init"]["title"]
    assert title_ca == "Configura la predicció de Meteocat"
    
    # Spanish
    es = load_translation("es")
    title_es = es["options"]["step"]["init"]["title"]
    assert title_es == "Configuración de la estación externa"
    
    # English
    en = load_translation("en")
    title_en = en["options"]["step"]["init"]["title"]
    assert title_en == "Configuration"


def test_update_times_title_and_description():
    """Test that update_times step has correct title and empty description."""
    
    # Catalan
    ca = load_translation("ca")
    title_ca = ca["config"]["step"]["update_times"]["title"]
    desc_ca = ca["config"]["step"]["update_times"]["description"]
    assert title_ca == "Configura la predicció de Meteocat"
    assert desc_ca == "Indica a quines hores vols que s'actualitzi:"
    
    # Spanish
    es = load_translation("es")
    title_es = es["config"]["step"]["update_times"]["title"]
    desc_es = es["config"]["step"]["update_times"]["description"]
    assert title_es == "Configuración de la predicción Meteocat"
    assert desc_es == "Indica a qué horas quieres que se actualice.'"
    
    # English
    en = load_translation("en")
    title_en = en["config"]["step"]["update_times"]["title"]
    desc_en = en["config"]["step"]["update_times"]["description"]
    assert title_en == "Data Updates"
    assert desc_en == "Configure data to download and update times.\n\n**Query Types**\n{measurements_info}"


def test_condition_mapping_custom_texts():
    """Test that condition mapping custom step has correct texts."""
    
    # Catalan
    ca = load_translation("ca")
    title_ca = ca["config"]["step"]["condition_mapping_custom"]["title"]
    desc_ca = ca["config"]["step"]["condition_mapping_custom"]["description"]
    entity_label_ca = ca["config"]["step"]["condition_mapping_custom"]["data"]["local_condition_entity"]
    mapping_label_ca = ca["config"]["step"]["condition_mapping_custom"]["data"]["custom_condition_mapping"]
    
    assert title_ca == "Configura el mapeig de la condició climàtica"
    assert desc_ca == ""
    assert entity_label_ca == "Sensor que indica la condició"
    assert mapping_label_ca == "Mapeig de valors"
    
    # Spanish
    es = load_translation("es")
    title_es = es["config"]["step"]["condition_mapping_custom"]["title"]
    desc_es = es["config"]["step"]["condition_mapping_custom"]["description"]
    entity_label_es = es["config"]["step"]["condition_mapping_custom"]["data"]["local_condition_entity"]
    mapping_label_es = es["config"]["step"]["condition_mapping_custom"]["data"]["custom_condition_mapping"]
    
    assert title_es == "Configuración del mapeo de la condición climática"
    assert desc_es == ""
    assert entity_label_es == "Sensor que indica la condición"
    assert mapping_label_es == "Mapeo de valores"
    
    # English
    en = load_translation("en")
    title_en = en["config"]["step"]["condition_mapping_custom"]["title"]
    desc_en = en["config"]["step"]["condition_mapping_custom"]["description"]
    entity_label_en = en["config"]["step"]["condition_mapping_custom"]["data"]["local_condition_entity"]
    mapping_label_en = en["config"]["step"]["condition_mapping_custom"]["data"]["custom_condition_mapping"]
    
    assert title_en == "Weather Condition Mapping Configuration"
    assert desc_en == "Select the sensor that contains the condition value and the mapping to be used."
    assert entity_label_en == "Sensor that indicates the condition (required)"
    assert mapping_label_en == "Value mapping (required)"


def test_required_field_error_translation():
    """Test that required field error message exists in all languages."""
    
    # Catalan
    ca = load_translation("ca")
    required_ca = ca["config"]["error"]["required"]
    assert required_ca == "Aquest camp és obligatori"
    
    # Spanish
    es = load_translation("es")
    required_es = es["config"]["error"]["required"]
    assert required_es == "Este campo es obligatorio"
    
    # English
    en = load_translation("en")
    required_en = en["config"]["error"]["required"]
    assert required_en == "This field is required"
