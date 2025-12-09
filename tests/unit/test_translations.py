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
    desc_ca = ca["options"]["step"]["init"]["description"]
    assert "Configura les dades a descarregar" in desc_ca
    assert "opcions avançades" not in desc_ca
    
    # Spanish
    es = load_translation("es")
    desc_es = es["options"]["step"]["init"]["description"]
    assert "Configura los datos a descargar" in desc_es
    assert "opciones avanzadas" not in desc_es
    
    # English
    en = load_translation("en")
    desc_en = en["options"]["step"]["init"]["description"]
    assert "Configure data to download" in desc_en
    assert "advanced options" not in desc_en
