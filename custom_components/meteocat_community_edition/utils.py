"""Utility functions for Meteocat (Community Edition)."""
from __future__ import annotations

import logging


try:
    from pythermalcomfort.models import utci as calc_utci_func
    HAS_PYTHERMALCOMFORT = True
except ImportError:
    HAS_PYTHERMALCOMFORT = False

_LOGGER = logging.getLogger(__name__)

def calculate_utci(temp_c: float, humidity_percent: float, wind_speed_kmh: float) -> float:
    """Calculate UTCI (Universal Thermal Climate Index).
    
    Uses pythermalcomfort library if available.
    Otherwise uses Australian Apparent Temperature as a safe fallback approximation.
    """
    
    # Convert wind to m/s
    wind_ms = wind_speed_kmh / 3.6
    
    if HAS_PYTHERMALCOMFORT:
        try:
            # utci(tdb, tr, v, rh)
            # tr = temp_c (Approximation where Mean Radiant Temp = Air Temp)
            val = calc_utci_func(tdb=temp_c, tr=temp_c, v=wind_ms, rh=humidity_percent)
            return round(val, 1)
        except Exception as e:
            _LOGGER.warning("Error calculating UTCI with library: %s", e)
    
    # Fallback: Australian Apparent Temperature (Physically consistent approximation)
    # AT = Ta + 0.33*e - 0.70*ws - 4.00
    # e (hPa)
    import math
    try:
        e = (humidity_percent / 100.0) * 6.105 * math.exp((17.27 * temp_c) / (237.7 + temp_c))
        at = temp_c + 0.33 * e - 0.70 * wind_ms - 4.00
        return round(at, 1)
    except Exception:
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
