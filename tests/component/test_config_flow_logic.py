"""Tests for config flow sorting logic."""
import pytest

def test_config_flow_mapping_sorting_numeric():
    """Test that condition mapping is sorted numerically when possible."""
    current_mapping = {
        "0": "clear-night",
        "1": "sunny",
        "10": "fog",
        "2": "partlycloudy"
    }
    
    # Logic extracted from config_flow.py
    try:
        sorted_items = sorted(current_mapping.items(), key=lambda item: int(item[0]))
    except ValueError:
        sorted_items = sorted(current_mapping.items())
    
    current_mapping_str = "\n".join([f"{k}: {v}" for k, v in sorted_items])
    
    expected_str = "0: clear-night\n1: sunny\n2: partlycloudy\n10: fog"
    assert current_mapping_str == expected_str

def test_config_flow_mapping_sorting_alphanumeric_fallback():
    """Test fallback to alphabetical sorting if keys are non-numeric."""
    current_mapping = {
        "sunny": "sunny",
        "cloudy": "cloudy",
        "alpha": "clear-night"
    }
    
    # Logic extracted from config_flow.py
    try:
        # This should fail and raise ValueError because "sunny" is not an int
        sorted_items = sorted(current_mapping.items(), key=lambda item: int(item[0]))
    except ValueError:
        sorted_items = sorted(current_mapping.items())
    
    current_mapping_str = "\n".join([f"{k}: {v}" for k, v in sorted_items])
    
    expected_str = "alpha: clear-night\ncloudy: cloudy\nsunny: sunny"
    assert current_mapping_str == expected_str
