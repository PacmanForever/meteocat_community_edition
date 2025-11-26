# Meteocat (Community Edition)

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

IntegraciÃ³n **comunitaria** y **no oficial** para Home Assistant del Servicio MeteorolÃ³gico de CataluÃ±a (Meteocat).

> ðŸ“¢ **IntegraciÃ³n de la Comunidad**
>
> Esta es una integraciÃ³n **creada por la comunidad**, **gratuita** y de **cÃ³digo abierto**. No estÃ¡ afiliada, patrocinada ni aprobada por el Servicio MeteorolÃ³gico de CataluÃ±a.
>
> âœ… **Uso Legal y Oficial de la API**: Utiliza la [**API oficial del Meteocat**](https://apidocs.meteocat.gencat.cat/) de manera completamente legal y siguiendo sus condiciones de uso.
>
> 🎯 **Objetivo**: Facilitar la integración con Home Assistant sin necesidad de conocer el funcionamiento interno de la API. No tiene ningún fin comercial ni busca obtener ningún beneficio económico.

> [!IMPORTANT]
> **Es necesario registrarse en la API de Meteocat** para obtener una clave API:
> - 🆓 **Plan ciudadano** (gratuito)
> - 💼 **Plan empresa** (de pago)
>
> Regístrate en: https://apidocs.meteocat.gencat.cat/

**Idiomas**: [Català](README.md) | [English](README.en.md) | **Español**

## CaracterÃ­sticas

- ðŸŒ¡ï¸ **Datos meteorolÃ³gicos en tiempo real** de las estaciones XEMA
- ðŸ“Š **Predicciones horarias** (72 horas) y **diarias** (8 dÃ­as)
- â˜€ï¸ **Ãndice UV** previsto
- ðŸ“ˆ **Sensores de cuotas API** para controlar el uso
- ðŸ¢ **MÃºltiples estaciones** configurables
- ðŸ™ï¸ **Modo Municipio** para obtener solo predicciones (sin estaciÃ³n)
- ðŸŒ Traducciones en **catalÃ¡n**, **castellano** e **inglÃ©s**

## InstalaciÃ³n

### VÃ­a HACS (Recomendado)

1. Asegúrate de tener [HACS](https://hacs.xyz/) instalado
2. En HACS, ve a "Integraciones"
3. Haz clic en el menú de 3 puntos (arriba a la derecha) y selecciona "Repositorios personalizados"
4. Añade esta URL: `https://github.com/PacmanForever/meteocat_community_edition`
5. Categoría: `Integration`
6. Haz clic en "AÃ±adir"
7. Busca "Meteocat" e instala
8. Reinicia Home Assistant

### Manual

1. Descarga la carpeta `custom_components/meteocat_community_edition`
2. CÃ³piala a `<config>/custom_components/meteocat_community_edition`
3. Reinicia Home Assistant

## ConfiguraciÃ³n

### Obtener una API Key

1. RegÃ­strate en [https://apidocs.meteocat.gencat.cat/](https://apidocs.meteocat.gencat.cat/)
2. Sigue el [proceso de registro](https://apidocs.meteocat.gencat.cat/documentacio/proces-de-registre/)
3. ObtendrÃ¡s una clave API Ãºnica

### AÃ±adir una estaciÃ³n o municipio

#### Modo EstaciÃ³n (con datos en tiempo real)

1. En Home Assistant, ve a **ConfiguraciÃ³n** â†’ **Dispositivos y Servicios**
2. Haz clic en **AÃ±adir integraciÃ³n**
3. Busca **Meteocat (Community Edition)**
4. Introduce tu **clave API**
5. Selecciona **"EstaciÃ³n XEMA"**
6. Selecciona la **comarca**
7. Selecciona la **estaciÃ³n meteorolÃ³gica**
8. Configura las **horas de actualizaciÃ³n** (por defecto 06:00 y 14:00)

Esto crearÃ¡:
- **Entidad Weather** con datos actuales de la estaciÃ³n y predicciones
- **Sensores de cuotas** API
- **Sensores de horas de actualizaciÃ³n** configuradas

#### Modo Municipio (sin estaciÃ³n)

1. En Home Assistant, ve a **ConfiguraciÃ³n** â†’ **Dispositivos y Servicios**
2. Haz clic en **AÃ±adir integraciÃ³n**
3. Busca **Meteocat (Community Edition)**
4. Introduce tu **clave API**
5. Selecciona **"predicciones municipales"**
6. Selecciona la **comarca**
7. Selecciona el **municipio**
8. Configura las **horas de actualizaciÃ³n** (por defecto 06:00 y 14:00)

Esto crearÃ¡:
- **Sensor de predicciÃ³n horaria** (72h en atributos)
- **Sensor de predicciÃ³n diaria** (8 dÃ­as en atributos)
- **Sensor de Ã­ndice UV**
- **Sensores de cuotas** API
- **Sensores de horas de actualizaciÃ³n** configuradas

> **Nota:** El Modo Municipio es ideal si tienes una estaciÃ³n meteorolÃ³gica local y solo quieres aÃ±adir las predicciones oficiales de Meteocat.

**Puedes configurar mÃºltiples estaciones y municipios** (con diferentes API keys para incrementar los lÃ­mites).

### Opciones avanzadas

Para configurar un endpoint personalizado o modificar las horas de actualizaciÃ³n:

1. Ve a **ConfiguraciÃ³n** â†’ **Dispositivos y Servicios**
2. Encuentra **Meteocat (Community Edition)**
3. Haz clic en los 3 puntos â†’ **Opciones**
4. Modifica:
   - **URL base de la API** (deja vacÃ­o para producciÃ³n)
   - **Horas de actualizaciÃ³n** (formato 24h: HH:MM)

## Entidades

### Modo EstaciÃ³n XEMA

Para cada estaciÃ³n configurada se crean:

#### Weather Entity
- `weather.{estacion}_{codigo}`: Entidad principal con datos actuales y predicciones
- Ejemplo: `weather.Barcelona_ym`

#### Sensores de Cuotas
- **Peticiones disponibles PredicciÃ³n**: Consumos restantes del plan PredicciÃ³n
- **Peticiones disponibles Referencia**: Consumos restantes del plan Referencia  
- **Peticiones disponibles XDDE**: Consumos restantes del plan XDDE
- **Peticiones disponibles XEMA**: Consumos restantes del plan XEMA
- Entity IDs: `sensor.{estacion}_{codigo}_quota_{plan}`
- Ejemplo: `sensor.Barcelona_ym_quota_prediccio`
- Atributos: lÃ­mite total, peticiones utilizadas, fecha de reset

#### Sensores de Timestamps
- **Ãšltima actualizaciÃ³n**: Timestamp de la Ãºltima actualizaciÃ³n exitosa
- **PrÃ³xima actualizaciÃ³n**: Timestamp de la prÃ³xima actualizaciÃ³n programada
- Entity IDs: `sensor.{estacion}_{codigo}_last_update`, `sensor.{estacion}_{codigo}_next_update`

#### Sensores de Horas de ActualizaciÃ³n
- **Hora de actualizaciÃ³n 1**: Muestra la primera hora configurada (solo lectura)
- **Hora de actualizaciÃ³n 2**: Muestra la segunda hora configurada (solo lectura)
- Entity IDs: `sensor.{estacion}_{codigo}_update_time_1`, `sensor.{estacion}_{codigo}_update_time_2`
- Formato: HH:MM (24h)

#### BotÃ³n de ActualizaciÃ³n
- **Actualizar datos**: Fuerza una actualizaciÃ³n inmediata de todos los datos
- Entity ID: `button.{estacion}_{codigo}_refresh`
- Ejemplo: `button.Barcelona_ym_refresh`

> **Nota:** Todas las entidades se agrupan bajo un Ãºnico dispositivo con nombre "{EstaciÃ³n} {CÃ³digo}" (ej: "Barcelona YM")

### Modo Predicciones Municipales

Para cada municipio configurado se crean:

#### Sensor PredicciÃ³n Horaria
- **Nombre**: {Municipio} PredicciÃ³n Horaria
- **Entity ID**: `sensor.{municipio}_prediccio_horaria`
- Estado: NÃºmero de horas de predicciÃ³n disponibles (ej: "72 horas")
- Atributos: Datos completos de predicciÃ³n horaria (72h)

#### Sensor PredicciÃ³n Diaria
- **Nombre**: {Municipio} PredicciÃ³n Diaria
- **Entity ID**: `sensor.{municipio}_prediccio_diaria`
- Estado: NÃºmero de dÃ­as de predicciÃ³n disponibles (ej: "8 dÃ­as")
- Atributos: Datos completos de predicciÃ³n diaria (8 dÃ­as)

#### Sensor PredicciÃ³n Ãndice UV
- **Nombre**: {Municipio} PredicciÃ³n Ãndice UV
- **Entity ID**: `sensor.{municipio}_prediccio_index_uv`
- Estado: NÃºmero de dÃ­as con predicciÃ³n UV disponible (ej: "3 dies")
- Atributos: Datos completos de previsiÃ³n UV (datos horarios para 3 dÃ­as)

#### Sensores de Cuotas
- **Peticiones disponibles PredicciÃ³n**: Consumos restantes del plan PredicciÃ³n
- **Peticiones disponibles Referencia**: Consumos restantes del plan Referencia  
- **Peticiones disponibles XDDE**: Consumos restantes del plan XDDE
- **Peticiones disponibles XEMA**: Consumos restantes del plan XEMA
- Entity IDs: `sensor.{municipio}_quota_{plan}`
- Ejemplo: `sensor.Barcelona_quota_prediccio`
- Atributos: lÃ­mite total, peticiones utilizadas, fecha de reset

#### Sensores de Timestamps
- **Ãšltima actualizaciÃ³n**: Timestamp de la Ãºltima actualizaciÃ³n exitosa
- **PrÃ³xima actualizaciÃ³n**: Timestamp de la prÃ³xima actualizaciÃ³n programada
- Entity IDs: `sensor.{municipio}_last_update`, `sensor.{municipio}_next_update`

#### Sensores de Horas de ActualizaciÃ³n
- **Hora de actualizaciÃ³n 1**: Muestra la primera hora configurada (solo lectura)
- **Hora de actualizaciÃ³n 2**: Muestra la segunda hora configurada (solo lectura)
- Entity IDs: `sensor.{municipio}_update_time_1`, `sensor.{municipio}_update_time_2`
- Formato: HH:MM (24h)

#### BotÃ³n de ActualizaciÃ³n
- **Actualizar datos**: Fuerza una actualizaciÃ³n inmediata de todos los datos
- Entity ID: `button.{municipio}_refresh`
- Ejemplo: `button.Barcelona_refresh`

> **Nota:** Todas las entidades se agrupan bajo un Ãºnico dispositivo con nombre "{Municipio}" (ej: "Barcelona")

## Actualización de datos

### 📊 Sistema de actualizaciones programadas

La integración está **optimizada para ahorrar cuota de la API** y asegurar que llegas a fin de mes sin problemas.

#### Comportamiento del sistema

Los datos se actualizan **SOLO** en estos casos:

1. **Al inicio**: Cuando se enciende Home Assistant o se activa la integración (1 vez)
2. **A las horas programadas**: Por defecto a las **06:00** y **14:00** (2 veces/día)
3. **Manualmente**: Cuando presionas el botón "Actualizar datos"

⚠️ **IMPORTANTE**: La integración **NO hace polling automático**. Esto significa que NO se actualiza cada X minutos/horas de forma continua, sino que solo lo hace en los momentos exactos configurados.

#### Consumo de cuota por actualización

Cada actualización realiza las siguientes llamadas a la API:

**Modo Estación (XEMA)**:
- Primera actualización: 6 llamadas (stations + measurements + forecast + hourly + uv + quotes)
- Actualizaciones posteriores: 5 llamadas (measurements + forecast + hourly + uv + quotes)
- **Media diaria**: ~16 llamadas (1 inicial + 2 programadas × 5)

**Modo Municipal**:
- Cada actualización: 4 llamadas (forecast + hourly + uv + quotes)
- **Media diaria**: ~8 llamadas (2 programadas × 4)

#### Cálculo mensual (30 días)

| Modo | Llamadas/día | Llamadas/mes | Cuota restante* | Actualizaciones manuales disponibles |
|------|--------------|--------------|-----------------|--------------------------------------|
| **Estación** | 16 | 480 | 520 | ~17/día (520÷30) |
| **Municipal** | 8 | 240 | 760 | ~25/día (760÷30) |

\* Asumiendo cuota de 1000 llamadas/mes (plan Predicció estándar)

#### Personalizar horas de actualización

Puedes modificar las horas de actualización a través de:

**Configuración** → **Dispositivos y Servicios** → (3 puntos de la integración) → **Opciones**

- **Hora de actualización 1**: Primera hora del día (formato 24h: HH:MM)
- **Hora de actualización 2**: Segunda hora del día (formato 24h: HH:MM)

Ejemplos de configuración:
- **Predeterminado**: 06:00 y 14:00
- **Noctámbulo**: 10:00 y 22:00
- **Madrugador**: 05:00 y 12:00

⚠️ **Recomendación**: Mantener 2 actualizaciones diarias. Con 3 o más actualizaciones diarias, puedes agotar la cuota antes de fin de mes.

#### Botón de actualización manual

Cada entrada crea un botón **"Actualizar datos"** que te permite forzar una actualización inmediata cuando la necesites:

- No afecta las actualizaciones programadas
- Consume cuota de la API (5 llamadas en modo Estación, 4 en modo Municipal)
- Útil para obtener datos frescos antes de un evento o viaje

## Eventos

Cada entrada de la integraciÃ³n dispara un **evento** (`meteocat_community_edition_data_updated`) cada vez que se actualizan los datos, tanto si es una actualizaciÃ³n automÃ¡tica programada como si es manual (vÃ­a botÃ³n).

Este evento contiene la siguiente informaciÃ³n:

- **`mode`**: Modo de la entrada (`estacio` o `municipi`)
- **`station_code`**: CÃ³digo de la estaciÃ³n (solo en Modo EstaciÃ³n)
- **`municipality_code`**: CÃ³digo del municipio (si estÃ¡ disponible)
- **`timestamp`**: Momento exacto de la actualizaciÃ³n (ISO 8601)

### Utilizar eventos en automatizaciones

Puedes crear automatizaciones que se desencadenen cuando haya nuevos datos:

```yaml
automation:
  - alias: "NotificaciÃ³n cuando se actualiza Meteocat"
    trigger:
      - platform: event
        event_type: meteocat_community_edition_data_updated
        event_data:
          mode: estacio
          station_code: YM
    action:
      - service: notify.mobile_app
        data:
          message: "Â¡Nuevos datos meteorolÃ³gicos disponibles de la estaciÃ³n Barcelona!"

  - alias: "Actualizar dashboard con nuevas predicciones"
    trigger:
      - platform: event
        event_type: meteocat_community_edition_data_updated
        event_data:
          mode: municipi
          municipality_code: "080759"
    action:
      - service: script.refresh_weather_dashboard
        data: {}
```

TambiÃ©n puedes escuchar el evento sin filtros para actuar con cualquier actualizaciÃ³n:

```yaml
automation:
  - alias: "Log actualizaciones Meteocat"
    trigger:
      - platform: event
        event_type: meteocat_community_edition_data_updated
    action:
      - service: logbook.log
        data:
          name: Meteocat
          message: >
            ActualizaciÃ³n de datos completada: 
            Mode={{ trigger.event.data.mode }}, 
            Timestamp={{ trigger.event.data.timestamp }}
```

## Utilizar las predicciones municipales en una entidad Weather personalizada

Si has configurado el **Modo Municipio**, puedes utilizar los datos de los sensores para crear tu propia entidad Weather mediante el componente [`template` de Home Assistant](https://www.home-assistant.io/integrations/weather.template/).

### Sensores disponibles en Modo Municipio

El Modo Municipio crea estos sensores:

- **`sensor.{municipio}_prediccio_horaria`**: PredicciÃ³n de las prÃ³ximas 72 horas
- **`sensor.{municipio}_prediccio_diaria`**: PredicciÃ³n de los prÃ³ximos 8 dÃ­as
- **`sensor.{municipio}_prediccio_index_uv`**: PredicciÃ³n de Ã­ndice UV (3 dÃ­as)
- **`sensor.{municipio}_quota_{plan}`**: Consumos API (PredicciÃ³n, Referencia, XDDE, XEMA)
- **`sensor.{municipio}_last_update`**: Ãšltima actualizaciÃ³n
- **`sensor.{municipio}_next_update`**: PrÃ³xima actualizaciÃ³n programada
- **`button.{municipio}_refresh`**: BotÃ³n para actualizar manualmente

### Acceder a los datos de predicciÃ³n

Los sensores almacenan las predicciones completas en sus **atributos**:

#### PredicciÃ³n Horaria (`sensor.{municipio}_prediccio_horaria`)

El estado del sensor muestra el nÃºmero de horas disponibles (ej: "72 horas").

Atributos disponibles:
```yaml
# Acceder a todos los datos de predicciÃ³n horaria
{{ state_attr('sensor.Barcelona_previsio_horaria', 'forecast') }}

# La estructura contiene:
# - dies: array de dÃ­as con predicciones
#   - data: fecha del dÃ­a (ej: "2025-11-24")
#   - variables: diccionario con las variables meteorolÃ³gicas
#     - temp: temperatura (valores por hora)
#     - hr: humedad relativa
#     - ws: velocidad del viento
#     - wd: direcciÃ³n del viento
#     - ppcp: precipitaciÃ³n
#     - etc.

# Ejemplo: acceder a las temperaturas de hoy
{{ state_attr('sensor.Barcelona_previsio_horaria', 'forecast').dies[0].variables.temp.valors }}
```

#### PredicciÃ³n Diaria (`sensor.{municipio}_prediccio_diaria`)

El estado del sensor muestra el nÃºmero de dÃ­as disponibles (ej: "8 dÃ­as").

Atributos disponibles:
```yaml
# Acceder a todos los datos de predicciÃ³n diaria
{{ state_attr('sensor.Barcelona_previsio_diaria', 'forecast') }}

# La estructura contiene:
# - dies: array de dÃ­as con predicciones
#   - data: fecha del dÃ­a (ej: "2025-11-24")
#   - variables:
#     - tmax: temperatura mÃ¡xima
#     - tmin: temperatura mÃ­nima
#     - ppcp: precipitaciÃ³n total
#     - etc.

# Ejemplo: temperatura mÃ¡xima de maÃ±ana
{{ state_attr('sensor.Barcelona_previsio_diaria', 'forecast').dies[1].variables.tmax.valor }}

# Ejemplo: temperatura mÃ­nima de maÃ±ana
{{ state_attr('sensor.Barcelona_previsio_diaria', 'forecast').dies[1].variables.tmin.valor }}
```

#### PredicciÃ³n Ãndice UV (`sensor.{municipio}_prediccio_index_uv`)

El estado del sensor muestra el nÃºmero de dÃ­as con predicciÃ³n UV disponible (ej: "3 dies").

Atributos disponibles:
```yaml
# Acceder a todos los datos UV
{{ state_attr('sensor.Barcelona_prediccio_index_uv', 'uv_forecast') }}

# La estructura contiene:
# - ine: cÃ³digo INE del municipio
# - nom: nombre del municipio
# - uvi: array con predicciones UV por dÃ­as (normalmente 3 dÃ­as)
#   - date: fecha (ej: "2025-11-24")
#   - hours: array de horas con valores UV
#     - hour: hora (0-23)
#     - uvi: Ã­ndice UV
#     - uvi_clouds: Ã­ndice UV con nubes

# Ejemplo: UV a las 12:00 de hoy
{% set uv_data = state_attr('sensor.Barcelona_prediccio_index_uv', 'uv_forecast') %}
{% if uv_data and uv_data.uvi %}
  {{ uv_data.uvi[0].hours | selectattr('hour', 'equalto', 12) | map(attribute='uvi') | first }}
{% endif %}

# Ejemplo: UV mÃ¡ximo de hoy
{% set uv_data = state_attr('sensor.Barcelona_prediccio_index_uv', 'uv_forecast') %}
{% if uv_data and uv_data.uvi %}
  {{ uv_data.uvi[0].hours | map(attribute='uvi') | max }}
{% endif %}
```

### Ejemplo de entidad Weather personalizada

âš ï¸ **Nota importante**: El componente `weather.template` requiere preprocesar los datos ya que la API de Meteocat devuelve estructuras complejas. Es mÃ¡s prÃ¡ctico utilizar **tarjetas personalizadas** o **sensores template** para mostrar las predicciones.

#### AÃ±adir Ã­ndice UV a una entidad weather local

Si tienes una estaciÃ³n meteorolÃ³gica local y quieres aÃ±adirle la predicciÃ³n de Ã­ndice UV de Meteocat, puedes crear un sensor template que extraiga el valor UV mÃ¡ximo:

```yaml
template:
  - sensor:
      - name: "UV Index Weather"
        unique_id: uv_index_weather
        state: >
          {% set uv_data = state_attr('sensor.Barcelona_prediccio_index_uv', 'uv_forecast') %}
          {% if uv_data and uv_data.uvi and uv_data.uvi | length > 0 %}
            {{ uv_data.uvi[0].hours | map(attribute='uvi') | max | round(0) }}
          {% else %}
            0
          {% endif %}
        unit_of_measurement: "UV"
        icon: mdi:weather-sunny-alert
```

Este sensor extrae el valor UV mÃ¡ximo del primer dÃ­a y puedes utilizarlo en una entidad `weather.template`:

```yaml
weather:
  - platform: template
    name: "Casa con UV"
    condition_template: "{{ states('weather.mi_estacion_local') }}"
    temperature_template: "{{ state_attr('weather.mi_estacion_local', 'temperature') }}"
    humidity_template: "{{ state_attr('weather.mi_estacion_local', 'humidity') }}"
    # ... otros campos de tu estaciÃ³n local ...
    
    # AÃ±adir Ã­ndice UV de Meteocat
    uv_index_template: "{{ states('sensor.uv_index_weather') }}"
    
    # Predicciones horarias/diarias de Meteocat
    forecast_hourly_template: "{{ state_attr('sensor.Barcelona_prediccio_horaria', 'forecast') }}"
    forecast_daily_template: "{{ state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') }}"
```

> **Importante**: Las predicciones de Meteocat siguen la estructura de su API, que puede no ser directamente compatible con `weather.template`. Consulta la documentaciÃ³n de [`weather.template`](https://www.home-assistant.io/integrations/weather.template/) para adaptar los datos al formato esperado.

### Crear tarjetas personalizadas

Utiliza estos datos para crear tarjetas en tu dashboard:

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## PredicciÃ³n Horaria - {{ state_attr('sensor.Barcelona_previsio_horaria', 'forecast').nom }}
      
      **Disponibles:** {{ states('sensor.Barcelona_previsio_horaria') }}
      
      {% set forecast = state_attr('sensor.Barcelona_previsio_horaria', 'forecast') %}
      {% if forecast and forecast.dies %}
        {% for dia in forecast.dies[:2] %}
        ### {{ dia.data }}
        Temperatura: {{ dia.variables.temp.valors[:6] | join(', ') }}Â°C
        {% endfor %}
      {% endif %}

  - type: markdown
    content: |
      ## PredicciÃ³n Diaria - PrÃ³ximos dÃ­as
      
      **Disponibles:** {{ states('sensor.Barcelona_previsio_diaria') }}
      
      {% set forecast = state_attr('sensor.Barcelona_previsio_diaria', 'forecast') %}
      {% if forecast and forecast.dies %}
        {% for dia in forecast.dies[:5] %}
        **{{ dia.data }}**: {{ dia.variables.tmin.valor }}Â°C - {{ dia.variables.tmax.valor }}Â°C
        {% endfor %}
      {% endif %}

  - type: markdown
    content: |
      ## PredicciÃ³n Ãndice UV
      
      **Disponibles:** {{ states('sensor.Barcelona_prediccio_index_uv') }}
      
      {% set uv = state_attr('sensor.Barcelona_prediccio_index_uv', 'uv_forecast') %}
      {% if uv and uv.uvi %}
        **UV MÃ¡ximo hoy:** {{ uv.uvi[0].hours | map(attribute='uvi') | max }}
        
        **Valores por horas:**
        {% for hour in uv.uvi[0].hours | selectattr('uvi', 'gt', 0) %}
        {{ hour.hour }}h: UV {{ hour.uvi }}
        {% endfor %}
      {% endif %}
```

### Sensores template personalizados

Puedes crear sensores template para extraer datos especÃ­ficos:

```yaml
template:
  - sensor:
      - name: "Temperatura actual Barcelona"
        unit_of_measurement: "Â°C"
        state: >
          {% set forecast = state_attr('sensor.Barcelona_previsio_horaria', 'forecast') %}
          {% if forecast and forecast.dies %}
            {{ forecast.dies[0].variables.temp.valors[now().hour] }}
          {% else %}
            unknown
          {% endif %}
      
      - name: "Temperatura mÃ¡xima maÃ±ana"
        unit_of_measurement: "Â°C"
        state: >
          {% set forecast = state_attr('sensor.Barcelona_previsio_diaria', 'forecast') %}
          {% if forecast and forecast.dies | length > 1 %}
            {{ forecast.dies[1].variables.tmax.valor }}
          {% else %}
            unknown
          {% endif %}
      
      - name: "Lluvia prevista hoy"
        unit_of_measurement: "mm"
        state: >
          {% set forecast = state_attr('sensor.Barcelona_previsio_diaria', 'forecast') %}
          {% if forecast and forecast.dies %}
            {{ forecast.dies[0].variables.ppcp.valor | default(0) }}
          {% else %}
            0
          {% endif %}
```

### Automatizaciones con predicciones

Crea automatizaciones basadas en las predicciones futuras:

```yaml
automation:
  - alias: "Aviso temperatura alta maÃ±ana"
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
          message: "Â¡MaÃ±ana harÃ¡ mÃ¡s de 30Â°C!"

  - alias: "Aviso UV alto"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: template
        value_template: >
          {% set uv_data = state_attr('sensor.Barcelona_prediccio_index_uv', 'uv_forecast') %}
          {% if uv_data and uv_data.uvi %}
            {{ uv_data.uvi[0].hours | map(attribute='uvi') | max > 6 }}
          {% else %}
            false
          {% endif %}
    action:
      - service: notify.mobile_app
        data:
          message: "Â¡Hoy el Ã­ndice UV serÃ¡ alto! ProtÃ©gete del sol."
```

### Explorar los datos

Utiliza **Developer Tools â†’ Template** de Home Assistant para explorar la estructura completa de los datos:

```yaml
# Ver toda la estructura de predicciÃ³n horaria
{{ state_attr('sensor.Barcelona_previsio_horaria', 'forecast') }}

# Ver toda la estructura de predicciÃ³n diaria
{{ state_attr('sensor.Barcelona_previsio_diaria', 'forecast') }}

# Ver toda la estructura UV
{{ state_attr('sensor.Barcelona_prediccio_index_uv', 'uv_forecast') }}
```

> **Consejo:** Las estructuras de datos siguen exactamente el formato de la API de Meteocat. Consulta la [documentaciÃ³n oficial de la API](https://apidocs.meteocat.gencat.cat/) para conocer todos los campos disponibles.

## Limitaciones

### Cuotas de la API

La API de Meteocat tiene lÃ­mites de peticiones que dependen del plan contratado. Consulta la [documentaciÃ³n oficial de Meteocat](https://apidocs.meteocat.gencat.cat/documentacio/consums/) para conocer los lÃ­mites actualizados de cada plan.

Cada entrada de la integraciÃ³n crea **sensores de cuotas** que muestran las peticiones disponibles de los cuatro planes (PredicciÃ³n, Referencia, XDDE, XEMA), independientemente del plan contratado en tu API key.

Esta integraciÃ³n estÃ¡ optimizada para minimizar el uso:
- Solo 2 actualizaciones automÃ¡ticas al dÃ­a (6:00 y 14:00)
- Las cuotas se consultan **despuÃ©s** de las otras APIs para contabilizar correctamente
- Los sensores de cuotas te permiten monitorizar el uso en tiempo real

**Consejo**: Si necesitas mÃ¡s peticiones, puedes crear mÃºltiples entradas con diferentes API Keys.

### Otras limitaciones

- Las predicciones municipales dependen de la disponibilidad en la API de Meteocat
- En Modo EstaciÃ³n, algunas estaciones pueden no tener municipio asociado para predicciones
- Requiere conexiÃ³n a Internet

## Troubleshooting

### Error "cannot_connect"
- Verifica que la clave API sea correcta
- Comprueba la conexiÃ³n a Internet
- AsegÃºrate de que no has superado los lÃ­mites de cuotas

### No se muestran predicciones
- Algunas estaciones pueden no tener municipio asociado
- Espera a la siguiente actualizaciÃ³n programada

### Cuotas agotadas
- AÃ±ade la estaciÃ³n con una API Key diferente
- Espera al reset de cuotas (consultable en los sensores)

## Contribuir

Â¡Las contribuciones son bienvenidas! Por favor:

1. Fork del repositorio
2. Crea una rama para tu caracterÃ­stica
3. Haz commit de los cambios
4. EnvÃ­a un Pull Request

## Licencia

Este proyecto estÃ¡ licenciado bajo GPL-3.0 - ver [LICENSE](LICENSE) para detalles.

## Agradecimientos

- [Servicio MeteorolÃ³gico de CataluÃ±a](https://www.meteo.cat/) por proporcionar la API
- Comunidad de Home Assistant

## Disclaimer

Esta es una integraciÃ³n **no oficial** creada por la comunidad para facilitar el uso de la API pÃºblica del Meteocat en Home Assistant.

- âŒ **NO** estÃ¡ afiliada, patrocinada ni aprobada por el Servicio MeteorolÃ³gico de CataluÃ±a
- âœ… **SÃ** utiliza la API oficial del Meteocat de manera legal y respetando sus condiciones de uso
- ðŸ’° **Gratuita**: Proyecto de cÃ³digo abierto sin Ã¡nimo de lucro
- ðŸŽ¯ **PropÃ³sito**: Simplificar la integraciÃ³n con Home Assistant sin necesidad de programar llamadas directas a la API

Para utilizar esta integraciÃ³n, debes registrarte en https://apidocs.meteocat.gencat.cat/ y obtener tu propia clave API segÃºn las condiciones establecidas por Meteocat.

### Licencia y GarantÃ­as

Este software se distribuye bajo la **licencia GPL-3.0** (GNU General Public License v3.0):

- âœ… **Software libre**: Puedes usar, modificar y redistribuir este cÃ³digo
- ðŸ“– **CÃ³digo abierto**: Todo el cÃ³digo fuente estÃ¡ disponible pÃºblicamente
- ðŸ”„ **Copyleft**: Las modificaciones deben mantener la misma licencia GPL-3.0
- âš ï¸ **Sin garantÃ­as**: Este software se proporciona "TAL CUAL" (AS IS), sin garantÃ­a de ningÃºn tipo, expresa o implÃ­cita, incluyendo pero no limitÃ¡ndose a las garantÃ­as de comercializaciÃ³n, idoneidad para un propÃ³sito particular y no infracciÃ³n. En ningÃºn caso los autores serÃ¡n responsables de ninguna reclamaciÃ³n, daÃ±o u otra responsabilidad.

Consulta el archivo [LICENSE](LICENSE) para la licencia completa.

---

[releases-shield]: https://img.shields.io/github/release/PacmanForever/meteocat_community_edition.svg
[releases]: https://github.com/PacmanForever/meteocat_community_edition/releases
[license-shield]: https://img.shields.io/github/license/PacmanForever/meteocat_community_edition.svg
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg

