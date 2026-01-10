# Project Requirements - Meteocat Community Edition

This document outlines the specific requirements for the Meteocat Community Edition Home Assistant integration.

## Integration Overview

- **Name**: Meteocat (Community Edition)
- **Domain**: meteocat_community_edition
- **Version**: 1.2.46
- **Home Assistant**: 2024.1.0 (minimum)

## Functional Requirements

### Core Features
- Integration with Meteorological Service of Catalonia (Meteocat) API
- Real-time weather data from XEMA weather stations
- Hourly forecasts (72 hours) and daily forecasts (8 days)
- API quota monitoring sensors
- Multiple configurable weather stations
- Local Station Mode combining local sensors with official forecasts
- Manual refresh buttons for measurements and forecasts
- Multi-language support (Catalan, Spanish, English)

### Operating Modes
- **MODE_EXTERNAL (External Station Mode)**: Configuration based on XEMA weather stations with real-time measurements and forecasts
- **MODE_LOCAL (Local Station Mode)**: Configuration based on municipalities with forecasts combined with local sensor data

### API Integration
- **API Endpoint**: https://api.meteo.cat/ (official Meteocat API)
- **Authentication**: API key (citizen or enterprise plan)
- **Rate Limits**: Different limits per plan (citizen: 1000 requests/day, enterprise: higher)
- **Data Format**: JSON
- **Error Handling**: 401/403 (authentication), 429 (rate limit), network errors

### Data Collection
- **Update Frequency**: Hourly for measurements, scheduled for forecasts (configurable times)
- **Real-time Updates**: Measurements updated hourly, forecasts on schedule
- **Historical Data**: Not supported (only current and forecast data)
- **Caching**: Station data cached in entry.data, API quota data cached
- **Data Mapping**:
  - Meteorological conditions are mapped from Meteocat numeric codes to Home Assistant string states.
  - Unknown or unmapped condition codes default to `exceptional` to alert the user of an unusual state.

## Technical Requirements

### Dependencies
- **Required Packages**: aiohttp>=3.9.0
- **Python Version**: 3.11+ (tested on 3.11, 3.12)
- **Platform Requirements**: Linux (HA requirement)

### Configuration
- **Required Parameters**: API key, operation mode, region selection, station/municipality
- **Optional Parameters**: Forecast times (up to 3 daily), API base URL for testing
- **Validation**: API key verification, station/municipality existence
- **Security**: API key stored encrypted in HA config

### Entities and Platforms
- **Sensors**: Location coordinates, geographic context, API quotas, timestamps, update hours
- **Binary Sensors**: Update status (diagnostic), API quota monitoring
- **Buttons**: Manual refresh buttons for measurements and forecasts
- **Weather**: Main weather entity with current conditions and forecasts
- **Device Classes**: Various HA device classes for sensors
- **Events**: meteocat_community_edition_data_updated, meteocat_community_edition_next_update_changed
- **Device Triggers**: data_updated, next_update_changed triggers for automations

## Quality Requirements

### Testing
- **Coverage Target**: >95%
- **Unit Tests**: API client, config flow, coordinator, sensors, error handling
- **Component Tests**: Full integration tests with HA environment
- **Edge Cases**: Quota exhausted, network errors, API authentication failures

### Performance
- **Memory Usage**: Minimal (API data caching)
- **CPU Usage**: Low (scheduled updates, not continuous polling)
- **Network Usage**: ~24-27 API calls per day depending on mode

### Compatibility
- **HA Versions**: 2024.1.0+
- **Python Versions**: 3.11, 3.12
- **Platforms**: Linux-based systems (HA compatible)

## Security Requirements

- **API Key Handling**: Encrypted storage in HA config, re-authentication flow for expired keys
- **Data Privacy**: Only weather data stored, no personal user information
- **Network Security**: HTTPS only, certificate validation
- **Error Messages**: No sensitive information exposed in logs or UI

## Deployment Requirements

### HACS Integration
- **Category**: integration
- **Content Root**: false
- **Supported Countries**: ES (Spain)
- **README Rendering**: true

### Release Process
- **Versioning**: Semantic versioning (1.2.46)
- **Changelog**: Detailed release notes in CHANGELOG.md
- **Breaking Changes**: Documented in changelog with migration notes

## Maintenance Requirements

