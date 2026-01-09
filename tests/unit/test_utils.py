"""Tests for utility functions."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from custom_components.meteocat_community_edition.utils import (
    calculate_utci,
    get_utci_category_key,
    get_utci_icon,
)

def test_calculate_utci():
    """Test UTCI calculation."""
    # Test case 1: Normal conditions
    # T=20, H=50, V=10
    # UTCI approx = 20 + (0.049*20 + 0.455)*(9) + (0.001*20 + 0.015)*(0) = 20 + 1.435*9 = 20 + 12.915 = 32.9
    assert calculate_utci(20, 50, 10) == 32.9
    
    # Test case 2: Zero wind (clamped to 0.5)
    # T=20, H=50, V=0 -> V=0.5
    # UTCI = 20 + (1.435)*(-0.5) = 20 - 0.7175 = 19.3
    assert calculate_utci(20, 50, 0) == 19.3

def test_get_utci_category_key_ranges():
    """Test all UTCI category ranges."""
    assert get_utci_category_key(50) == "stress_extreme_heat"      # > 46
    assert get_utci_category_key(46.1) == "stress_extreme_heat"
    
    assert get_utci_category_key(46) == "stress_very_strong_heat"  # > 38 and <= 46
    assert get_utci_category_key(39) == "stress_very_strong_heat"
    assert get_utci_category_key(38.1) == "stress_very_strong_heat"
    
    assert get_utci_category_key(38) == "stress_strong_heat"       # > 32 and <= 38
    assert get_utci_category_key(33) == "stress_strong_heat"
    
    assert get_utci_category_key(32) == "stress_moderate_heat"     # > 26 and <= 32
    assert get_utci_category_key(27) == "stress_moderate_heat"
    
    assert get_utci_category_key(26) == "comfort_no_stress"        # >= 9 and <= 26
    assert get_utci_category_key(9) == "comfort_no_stress"
    
    assert get_utci_category_key(8.9) == "stress_moderate_cold"    # >= 0 and < 9
    assert get_utci_category_key(0) == "stress_moderate_cold"
    
    assert get_utci_category_key(-0.1) == "stress_strong_cold"     # >= -13 and < 0
    assert get_utci_category_key(-13) == "stress_strong_cold"
    
    assert get_utci_category_key(-13.1) == "stress_very_strong_cold" # >= -27 and < -13
    assert get_utci_category_key(-27) == "stress_very_strong_cold"
    
    assert get_utci_category_key(-27.1) == "stress_extreme_cold"   # < -27
    assert get_utci_category_key(-30) == "stress_extreme_cold"

def test_get_utci_icon_coverage():
    """Test icon generation for coverage if logic exists."""
    # Assuming get_utci_icon mirrors logic or has ranges
    assert get_utci_icon(30) is not None
