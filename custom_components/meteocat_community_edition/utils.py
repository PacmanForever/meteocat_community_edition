"""Utility functions for Meteocat (Community Edition)."""
from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)

def calculate_utci(temp_c: float, humidity_percent: float, wind_speed_kmh: float) -> float:
    """Calculate UTCI (Universal Thermal Climate Index) using a simplified linear approximation.
    
    Formula provided by user:
    UTCI = Ta + (0.049 * Ta + 0.455) * (Va - 1) + (0.001 * Ta + 0.015) * (Rh - 50)
    
    Where:
    - Ta: Temperature in Celsius
    - Va: Wind speed in km/h (floored at 0.5)
    - Rh: Relative Humidity in %
    """
    
    # Floor wind speed to 0.5 km/h
    va = max(0.5, wind_speed_kmh)
    
    # Calculate UTCI
    utci = temp_c + (0.049 * temp_c + 0.455) * (va - 1) + (0.001 * temp_c + 0.015) * (humidity_percent - 50)
    
    return round(utci, 1)

def get_utci_category_key(utci_value: float) -> str:
    """Return the translation key suffix for the UTCI category."""
    if utci_value > 46:
        return "stress_extreme_heat"
    elif utci_value > 38:
        return "stress_very_strong_heat"
    elif utci_value > 32:
        return "stress_strong_heat"
    elif utci_value > 26:
        return "stress_moderate_heat"
    elif utci_value >= 9:
        return "comfort_no_stress"
    elif utci_value >= 0:
        return "stress_moderate_cold"
    elif utci_value >= -13:
        return "stress_strong_cold"
    elif utci_value >= -27:
        return "stress_very_strong_cold"
    else:
        return "stress_extreme_cold"

def get_utci_icon(utci_value: float) -> str:
    """Return the icon based on UTCI value."""
    if utci_value > 26:
        return "mdi:thermometer-alert"
    elif utci_value < 9:
        return "mdi:snowflake-alert"
    else:
        return "mdi:check-circle-outline"
