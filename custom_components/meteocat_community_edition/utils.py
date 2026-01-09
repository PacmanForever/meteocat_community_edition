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
