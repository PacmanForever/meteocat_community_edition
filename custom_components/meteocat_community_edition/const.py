"""Constants for the Meteocat (Community Edition) integration."""
from typing import Final

DOMAIN: Final = "meteocat_community_edition"
ATTRIBUTION: Final = "Meteocat"

# API Configuration
DEFAULT_API_BASE_URL: Final = "https://api.meteo.cat"
API_TIMEOUT: Final = 30

# Configuration
CONF_API_KEY: Final = "api_key"
CONF_MODE: Final = "mode"
CONF_STATION_CODE: Final = "station_code"
CONF_STATION_NAME: Final = "station_name"
CONF_MUNICIPALITY_CODE: Final = "municipality_code"
CONF_MUNICIPALITY_NAME: Final = "municipality_name"
CONF_COMARCA_CODE: Final = "comarca_code"
CONF_COMARCA_NAME: Final = "comarca_name"
CONF_API_BASE_URL: Final = "api_base_url"
CONF_UPDATE_TIME_1: Final = "update_time_1"
CONF_UPDATE_TIME_2: Final = "update_time_2"
CONF_UPDATE_TIME_3: Final = "update_time_3"
CONF_ENABLE_FORECAST_DAILY: Final = "enable_forecast_daily"
CONF_ENABLE_FORECAST_HOURLY: Final = "enable_forecast_hourly"

# Local Sensors Configuration
CONF_SENSOR_TEMPERATURE: Final = "sensor_temperature"
CONF_SENSOR_HUMIDITY: Final = "sensor_humidity"
CONF_SENSOR_PRESSURE: Final = "sensor_pressure"
CONF_SENSOR_WIND_SPEED: Final = "sensor_wind_speed"
CONF_SENSOR_WIND_BEARING: Final = "sensor_wind_bearing"
CONF_SENSOR_WIND_GUST: Final = "sensor_wind_gust"
CONF_SENSOR_VISIBILITY: Final = "sensor_visibility"
CONF_SENSOR_UV_INDEX: Final = "sensor_uv_index"
CONF_SENSOR_OZONE: Final = "sensor_ozone"
CONF_SENSOR_CLOUD_COVERAGE: Final = "sensor_cloud_coverage"
CONF_SENSOR_DEW_POINT: Final = "sensor_dew_point"
CONF_SENSOR_APPARENT_TEMPERATURE: Final = "sensor_apparent_temperature"
CONF_SENSOR_RAIN: Final = "sensor_rain"

# Configuration modes
MODE_EXTERNAL: Final = "external"
MODE_LOCAL: Final = "local"

# Mode labels (used in config flow)
MODE_EXTERNAL_LABEL: Final = "Estació Externa (Mesures i predicció de Meteocat)"
MODE_LOCAL_LABEL: Final = "Estació Local (Mesures locals i predicció de Meteocat)"

# Update times (defaults)
DEFAULT_UPDATE_TIME_1: Final = "06:00"
DEFAULT_UPDATE_TIME_2: Final = "14:00"
UPDATE_TIMES: Final = ["06:00", "14:00"]

# Events
EVENT_DATA_UPDATED: Final = f"{DOMAIN}_data_updated"
EVENT_NEXT_UPDATE_CHANGED: Final = f"{DOMAIN}_next_update_changed"
EVENT_ATTR_MODE: Final = "mode"
EVENT_ATTR_STATION_CODE: Final = "station_code"
EVENT_ATTR_MUNICIPALITY_CODE: Final = "municipality_code"
EVENT_ATTR_TIMESTAMP: Final = "timestamp"
EVENT_ATTR_NEXT_UPDATE: Final = "next_update"
EVENT_ATTR_PREVIOUS_UPDATE: Final = "previous_update"
EVENT_ATTR_NEXT_FORECAST_UPDATE: Final = "next_forecast_update"

# Weather condition mapping (Estat Cel -> Home Assistant condition)
METEOCAT_CONDITION_MAP: Final = {
    1: "sunny",
    2: "partlycloudy",
    3: "partlycloudy",
    4: "cloudy",
    5: "rainy",
    6: "rainy",
    7: "pouring",
    8: "lightning-rainy",
    9: "hail",
    10: "snowy",
    11: "fog",
    12: "fog",
    13: "snowy",
    20: "cloudy",
    21: "cloudy",
    22: "fog",
    23: "rainy",
    24: "lightning-rainy",
    25: "hail",
    26: "snowy",
    27: "snowy",
    28: "snowy",
    29: "snowy-rainy",
    30: "snowy-rainy",
    31: "rainy",
    32: "rainy",
}

# Variable codes for XEMA measurements
XEMA_VARIABLES: Final = {
    "temperature": 32,  # Temperatura (°C)
    "humidity": 33,  # Humitat relativa (%)
    "pressure": 34,  # Pressió atmosfèrica (hPa)
    "wind_speed": 30,  # Velocitat del vent (m/s)
    "wind_direction": 31,  # Direcció del vent (graus)
    "precipitation": 35,  # Precipitació (mm)
    "solar_radiation": 36,  # Radiació solar (W/m²)
}

# API Endpoints
ENDPOINT_XEMA_STATIONS: Final = "/xema/v1/estacions/metadades"
ENDPOINT_XEMA_MEASUREMENTS: Final = "/xema/v1/variables/mesurades"
ENDPOINT_MUNICIPALITIES: Final = "/referencia/v1/municipis"
ENDPOINT_FORECAST_MUNICIPAL: Final = "/pronostic/v1/municipal"
ENDPOINT_FORECAST_HOURLY: Final = "/pronostic/v1/municipalHoraria"
ENDPOINT_QUOTES: Final = "/quotes/v1/consum-actual"
ENDPOINT_COMARQUES: Final = "/referencia/v1/comarques"
