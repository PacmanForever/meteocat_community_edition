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


def load_strings():
    """Load the canonical integration strings."""
    path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "custom_components",
        "meteocat_community_edition",
        "strings.json",
    )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_options_flow_description_content():
    """Test that options flow description is correct and does not contain 'advanced options'."""
    
    # Catalan
    ca = load_translation("ca")
    desc_ca = ca["config"]["step"]["update_times"]["description"]
    assert desc_ca == "Indica a quines hores vols que s'actualitzi:\n\nATENCIÓ: Com més hores d'actualització i més tipus de predicció activis, més quota consumiràs i potser no arribes a final de mes."
    assert "opcions avançades" not in desc_ca
    
    # Spanish
    es = load_translation("es")
    desc_es = es["config"]["step"]["update_times"]["description"]
    assert desc_es == "Indica a qué horas quieres que se actualice.\n\nATENCIÓN: Cuantas más horas de actualización y más tipos de predicción actives, más cuota se consumirá. Si el consumo es demasiado alto, es posible que la cuota mensual no llegue a final de mes."
    assert "opciones avanzadas" not in desc_es
    
    # English
    en = load_translation("en")
    desc_en = en["config"]["step"]["update_times"]["description"]
    assert desc_en == "Indicate at what times you want it to update:\n\nATTENTION: The more update times and forecast types you enable, the more quota will be consumed. If consumption is too high, your monthly quota may run out before the end of the month."
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


def test_station_rule_translations_cover_every_options_field():
    """Ensure every supported language translates the complete rules flow."""
    strings = load_strings()["options"]
    expected_steps = {
        "init",
        "station_rules",
        "station_rule",
    }

    for language in ("ca", "en", "es"):
        options = load_translation(language)["options"]
        assert expected_steps <= set(options["step"])
        assert set(strings["error"]) == set(options["error"])
        for step_id in expected_steps:
            expected_data = set(strings["step"][step_id]["data"])
            translated_step = options["step"][step_id]
            assert expected_data == set(translated_step["data"])
            assert translated_step["title"]
            for label in translated_step["data"].values():
                assert label

    assert (
        load_translation("ca")["options"]["step"]["station_rule"]["data"][
            "parameter"
        ]
        == "Paràmetre de l’estació"
    )
    assert (
        load_translation("es")["options"]["step"]["station_rules"]["title"]
        == "Reglas de la estación"
    )


def test_binary_sensor_names_are_affirmative_phrases_in_all_languages():
    """Make binary sensor names read naturally with their on/off state."""
    expected_names = {
        "ca": {
            "freezing": "Està glaçant",
            "raining": "Està plovent",
            "windy": "Fa vent",
            "muggy": "Fa xafogor",
        },
        "en": {
            "freezing": "It is freezing",
            "raining": "It is raining",
            "windy": "It is windy",
            "muggy": "It is muggy",
        },
        "es": {
            "freezing": "Está helando",
            "raining": "Está lloviendo",
            "windy": "Hace viento",
            "muggy": "Hace bochorno",
        },
    }

    for language, names in expected_names.items():
        binary_sensors = load_translation(language)["entity"]["binary_sensor"]
        for key, name in names.items():
            assert binary_sensors[key]["name"] == name