### Monitoring
- **Health Checks**: Binary sensor for update status, API quota sensors
- **Error Reporting**: Comprehensive logging, user-friendly error messages
- **Performance Monitoring**: API call counters, update success rates

### Updates
- **API Changes**: Monitor Meteocat API documentation for changes
- **HA Compatibility**: Test against new HA versions, update minimum version if needed
- **Dependency Updates**: Regular updates of aiohttp and other dependencies

### Internationalization
- **Supported Languages**: Catalan (ca.json), Spanish (es.json), English (en.json)
- **Translation Coverage**: Complete coverage of config flow, errors, sensor names, UI elements

---

**Last Updated**: December 2025
**Maintained by**: Project maintainers
**Related Documents**:
- `.ai_instructions.md`: AI assistant guidelines
- `docs/HA_HACS_Integration_Creation_Guide.md`: Setup guide

## Detailed Functional Specifications

### Operating Modes

#### MODE_EXTERNAL (External Station Mode)
- Configuration based on XEMA weather stations
- Selection by region and station
- Access to real-time measurements and forecasts from the station
- **Weather Entity**: Creates a weather entity with station data and forecasts

#### MODE_LOCAL (Local Station Mode)
- Configuration based on municipalities
- Selection by region and municipality
- Access to hourly and daily forecasts
- **Weather Entity**: Creates a weather entity combining local sensor data with Meteocat forecasts

### Sensors - MODE_EXTERNAL

#### Location Sensors
- **Station Latitude**: Geographic coordinate (degrees)
- **Station Longitude**: Geographic coordinate (degrees)
- **Station Altitude**: Altitude in meters

#### Geographic Context Sensors
- **Region**: Region where the station is located (always available)
- **Municipality**: Station municipality (if available in API)
- **Province**: Station province (if available in API)

#### API Quota Sensors
- **Available requests per plan**: Shows remaining consumption
  - Forecast
  - Reference
  - XDDE
  - XEMA

#### Timestamp Sensors (Measurements - Hourly)
- **Last Update**: Timestamp of last successful measurement update
  - Data source: `coordinator.last_successful_update_time`
- **Next Update**: Timestamp of next scheduled measurement update
  - Data source: `coordinator.next_scheduled_update`
  - Automatically updated when next update is scheduled
- All timestamp sensors are Diagnostic category

#### Timestamp Sensors (Forecast - Scheduled)
- **Last Forecast Update**: Timestamp of last successful forecast update
  - Data source: `coordinator.last_forecast_update`
- **Next Forecast Update**: Timestamp of next scheduled forecast update
  - Data source: `coordinator.next_forecast_update`
  - Automatically updated when next update is scheduled
- All forecast timestamp sensors are Diagnostic category

#### Update Hours Sensors
- **Update Hour 1**: First configured forecast update time
- **Update Hour 2**: Second configured forecast update time
- All sensors are Diagnostic category

#### Status Sensor
- **Last Successful Update**: Binary sensor for diagnostic update status
  - Category: Diagnostic
  - Device class: Problem
  - Logic: ON = problem detected (last update failed or missing data), OFF = no problems (successful update with data)
  - Intelligent detection:
    - Detects exhausted quotas (when update_success=True but no data)
    - Detects network/API errors
    - Respects granular configuration (only alerts if enabled data is missing)
    - Specific error messages in attributes
  - Always available (reports errors even when coordinator fails)

### Buttons - Manual Refresh

#### Refresh Measurements Button (MODE_EXTERNAL only)
- **Purpose**: Manually trigger measurement data refresh outside scheduled updates
- **Entity ID**: `button.{station_name}_{station_code}_refresh_measurements`
- **Icon**: mdi:refresh
- **Availability**: Always available (allows manual refresh even if API is down)
- **Function**: Calls `coordinator.async_refresh_measurements()` to update real-time station data

#### Refresh Forecast Button (MODE_EXTERNAL and MODE_LOCAL)
- **Purpose**: Manually trigger forecast data refresh outside scheduled updates
- **Entity ID**: 
  - MODE_EXTERNAL: `button.{station_name}_{station_code}_refresh_forecast`
  - MODE_LOCAL: `button.{municipality_name}_refresh_forecast`
- **Icon**: mdi:refresh
- **Availability**: Always available (allows manual refresh even if API is down)
- **Function**: Calls `coordinator.async_refresh_forecast()` to update forecast data

