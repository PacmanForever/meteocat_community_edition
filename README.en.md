# Meteocat (Community Edition)

[![hacs][hacsbadge]][hacs]
[![Version](https://img.shields.io/github/v/tag/PacmanForever/meteocat_community_edition?label=version)](https://github.com/PacmanForever/meteocat_community_edition/tags)
[![Stars](https://img.shields.io/github/stars/PacmanForever/meteocat_community_edition?style=social)](https://github.com/PacmanForever/meteocat_community_edition/stargazers)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

[![Unit Tests](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests_unit.yml/badge.svg)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests_unit.yml)
[![Component Tests](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests_component.yml/badge.svg)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests_component.yml)
[![Validate HACS](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hacs.yml/badge.svg)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hacs.yml)
[![Validate Hassfest](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hassfest.yml/badge.svg)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hassfest.yml)

![Home Assistant](https://img.shields.io/badge/home%20assistant-2024.1.0%2B-blue)

**Languages**: [Català](README.md) | **English** | [Español](README.es.md)

**Community-created** and **unofficial** integration for Home Assistant of the Meteorological Service of Catalonia (Meteocat).

> 📢 **Community Integration**
>
> This is a **community-created**, **free** and **open-source** integration. It is not affiliated with, sponsored by, or approved by the Meteorological Service of Catalonia.
>
> ✅ **Legal and Official API Usage**: Uses the [**official Meteocat API**](https://apidocs.meteocat.gencat.cat/) in a completely legal manner, following its terms of use.
>
> 🎯 **Purpose**: Simplify Home Assistant integration without needing to understand the internal workings of the API. It has no commercial purpose and seeks no economic benefit.

> [!IMPORTANT]
> **Beta:** This integration is currently in *beta*. Correct operation is not guaranteed and it may contain bugs; use it at your own risk
> 
> **Registration required at the Meteocat API** to obtain an API key:
> - 🆓 **Citizen plan** (free)
> - 💼 **Business plan** (paid)
>
> Register at: https://apidocs.meteocat.gencat.cat/

## Features

- 🌡️ **Real-time weather data** from XEMA stations
- 📊 **Hourly forecasts** (72 hours) and **daily forecasts** (8 days)
- 📈 **API quota sensors** to monitor usage
- 🏢 **Multiple stations** configurable
- 🏙️ **Municipality Mode** to get only forecasts (without station)
- 🌍 Translations in **Catalan**, **Spanish**, and **English**

## Installation

### Via HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. In HACS, go to "Integrations"
3. Click the 3-dot menu (top right) and select "Custom repositories"
4. Add this URL: `https://github.com/PacmanForever/meteocat_community_edition`
5. Category: `Integration`
6. Click "Add"
7. Search for "Meteocat" and install
8. Restart Home Assistant

### Manual

1. Download the `custom_components/meteocat_community_edition` folder
2. Copy it to `<config>/custom_components/meteocat_community_edition`
3. Restart Home Assistant

## Configuration

### New in the configuration flow

- **Weather condition mapping step**: In local mode, after selecting sensors, a screen appears to define how the weather condition (icon) of the Weather entity is mapped.
    - You can choose between:
        - **Automatic (Meteocat)**: The condition value is taken directly from the official Meteocat forecast.
        - **Custom**: You can manually define a mapping between your local sensor values and the conditions supported by Home Assistant (example: `{ "0": "clear-night", "1": "sunny", "2": "cloudy", "3": "rainy" }`).
    - This screen is fully translated to Catalan, Spanish, and English.

- **Mapping example**: An example mapping is provided on the screen to make configuration easier.

## Entities

- **Update buttons**: The "Refresh Measurements" and "Refresh Forecast" buttons now always show an icon.

## Advanced options

- **API URL**: When you set a test API URL, the integration uses that URL for all requests, never the real one unless configured.

## Translations

- All screens, including the new mapping step, are translated to Catalan, Spanish, and English.

## Versioning

- The current manifest version is `1.1.10` and matches the latest git tag.

## Tests

- The logic for the mapping screen, configuration, buttons, and API management is covered by automated tests.

### Get an API Key

1. Register at [https://apidocs.meteocat.gencat.cat/](https://apidocs.meteocat.gencat.cat/)
2. Follow the [registration process](https://apidocs.meteocat.gencat.cat/documentacio/proces-de-registre/)
3. You will receive a unique API key

### Add a station or municipality

#### Station Mode (with real-time data)

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Meteocat (Community Edition)**
4. Enter your **API key**
5. Select **"XEMA Station"**
6. Select the **region**
7. Select the **weather station**
8. Configure **update times** (default 06:00 and 14:00)

This will create:
- **Weather Entity** with current station data and forecasts
- **API Quota sensors**
- **Update time sensors** configured

#### Municipality Mode (without station)

> ⚠️ **Important:** This mode is designed **exclusively** for users who have a **local weather station** (Davis, Netatmo, Ecowitt, etc.) and want to complement it with **official hourly and daily forecasts** from Meteocat. If you do not have any local weather station in Home Assistant, use the **Station Mode** which will provide you with both monitoring data and forecasts.

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Meteocat (Community Edition)**
4. Enter your **API key**
5. Select **"municipal forecasts"**
6. Select the **region**
7. Select the **municipality**
8. Configure **update times** (default 06:00 and 14:00)

This will create:
- **Hourly forecast sensor** (72h in attributes)
- **Daily forecast sensor** (8 days in attributes)
- **API Quota sensors**
- **Update time sensors** configured

> **Note:** Municipality Mode is ideal if you have a local weather station and only want to add official Meteocat forecasts.

**You can configure multiple stations and municipalities** (with different API keys to increase limits).

### Advanced Options

To configure a custom endpoint or modify update times:

1. Go to **Settings** → **Devices & Services**
2. Find **Meteocat (Community Edition)**
3. Click the 3 dots → **Options**
4. Modify:
   - **API Base URL** (leave empty for production)
   - **Update times** (24h format: HH:MM)

## Entities

### External Station Mode (Meteocat measurements and forecast)

For each configured station, these entities are created:

#### Weather Entity
- `weather.{station}_{code}`: Main entity with current data and forecasts
- Example: `weather.Barcelona_ym`

#### Quota Sensors
- **Available Requests Forecast**: Remaining requests for Forecast plan
- **Available Requests XEMA**: Remaining requests for XEMA plan
- Entity IDs: `sensor.{station}_{code}_quota_disponible_{plan}`
- Example: `sensor.Barcelona_ym_quota_disponible_prediccio`
- Attributes: total limit, used requests, reset date

#### Status Sensor
- **Last update successful**: Indicates if the last data update was successful.
- Entity ID: `binary_sensor.{station}_{code}_update_state`
- State: OFF (OK) / ON (Problem)

#### Timestamp Sensors (Measurements - Hourly)
- **Last update**: Timestamp of the last successful measurement update
- **Next update**: Timestamp of the next scheduled measurement update
- Entity IDs: `sensor.{station}_{code}_last_update`, `sensor.{station}_{code}_next_update`

#### Timestamp Sensors (Forecast - Scheduled)
- **Last forecast update**: Timestamp of the last successful forecast update
- **Next forecast update**: Timestamp of the next scheduled forecast update
- Entity IDs: `sensor.{station}_{code}_last_forecast_update`, `sensor.{station}_{code}_next_forecast_update`

#### Update Time Sensors
- **Update time 1**: Shows the first configured time (read-only)
- **Update time 2**: Shows the second configured time (read-only)
- Entity IDs: `sensor.{station}_{code}_update_time_1`, `sensor.{station}_{code}_update_time_2`
- Format: HH:MM (24h)

#### Refresh Button
- **Refresh data**: Forces an immediate update of all data
- Entity ID: `button.{station}_{code}_refresh`
- Example: `button.Barcelona_ym_refresh`

> **Note:** All entities are grouped under a single device named "{Station} {Code}" (e.g., "Barcelona YM")

### Local Station Mode (Local measurements and Meteocat forecast)

This mode is designed for users who have their own weather station (Netatmo, Ecowitt, ESPHome, etc.) integrated into Home Assistant.

It allows creating a `weather` entity that combines:
1. **Current Data**: From your local sensors (Temperature, Humidity, Pressure, Wind, Rain Intensity).
2. **Forecast**: Official Meteocat forecast for your municipality.

> **Note about rain**: If you configure the **Rain Intensity** sensor, the entity will show "Rainy" state when precipitation is detected. If it's not raining, it will show the Meteocat forecast (e.g., "Sunny", "Cloudy").

For each configured municipality, these entities are created:

#### Weather Entity
- `weather.{municipality}`: Main entity. Shows current state (from your sensors) and forecast (from Meteocat).

#### Hourly Forecast Sensor
- **Name**: {Municipality} Hourly Forecast
- **Entity ID**: `sensor.{municipality}_previsio_horaria`
- State: Number of available forecast hours (e.g., "72 hours")
- Attributes: Complete hourly forecast data (72h)

#### Daily Forecast Sensor
- **Name**: {Municipality} Daily Forecast
- **Entity ID**: `sensor.{municipality}_previsio_diaria`
- State: Number of available forecast days (e.g., "8 days")
- Attributes: Complete daily forecast data (8 days)

#### Quota Sensors
- **Available Requests Forecast**: Remaining requests for Forecast plan
- Entity IDs: `sensor.{municipality}_quota_disponible_{plan}`
- Example: `sensor.Barcelona_quota_disponible_prediccio`
- Attributes: total limit, used requests, reset date

#### Status Sensor
- **Last update successful**: Indicates if the last data update was successful.
- Entity ID: `binary_sensor.{municipality}_update_state`
- State: OFF (OK) / ON (Problem)

#### Timestamp Sensors
- **Last update**: Timestamp of the last successful update
- **Next update**: Timestamp of the next scheduled update
- Entity IDs: `sensor.{municipality}_last_update`, `sensor.{municipality}_next_update`

#### Update Time Sensors
- **Update time 1**: Shows the first configured time (read-only)
- **Update time 2**: Shows the second configured time (read-only)
- Entity IDs: `sensor.{municipality}_update_time_1`, `sensor.{municipality}_update_time_2`
- Format: HH:MM (24h)

#### Refresh Button
- **Refresh data**: Forces an immediate update of all data
- Entity ID: `button.{municipality}_refresh`
- Example: `button.Barcelona_refresh`

> **Note:** All entities are grouped under a single device named "{Municipality}" (e.g., "Barcelona")

## Data Updates

### 📊 Scheduled Update System

The integration is **optimized to save API quota** and ensure you reach the end of the month without issues, while keeping station data up to date.

#### System Behavior

Data is updated as follows:

1. **Station Data (XEMA)**: Updated **every hour** (at minute 0).
2. **Forecasts and Quotes**: Updated **ONLY** at scheduled times (by default at **06:00** and **14:00**).
3. **Manually**: When you press the "Refresh data" button (updates everything).

#### Quota Consumption per Update

**Station Mode (XEMA)**:
- **Every hour**: 1 call (measurements)
- **At forecast times**: 3 additional calls (forecast + hourly + quotes)
- **Daily average**: ~30 calls (24 hours × 1 + 2 forecasts × 3)

**Local Station Mode**:
- **At forecast times**: 3 calls (forecast + hourly + quotes)
- **Daily average**: ~6 calls (2 scheduled × 3)

#### Monthly Calculation (30 days)

| Mode | Calls/day | Calls/month | Remaining quota* | Available manual updates |
|------|-----------|-------------|------------------|-------------------------|
| **Station XEMA** | ~30 | ~900 | ~100 | ~3/day (100÷30) |
| **Local Station** | ~6 | ~180 | ~820 | ~27/day (820÷30) |

\* Assuming 1000 calls/month quota (standard Predicció plan)

#### Customize Update Times

You can modify the update times through:

**Settings** → **Devices & Services** → (integration's 3 dots) → **Options**

- **Update time 1**: First time of day (24h format: HH:MM)
- **Update time 2**: Second time of day (24h format: HH:MM)

Configuration examples:
- **Default**: 06:00 and 14:00
- **Night owl**: 10:00 and 22:00
- **Early bird**: 05:00 and 12:00

⚠️ **Recommendation**: Keep 2 daily updates. With 3 or more daily updates, you may exhaust the quota before month end.

#### Manual Update Button

Each entry creates a **"Refresh data"** button that allows you to force an immediate update when needed:

- Does not affect scheduled updates
- Consumes API quota (5 calls in Station XEMA mode, 4 in Local Station mode)
- Useful to get fresh data before an event or trip

## Events

Each integration entry fires an **event** (`meteocat_community_edition_data_updated`) every time data is updated, whether it's a scheduled automatic update or manual (via button).

This event contains the following information:

- **`mode`**: Entry mode (`external` or `local`)
- **`station_code`**: Station code (only in Station Mode)
- **`municipality_code`**: Municipality code (if available)
- **`timestamp`**: Exact moment of the update (ISO 8601)

### Using events in automations

You can create automations that trigger when new data is available:

```yaml
automation:
  - alias: "Notify when Meteocat updates"
    trigger:
      - platform: event
        event_type: meteocat_community_edition_data_updated
        event_data:
          mode: external
          station_code: YM
    action:
      - service: notify.mobile_app
        data:
          message: "New weather data available from Barcelona station!"

  - alias: "Refresh dashboard with new forecasts"
    trigger:
      - platform: event
        event_type: meteocat_community_edition_data_updated
        event_data:
          mode: local
          municipality_code: "080759"
    action:
      - service: script.refresh_weather_dashboard
        data: {}
```

You can also listen for the event without filters to act on any update:

```yaml
automation:
  - alias: "Log Meteocat updates"
    trigger:
      - platform: event
        event_type: meteocat_community_edition_data_updated
    action:
      - service: logbook.log
        data:
          name: Meteocat
          message: >
            Data update completed: 
            Mode={{ trigger.event.data.mode }}, 
            Timestamp={{ trigger.event.data.timestamp }}
```

## Forecast Sensors Detail

Both in **Station XEMA Mode** and **Local Station Mode**, additional sensors are created with raw forecast data. This is useful if you want to create custom cards or advanced automations.

### Available sensors

Municipality Mode creates these sensors:

- **`sensor.{municipality}_hourly_forecast`**: Forecast for the next 72 hours
- **`sensor.{municipality}_daily_forecast`**: Forecast for the next 8 days
- **`sensor.{municipality}_quota_{plan}`**: API consumption (Forecast)
- **`sensor.{municipality}_last_update`**: Last update timestamp
- **`sensor.{municipality}_next_update`**: Next scheduled update
- **`button.{municipality}_refresh`**: Button to manually refresh

### Accessing forecast data

Sensors store complete forecasts in their **attributes**:

#### Hourly Forecast (`sensor.{municipality}_hourly_forecast`)

The sensor state shows the number of available hours (e.g., "72 hours").

Available attributes:
```yaml
# Access all hourly forecast data
{{ state_attr('sensor.barcelona_hourly_forecast', 'forecast') }}

# Structure contains:
# - dies: array of days with forecasts
#   - data: date of the day (e.g., "2025-11-24")
#   - variables: dictionary with weather variables
#     - temp: temperature (hourly values)
#     - hr: relative humidity
#     - ws: wind speed
#     - wd: wind direction
#     - ppcp: precipitation
#     - etc.

# Example: access today's temperatures
{{ state_attr('sensor.barcelona_hourly_forecast', 'forecast').dies[0].variables.temp.valors }}
```

#### Daily Forecast (`sensor.{municipality}_daily_forecast`)

The sensor state shows the number of available days (e.g., "8 days").

Available attributes:
```yaml
# Access all daily forecast data
{{ state_attr('sensor.barcelona_daily_forecast', 'forecast') }}

# Structure contains:
# - dies: array of days with forecasts
#   - data: date of the day (e.g., "2025-11-24")
#   - variables:
#     - tmax: maximum temperature
#     - tmin: minimum temperature
#     - ppcp: total precipitation
#     - etc.

# Example: tomorrow's maximum temperature
{{ state_attr('sensor.barcelona_daily_forecast', 'forecast').dies[1].variables.tmax.valor }}

# Example: tomorrow's minimum temperature
{{ state_attr('sensor.barcelona_daily_forecast', 'forecast').dies[1].variables.tmin.valor }}
```



### Create custom cards

Use this data to create cards on your dashboard:

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## Hourly Forecast - {{ state_attr('sensor.barcelona_hourly_forecast', 'forecast').nom }}
      
      **Available:** {{ states('sensor.barcelona_hourly_forecast') }}
      
      {% set forecast = state_attr('sensor.barcelona_hourly_forecast', 'forecast') %}
      {% if forecast and forecast.dies %}
        {% for dia in forecast.dies[:2] %}
        ### {{ dia.data }}
        Temperature: {{ dia.variables.temp.valors[:6] | join(', ') }}°C
        {% endfor %}
      {% endif %}

  - type: markdown
    content: |
      ## Daily Forecast - Next days
      
      **Available:** {{ states('sensor.barcelona_daily_forecast') }}
      
      {% set forecast = state_attr('sensor.barcelona_daily_forecast', 'forecast') %}
      {% if forecast and forecast.dies %}
        {% for dia in forecast.dies[:5] %}
        **{{ dia.data }}**: {{ dia.variables.tmin.valor }}°C - {{ dia.variables.tmax.valor }}°C
        {% endfor %}
      {% endif %}
```

### Custom template sensors

You can create template sensors to extract specific data:

```yaml
template:
  - sensor:
      - name: "Current Temperature Barcelona"
        unit_of_measurement: "°C"
        state: >
          {% set forecast = state_attr('sensor.Barcelona_previsio_horaria', 'forecast') %}
          {% if forecast and forecast.dies %}
            {{ forecast.dies[0].variables.temp.valors[now().hour] }}
          {% else %}
            unknown
          {% endif %}
      
      - name: "Tomorrow's Maximum Temperature"
        unit_of_measurement: "°C"
        state: >
          {% set forecast = state_attr('sensor.Barcelona_previsio_diaria', 'forecast') %}
          {% if forecast and forecast.dies | length > 1 %}
            {{ forecast.dies[1].variables.tmax.valor }}
          {% else %}
            unknown
          {% endif %}
      
      - name: "Rain Expected Today"
        unit_of_measurement: "mm"
        state: >
          {% set forecast = state_attr('sensor.Barcelona_previsio_diaria', 'forecast') %}
          {% if forecast and forecast.dies %}
            {{ forecast.dies[0].variables.ppcp.valor | default(0) }}
          {% else %}
            0
          {% endif %}
```

### Automations with forecasts

Create automations based on future forecasts:

```yaml
automation:
  - alias: "High temperature alert tomorrow"
    trigger:
      - platform: time
        at: "20:00:00"
    condition:
      - condition: template
        value_template: >
          {% set forecast = state_attr('sensor.Barcelona_previsio_diaria', 'forecast') %}
          {{ forecast.dies[1].variables.tmax.valor | float > 30 }}
    action:
      - service: notify.mobile_app
        data:
          message: "Tomorrow will be over 30°C!"
```

### Explore the data

Use Home Assistant's **Developer Tools → Template** to explore the complete data structure:

```yaml
# View complete hourly forecast structure
{{ state_attr('sensor.Barcelona_previsio_horaria', 'forecast') }}

# View complete daily forecast structure
{{ state_attr('sensor.Barcelona_previsio_diaria', 'forecast') }}
```

> **Tip:** The data structures follow exactly the Meteocat API format. Check the [official API documentation](https://apidocs.meteocat.gencat.cat/) to know all available fields.

## Limitations

### API Quotas

The Meteocat API has request limits depending on your subscribed plan. Check the [official Meteocat documentation](https://apidocs.meteocat.gencat.cat/documentacio/consums/) for updated limits for each plan.

Each integration entry creates **quota sensors** showing available requests for relevant plans (Forecast and XEMA), filtering out unused ones (Reference, XDDE).

This integration is optimized to minimize usage:
- Only 2 automatic updates per day (6:00 AM and 2:00 PM)
- Quotas are checked **after** other APIs to count correctly
- Quota sensors allow you to monitor usage in real-time

**Tip**: If you need more requests, you can create multiple entries with different API keys.

### Other limitations

- Municipality forecasts depend on availability in the Meteocat API
- In Station Mode, some stations may not have an associated municipality for forecasts
- Requires Internet connection

## Troubleshooting

### "cannot_connect" error
- Verify that the API key is correct
- Check Internet connection
- Make sure you haven't exceeded quota limits

### Forecasts not showing
- Some stations may not have an associated municipality
- Wait for the next scheduled update

### Quotas exhausted
- Add the station with a different API key
- Wait for quota reset (checkable in quota sensors)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a branch for your feature
3. Commit your changes
4. Submit a Pull Request

## License

This project is licensed under GPL-3.0 - see [LICENSE](LICENSE) for details.

## Credits

- [Meteorological Service of Catalonia](https://www.meteo.cat/) for providing the API
- Home Assistant community

## Disclaimer

This is an **unofficial** integration created by the community to facilitate the use of Meteocat's public API in Home Assistant.

- ❌ **NOT** affiliated with, sponsored by, or approved by the Meteorological Service of Catalonia
- ✅ **DOES** use the official Meteocat API legally and respecting its terms of use
- 💰 **Free**: Open-source project with no commercial purpose
- 🎯 **Purpose**: Simplify integration with Home Assistant without the need to program direct API calls

To use this integration, you must register at https://apidocs.meteocat.gencat.cat/ and obtain your own API key according to the conditions established by Meteocat.

### License and Warranties

This software is distributed under the **GPL-3.0 license** (GNU General Public License v3.0):

- ✅ **Free software**: You can use, modify and redistribute this code
- 📖 **Open source**: All source code is publicly available
- 🔄 **Copyleft**: Modifications must maintain the same GPL-3.0 license
- ⚠️ **No warranties**: This software is provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and non-infringement. In no event shall the authors be liable for any claim, damages or other liability.

See the [LICENSE](LICENSE) file for the complete license.

---

[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg


