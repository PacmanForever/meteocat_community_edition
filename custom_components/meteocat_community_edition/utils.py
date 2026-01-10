"""Utility functions for Meteocat (Community Edition)."""
from __future__ import annotations

import logging
import math

_LOGGER = logging.getLogger(__name__)

def calculate_utci(temp_c: float, humidity_percent: float, wind_speed_kmh: float) -> float:
    """Calculate an approximation of the Thermal Comfort Index.
    
    Since we want to avoid heavy external dependencies (pythermalcomfort) or 
    massive polynomial regression code (200+ lines), we use the:
    Australian Apparent Temperature (AAT).
    
    AT = Ta + 0.33*e - 0.70*ws - 4.00
    Where:
    - Ta: Dry bulb temperature (C)
    - e: Water vapour pressure (hPa)
    - ws: Wind speed (m/s) at 10m
    
    This provides a physically consistent "Feels Like" value that accounts for
    humidity (adds heat) and wind (removes heat), without the complexity of full UTCI.
    """
    
    # Convert wind to m/s
    wind_ms = wind_speed_kmh / 3.6
    
    try:
        # Calculate Vapour Pressure (e) in hPa
        # e = (rh / 100) * 6.105 * exp( (17.27 * Ta) / (237.7 + Ta) )
        e = (humidity_percent / 100.0) * 6.105 * math.exp((17.27 * temp_c) / (237.7 + temp_c))
        
        # Calculate AAT
        at = temp_c + 0.33 * e - 0.70 * wind_ms - 4.00
        
        return round(at, 1)
    except Exception:
        # Fallback to just temperature if calculation fails
        return temp_c

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