#### Button Behavior
- **Quota Consumption**: Buttons consume API quota when pressed (same as scheduled updates)
- **Error Handling**: Buttons work even when coordinator has errors
- **Device Grouping**: Buttons are grouped with other entities under the same device
- **Translation**: Buttons use translation keys for multi-language support

### Sensors - MODE_LOCAL

#### Weather Entity
- **Weather**: Main entity combining local sensor data (temperature, humidity, etc.) with Meteocat forecasts

#### Forecast Sensors
- **Hourly Forecast**: 72 hours forecast with complete data in attributes (if enabled)
- **Daily Forecast**: 8 days forecast with complete data in attributes (if enabled)

#### Geographic Context Sensors
- **Municipality**: Municipality name (always available)
- **Region**: Municipality region (always available)
- **Municipality Latitude**: Geographic coordinate (if available in API)
- **Municipality Longitude**: Geographic coordinate (if available in API)
- **Province**: Municipality province (if available in API)

#### UTCI Sensors (Universal Thermal Climate Index)
- **Numeric UTCI Index**: Calculates thermal sensation based on temp, humidity, and wind.
  - Formula: Linear approximation
  - Input: Temp (°C), Humidity (%), Wind (km/h)
- **Literal UTCI Status**: Text description and icon based on UTCI value.
  - Categories: 9 ranges from Extreme Heat to Extreme Cold
  - Visual indicators: Check icon for comfort, Alert/Snowflake/Thermometer for stress.

#### API Quota Sensors
- Same as MODE_EXTERNAL

#### Timestamp Sensors
- Same as MODE_EXTERNAL

#### Status Sensor
- **Last Successful Update**: Binary sensor for diagnostic update status
  - Category: Diagnostic
  - Device class: Problem
  - Logic: ON = problem detected (last update failed or missing data), OFF = no problems (successful update with data)
  - Intelligent detection:
    - Detects exhausted quotas (when update_success=True but no data)
    - Detects network/API errors
    - Respects granular configuration (only alerts if enabled data is missing)
    - Specific error messages in attributes
  - Always available (reports errors even when coordinator fails)

### API Quota Management

#### Scheduled Updates System
- **Station Data (XEMA)**: Hourly update (every hour at minute 0)
- **Forecasts and Quotas**: Scheduled update (default 06:00 and 14:00)
- **NO continuous automatic polling**: update_interval=None, own scheduling management

#### Estimated Quota Consumption
- **MODE_EXTERNAL**:
  - 24 calls/day for measurements (1 per hour)
  - 3 additional calls per scheduled update (forecast + hourly + quotas)
- **MODE_LOCAL**:
  - 3 calls per scheduled update (forecast + hourly + quotas)
  - No hourly consumption
- **Separate quotas** per API plan

#### Intelligent Retry System
- Automatic retries for temporary errors (timeout, rate limit)
- **NO** extra quota consumption: quotas only checked during scheduled updates
- Retry at 60 seconds after temporary error
- Maximum 3 retries per request

#### Quota Optimization
- **Station Data Persistence**: station_data cached in entry.data
  - Saves 1 get_stations() call per HA restart
  - **Atomic persistence optimization**: Update entry.data atomically to avoid race conditions and ensure data is saved correctly, avoiding unnecessary calls in subsequent updates
- **Configuration Data**: Municipality, region, province names saved during config_flow
  - NO API calls required during execution
- **Coordinates**: Saved during initial configuration
  - MODE_EXTERNAL: station coordinates
  - MODE_LOCAL: municipality coordinates (if available)
- **Update Scheduling**: `next_scheduled_update` property in coordinator
  - Allows sensor to show next update without additional calculations
  - Automatically updated when each update is scheduled
- **Quota-exhausted Setup Tolerance**: During initial configuration
  - If quotas are exhausted, integration configures anyway
  - Data will be obtained in next scheduled update
  - Avoids "Configuration failed" errors for temporary quota limits

### Custom Events

#### Event: meteocat_community_edition_data_updated
Fired when data is successfully updated.

**Attributes**:
- `mode`: MODE_EXTERNAL or MODE_LOCAL
- `station_code`: Station code (if MODE_EXTERNAL)
- `municipality_code`: Municipality code
- `timestamp`: Update timestamp
- `previous_update`: Previous update timestamp
- `next_update`: Next update timestamp

#### Event: meteocat_community_edition_next_update_changed
Fired when next scheduled update changes.

**Attributes**:
- Same as previous event

### Device Triggers

#### Trigger: data_updated
- Activates when new data is received
- Allows automations based on data updates

#### Trigger: next_update_changed
- Activates when the next scheduled update time changes
- Allows automations to react to scheduling changes

### Configuration

#### Configuration Flow (config_flow)
1. **API Key**: Access key for Meteocat API
2. **Input Type**: Selection MODE_EXTERNAL or MODE_LOCAL
3. **Region**: Region selection
4. **Station/Municipality**: Selection according to mode
5. **Data Configuration**: Selection of daily and/or hourly forecast
6. **Update Hours**: Configuration of up to 3 daily hours (HH:MM format)

#### Data Saved in entry.data
**MODE_EXTERNAL**:
- api_key, mode, station_code, station_name
- region_code, region_name
- update_time_1, update_time_2, update_time_3
- enable_forecast_daily, enable_forecast_hourly
- station_municipality_code, station_municipality_name (if available)
- station_province_code, station_province_name (if available)
- _station_data (coordinates and altitude cache)

**MODE_LOCAL**:
- api_key, mode, municipality_code, municipality_name
- region_code, region_name
- update_time_1, update_time_2, update_time_3
- enable_forecast_daily, enable_forecast_hourly
- municipality_lat, municipality_lon (if available)
- province_code, province_name (if available)

#### Configurable Options
- **API Base URL**: API URL (optional, defaults to production)

### Re-authentication

#### Authentication Error Management
- Automatic detection of 401/403 errors
- Marks integration as "reauth required"
- Re-authentication flow to update API key
- Keeps rest of configuration intact

### HACS and Home Assistant Validations

#### HACS
- ✅ hacs.json validation
- ✅ Valid fields: name, content_in_root, country, render_readme, homeassistant
- ✅ NO: iot_class (only in manifest.json)

#### Hassfest
- ✅ manifest.json validation
- ✅ Valid fields for custom components
- ✅ NO: homeassistant field (only for core integrations)

### Testing

#### Test Coverage
- **Coverage**: >95%
- **Total tests**: >195 tests (verified with pytest)

#### Covered Areas
- API client (requests, errors, retry logic)
- Config flow (all steps, validations, errors)
- Coordinator (scheduled updates, retry, quota, granular configuration)
- Sensors (all types, values, attributes)
- Sensor setup (conditional sensor creation)
- Binary sensors (update status, diagnostic, ALL API calls detection)
- Binary sensor: Verification of ALL API calls according to mode and configuration
  - MODE_EXTERNAL: measurements (mandatory), forecast/forecast_hourly (if municipality_code exists and enabled)
  - MODE_LOCAL: forecast, forecast_hourly (if enabled)
- Coordinate sensors: Reading entry.data._station_data when coordinator.data empty (quota exhausted)
- Weather entity (MODE_EXTERNAL - all properties)
- Buttons (manual refresh for measurements and forecasts)
- Custom events (data_updated, next_update_changed)
- Device triggers (data_updated, next_update_changed)
- Re-authentication (flow without restart)
- Data persistence (station_data, entry.data)
- Device grouping (shared identifiers)
- Setup with exhausted quotas (tolerance during initial configuration)
- Next scheduled update (sensor shows correct time)
- Retry logic (temporary errors, quota preservation)

#### GitHub Actions
- **tests.yml**: Runs all tests on Python 3.11 and 3.12
- **validate_hacs.yml**: HACS validation
- **validate_hassfest.yml**: manifest.json validation

### Code Quality

#### Documentation
- Docstrings in all modules, classes, and functions
- Critical comments for complex logic
- Complete README with examples

#### Structure
- Clear separation of responsibilities
- API client separate from coordinator
- Modular config flow
- Centralized constants

#### Error Management
- Try-except with appropriate logging
- Specific errors (MeteocatAPIError, MeteocatAuthError)
- Fallbacks for optional data
- Input validations

### Compatibility

#### Home Assistant
- Minimum version: 2024.1.0 (specified in hacs.json)
- Compatible with modern HA architecture

#### Python
- Python 3.11+
- Python 3.12+ (tested)

#### HACS
- Compatible with custom repository structure
- Installation via HACS custom repositories


