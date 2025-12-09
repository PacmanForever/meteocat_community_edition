# Future Plans: Hybrid Weather Station (Estació Local)

**Date:** 2025-12-10
**Status:** Planned for next iteration

## Concept
Transform the current "Municipality Mode" into a "Local Station Mode" (Estació Local).
This mode will combine:
1.  **Meteocat Forecast**: For weather condition (icon), daily/hourly forecast.
2.  **Local Home Assistant Sensors**: For current measurements (Temperature, Humidity, Pressure, Wind, etc.).

## Implementation Details

### 1. Weather Entity (`weather.py`)
The `MeteocatWeather` entity in "Local Station Mode" will populate its attributes from user-configured entity IDs instead of XEMA API data.

**Attributes to map:**
- `temperature_template`
- `apparent_temperature_template`
- `dew_point_template`
- `humidity_template`
- `pressure_template`
- `wind_speed_template`
- `wind_bearing_template`
- `wind_gust_speed_template`
- `visibility_template`
- `ozone_template`
- `cloud_coverage_template`

### 2. Condition Logic (The "Hybrid Condition")
To avoid extra API calls or complex text mapping for the `condition` (icon):
- **Base**: Use the condition from the **Daily Forecast** (already fetched).
- **Enhancement (Optional)**: Allow mapping a binary/numeric **Rain Sensor**.
    - If Rain Sensor > 0 (or On) -> Force condition to `rainy` / `pouring`.
    - Else -> Use Meteocat Daily Forecast condition.

### 3. Configuration Flow
- Update `config_flow.py` to ask for these sensor Entity IDs when "Estació Local" is selected.
- Make these fields optional (if not provided, value is None).

## Renaming (Current Step)
- **Mode Estació** -> **Mode Estació Externa** (Uses XEMA station data).
- **Mode Municipi** -> **Mode Estació Local** (Uses Forecast + Local Sensors).
