# Meteocat (Community Edition)

[![hacs][hacsbadge]][hacs]
[![Version](https://img.shields.io/github/v/tag/PacmanForever/meteocat_community_edition?label=version)](https://github.com/PacmanForever/meteocat_community_edition/tags)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

[![Tests](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests.yml/badge.svg)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests.yml)
[![Validate HACS](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hacs.yml/badge.svg)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hacs.yml)
[![Validate Hassfest](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hassfest.yml/badge.svg)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hassfest.yml)

![Home Assistant](https://img.shields.io/badge/home%20assistant-2024.1.0%2B-blue)

**Idiomas**: [Català](README.md) | [English](README.en.md) | **Español**

Integración **comunitaria** y **no oficial** para Home Assistant del Servicio Meteorológico de Cataluña (Meteocat).

> 📢 **Integración de la Comunidad**
>
> Esta es una integración **creada por la comunidad**, **gratuita** y de **código abierto**. No está afiliada, patrocinada ni aprobada por el Servicio Meteorológico de Cataluña.
>
> ✅ **Uso Legal y Oficial de la API**: Utiliza la [**API oficial del Meteocat**](https://apidocs.meteocat.gencat.cat/) de manera completamente legal y siguiendo sus condiciones de uso.
>
> 🎯 **Objetivo**: Facilitar la integración con Home Assistant sin necesidad de conocer el funcionamiento interno de la API. No tiene ninguna finalidad comercial ni busca obtener ningún beneficio económico.

> [!IMPORTANT]
> **Beta:** Esta integración se encuentra en fase *beta*. No se garantiza su correcto funcionamiento y puede contener errores; úsala bajo tu propia responsabilidad.
>
> **Es necesario registrarse en la API de Meteocat** para obtener una clave API:
> - 🆓 **Plan ciudadano** (gratuito)
> - 💼 **Plan empresa** (de pago)
>
> Regístrate en: https://apidocs.meteocat.gencat.cat/

## Características

- 🌡️ **Datos meteorológicos en tiempo real** de las estaciones XEMA
- 📊 **Predicciones horarias** (72 horas) y **diarias** (8 días)
- 📈 **Sensores de cuotas API** para controlar el uso
- 🏢 **Múltiples estaciones** configurables
- 🏙️ **Modo Municipio** para obtener solo predicciones (sin estación)
- 🌍 Traducciones en **catalán**, **castellano** e **inglés**

## Instalación

### Vía HACS (Recomendado)

1. Asegúrate de tener [HACS](https://hacs.xyz/) instalado
2. En HACS, ve a "Integraciones"
3. Haz clic en el menú de 3 puntos (arriba a la derecha) y selecciona "Repositorios personalizados"
4. Añade esta URL: `https://github.com/PacmanForever/meteocat_community_edition`
5. Categoría: `Integration`
6. Haz clic en "Añadir"
7. Busca "Meteocat" e instala
8. Reinicia Home Assistant

### Manual

1. Descarga la carpeta `custom_components/meteocat_community_edition`
2. Cópiala a `<config>/custom_components/meteocat_community_edition`
3. Reinicia Home Assistant

## Configuración

### Obtener una API Key

1. Regístrate en [https://apidocs.meteocat.gencat.cat/](https://apidocs.meteocat.gencat.cat/)
2. Sigue el [proceso de registro](https://apidocs.meteocat.gencat.cat/documentacio/proces-de-registre/)
3. Obtendrás una clave API única

### Añadir una estación o municipio

#### Modo Estación (con datos en tiempo real)

1. En Home Assistant, ve a **Configuración** → **Dispositivos y Servicios**
2. Haz clic en **Añadir integración**
3. Busca **Meteocat (Community Edition)**
4. Introduce tu **clave API**
5. Selecciona **"Estación XEMA"**
6. Selecciona la **comarca**
7. Selecciona la **estación meteorológica**
8. Configura las **horas de actualización** (por defecto 06:00 y 14:00)

Esto creará:
- **Entidad Weather** con datos actuales de la estación y predicciones
- **Sensores de cuotas** API
- **Sensores de horas de actualización** configuradas

#### Modo Municipio (solo predicciones)

> ⚠️ **Importante:** Este modo está pensado **exclusivamente** para usuarios que tienen una **estación meteorológica local** (personal, Netatmo, Ecowitt, etc.) y quieren complementarla con las **predicciones horarias y diarias oficiales** de Meteocat. Si no tienes ninguna estación meteorológica local, utiliza el **Modo Estación** que te proporcionará tanto datos en tiempo real como predicciones.

Este modo crea sensores con las predicciones en sus atributos, permitiéndote utilizarlas en entidades `weather.template` personalizadas que combinen datos de tu estación local con predicciones oficiales.

1. En Home Assistant, ve a **Configuración** → **Dispositivos y Servicios**
2. Haz clic en **Añadir integración**
3. Busca **Meteocat (Community Edition)**
4. Introduce tu **clave API**
5. Selecciona **"Predicción municipal"**
6. Selecciona la **comarca**
7. Selecciona el **municipio**
8. Configura las **horas de actualización** (por defecto 06:00 y 14:00)

Esto creará:
- **Sensor de predicción horaria** (72h en atributos) - Para utilizar en `weather.template`
- **Sensor de predicción diaria** (8 días en atributos) - Para utilizar en `weather.template`
- **Sensores de cuotas** API
- **Sensores de horas de actualización** configuradas

**Puedes configurar múltiples estaciones y municipios** (con diferentes API keys para incrementar los límites).

### Opciones avanzadas

Para configurar un endpoint personalizado o modificar las horas de actualización:

1. Ve a **Configuración** → **Dispositivos y Servicios**
2. Encuentra **Meteocat (Community Edition)**
3. Haz clic en los 3 puntos → **Opciones**
4. Modifica:
   - **URL base de la API** (deja el valor por defecto o vacío para producción)
   - **Horas de actualización** (formato 24h: HH:MM)

## Entidades

### Modo Estación XEMA

Para cada estación configurada se crean:

#### Weather Entity
- `weather.{estacion}_{codigo}`: Entidad principal con datos actuales y predicciones
- Ejemplo: `weather.Barcelona_ym`

#### Sensores de Cuotas
- **Peticiones disponibles Predicción**: Consumos restantes del plan Predicción
- **Peticiones disponibles XEMA**: Consumos restantes del plan XEMA
- Entity IDs: `sensor.{estacion}_{codigo}_quota_disponible_{plan}`
- Ejemplo: `sensor.Barcelona_ym_quota_disponible_prediccio`
- Atributos: límite total, peticiones utilizadas, fecha de reset

#### Sensor de Estado
- **Última actualización correcta**: Indica si la última actualización de datos ha sido exitosa.
- Entity ID: `binary_sensor.{estacion}_{codigo}_update_state`
- Estado: OFF (Correcto) / ON (Problema)

#### Sensores de Timestamps
- **Última actualización**: Timestamp de la última actualización exitosa
- **Próxima actualización**: Timestamp de la próxima actualización programada
- Entity IDs: `sensor.{estacion}_{codigo}_last_update`, `sensor.{estacion}_{codigo}_next_update`

#### Sensores de Horas de Actualización
- **Hora de actualización 1**: Muestra la primera hora configurada (solo lectura)
- **Hora de actualización 2**: Muestra la segunda hora configurada (solo lectura)
- Entity IDs: `sensor.{estacion}_{codigo}_update_time_1`, `sensor.{estacion}_{codigo}_update_time_2`
- Formato: HH:MM (24h)

#### Botón de Actualización
- **Actualizar datos**: Fuerza una actualización inmediata de todos los datos
- Entity ID: `button.{estacion}_{codigo}_refresh`
- Ejemplo: `button.Barcelona_ym_refresh`

> **Nota:** Todas las entidades se agrupan bajo un único dispositivo con nombre "{Estación} {Código}" (ej: "Barcelona YM")

### Modo Predicción Municipal

Para cada municipio configurado se crean:

#### Sensor Predicción Horaria
- **Nombre**: {Municipio} Predicción Horaria
- **Entity ID**: `sensor.{municipio}_prediccio_horaria`
- Estado: Número de horas de predicción disponibles (ej: "72 horas")
- Atributos: Datos completos de predicción horaria (72h)

#### Sensor Predicción Diaria
- **Nombre**: {Municipio} Predicción Diaria
- **Entity ID**: `sensor.{municipio}_prediccio_diaria`
- Estado: Número de días de predicción disponibles (ej: "8 días")
- Atributos: Datos completos de predicción diaria (8 días)

#### Sensores de Cuotas
- **Peticiones disponibles Predicción**: Consumos restantes del plan Predicción
- Entity IDs: `sensor.{municipio}_quota_disponible_{plan}`
- Ejemplo: `sensor.Barcelona_quota_disponible_prediccio`
- Atributos: límite total, peticiones utilizadas, fecha de reset

#### Sensor de Estado
- **Última actualización correcta**: Indica si la última actualización de datos ha sido exitosa.
- Entity ID: `binary_sensor.{municipio}_update_state`
- Estado: OFF (Correcto) / ON (Problema)

#### Sensores de Timestamps
- **Última actualización**: Timestamp de la última actualización exitosa
- **Próxima actualización**: Timestamp de la próxima actualización programada
- Entity IDs: `sensor.{municipio}_last_update`, `sensor.{municipio}_next_update`

#### Sensores de Horas de Actualización
- **Hora de actualización 1**: Muestra la primera hora configurada (solo lectura)
- **Hora de actualización 2**: Muestra la segunda hora configurada (solo lectura)
- Entity IDs: `sensor.{municipio}_update_time_1`, `sensor.{municipio}_update_time_2`
- Formato: HH:MM (24h)

#### Botón de Actualización
- **Actualizar datos**: Fuerza una actualización inmediata de todos los datos
- Entity ID: `button.{municipio}_refresh`
- Ejemplo: `button.Barcelona_refresh`

> **Nota:** Todas las entidades se agrupan bajo un único dispositivo con nombre "{Municipio}" (ej: "Barcelona")

## Actualización de datos

### 📊 Sistema de actualizaciones programadas

La integración está **optimizada para ahorrar cuota de la API** y asegurar que llegas a final de mes sin problemas.

#### Comportamiento del sistema

Los datos se actualizan **SOLO** en estos casos:

1. **Al inicio**: Cuando se enciende Home Assistant o se activa la integración (1 vez)
2. **A las horas programadas**: Por defecto a las **06:00** y **14:00** (2 veces/día)
3. **Manualmente**: Cuando pulsas el botón "Actualizar datos"

⚠️ **IMPORTANTE**: La integración **NO hace polling automático**. Esto significa que NO se actualiza cada X minutos/horas de forma continua, sino que solo lo hace en los momentos exactos configurados.

#### Consumo de cuota por actualización

Cada actualización hace las siguientes llamadas a la API:

**Modo Estación (XEMA)**:
- Primera actualización: 5 llamadas (stations + measurements + forecast + hourly + quotes)
- Actualizaciones posteriores: 4 llamadas (measurements + forecast + hourly + quotes)
- **Media diaria**: ~13 llamadas (1 inicial + 2 programadas × 4)

**Modo Municipal**:
- Cada actualización: 3 llamadas (forecast + hourly + quotes)
- **Media diaria**: ~6 llamadas (2 programadas × 3)

#### Cálculo mensual (30 días)

| Modo | Llamadas/día | Llamadas/mes | Cuota restante* | Actualizaciones manuales disponibles |
|------|-------------|--------------|-----------------|-------------------------------------|
| **Estación** | 13 | 390 | 610 | ~20/día (610÷30) |
| **Municipal** | 6 | 180 | 820 | ~27/día (820÷30) |

\* Asumiendo cuota de 1000 llamadas/mes (plan Predicción estándar)

#### Personalizar horas de actualización

Puedes modificar las horas de actualización a través de:

**Configuración** → **Dispositivos y Servicios** → (3 puntos de la integración) → **Opciones**

- **Hora de actualización 1**: Primera hora del día (formato 24h: HH:MM)
- **Hora de actualización 2**: Segunda hora del día (formato 24h: HH:MM)

Ejemplos de configuración:
- **Predeterminado**: 06:00 y 14:00
- **Noctámbulo**: 10:00 y 22:00
- **Madrugador**: 05:00 y 12:00

⚠️ **Recomendación**: Mantener 2 actualizaciones diarias. Con 3 o más actualizaciones diarias, puedes agotar la cuota antes de final de mes.

#### Botón de actualización manual

Cada entrada crea un botón **"Actualizar datos"** que te permite forzar una actualización inmediata cuando la necesites:

- No afecta a las actualizaciones programadas
- Consume cuota de la API (5 llamadas en modo Estación, 4 en modo Municipal)
- Útil para obtener datos frescos antes de un evento o viaje

## Eventos

Cada entrada de la integración dispara un **evento** (`meteocat_community_edition_data_updated`) cada vez que se actualizan los datos, tanto si es una actualización automática programada como si es manual (vía botón).

Este evento contiene la siguiente información:

- **`mode`**: Modo de la entrada (`estacio` o `municipi`)
- **`station_code`**: Código de la estación (solo en Modo Estación)
- **`municipality_code`**: Código del municipio (si está disponible)
- **`timestamp`**: Momento exacto de la actualización (ISO 8601)

### Utilizar eventos en automatizaciones

Puedes crear automatizaciones que se desencadenen cuando haya nuevos datos:

```yaml
automation:
  - alias: "Notificación cuando se actualiza Meteocat"
    trigger:
      - platform: event
        event_type: meteocat_community_edition_data_updated
        event_data:
          mode: estacio
          station_code: YM
    action:
      - service: notify.mobile_app
        data:
          message: "¡Nuevos datos meteorológicos disponibles de la estación Barcelona!"

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

También puedes escuchar el evento sin filtros para actuar con cualquier actualización:

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
            Actualización de datos completada: 
            Mode={{ trigger.event.data.mode }}, 
            Timestamp={{ trigger.event.data.timestamp }}
```

## Utilizar las predicciones municipales en una entidad Weather personalizada

> 💡 **¿Para qué sirve esta sección?** Si tienes una **estación meteorológica local** (Netatmo, Ecowitt, personal, etc.) que proporciona datos actuales pero **no tiene predicciones**, esta sección te explica cómo combinar los datos de tu estación con las predicciones oficiales de Meteocat utilizando el **Modo Municipio**.

Si has configurado el **Modo Municipio**, puedes utilizar los datos de los sensores de predicción para crear tu propia entidad Weather mediante el componente [`weather.template` de Home Assistant](https://www.home-assistant.io/integrations/weather.template/), combinando:
- **Datos actuales** de tu estación meteorológica local
- **Predicciones oficiales** de Meteocat (horarias y diarias)

### Sensores disponibles en Modo Municipio

El Modo Municipio crea estos sensores:

- **`sensor.{municipio}_prediccion_horaria`**: Predicción de las próximas 72 horas
- **`sensor.{municipio}_prediccion_diaria`**: Predicción de los próximos 8 días  
- **`sensor.{municipio}_quota_{plan}`**: Consumos API (Predicción)
- **`sensor.{municipio}_last_update`**: Última actualización
- **`sensor.{municipio}_next_update`**: Próxima actualización programada
- **`button.{municipio}_refresh`**: Botón para actualizar manualmente

### Acceder a los datos de predicción

Los sensores almacenan las predicciones completas en sus **atributos**:

#### Predicción Horaria (`sensor.{municipio}_prediccion_horaria`)

El estado del sensor muestra el número de horas disponibles (ej: "72 horas").

Atributos disponibles:
```yaml
# Acceder a todos los datos de predicción horaria
{{ state_attr('sensor.barcelona_prediccion_horaria', 'forecast') }}

# La estructura contiene:
# - dies: array de días con predicciones
#   - data: fecha del día (ej: "2025-11-24")
#   - variables: diccionario con las variables meteorológicas
#     - temp: temperatura (valores por hora)
#     - hr: humedad relativa
#     - ws: velocidad del viento
#     - wd: dirección del viento
#     - ppcp: precipitación
#     - etc.

# Ejemplo: acceder a las temperaturas de hoy
{{ state_attr('sensor.barcelona_prediccion_horaria', 'forecast').dies[0].variables.temp.valors }}
```

#### Predicción Diaria (`sensor.{municipio}_prediccion_diaria`)

El estado del sensor muestra el número de días disponibles (ej: "8 días").

Atributos disponibles:
```yaml
# Acceder a todos los datos de predicción diaria
{{ state_attr('sensor.barcelona_prediccion_diaria', 'forecast') }}

# La estructura contiene:
# - dies: array de días con predicciones
#   - data: fecha del día (ej: "2025-11-24")
#   - variables:
#     - tmax: temperatura máxima
#     - tmin: temperatura mínima
#     - ppcp: precipitación total
#     - etc.

# Ejemplo: temperatura máxima de mañana
{{ state_attr('sensor.barcelona_prediccion_diaria', 'forecast').dies[1].variables.tmax.valor }}

# Ejemplo: temperatura mínima de mañana
{{ state_attr('sensor.barcelona_prediccion_diaria', 'forecast').dies[1].variables.tmin.valor }}
```

### Ejemplo de entidad Weather personalizada
```

### Ejemplo de entidad Weather personalizada

⚠️ **Nota importante**: El componente `weather.template` requiere preprocesar los datos ya que la API de Meteocat devuelve estructuras complejas. Es más práctico utilizar **tarjetas personalizadas** o **sensores template** para mostrar las predicciones.

#### Añadir predicciones a una entidad weather local

Si tienes una estación meteorológica local y quieres añadirle las predicciones de Meteocat, puedes utilizar una entidad `weather.template`:

```yaml
weather:
  - platform: template
    name: "Casa con Predicción"
    condition_template: "{{ states('weather.mi_estacion_local') }}"
    temperature_template: "{{ state_attr('weather.mi_estacion_local', 'temperature') }}"
    humidity_template: "{{ state_attr('weather.mi_estacion_local', 'humidity') }}"
    # ... otros campos de tu estación local ...
    
    # Predicciones horarias/diarias de Meteocat
    forecast_hourly_template: "{{ state_attr('sensor.barcelona_prediccion_horaria', 'forecast_ha') }}"
    forecast_daily_template: "{{ state_attr('sensor.barcelona_prediccion_diaria', 'forecast_ha') }}"
```

> **Nota**: El atributo `forecast_ha` proporciona los datos en el formato estándar de Home Assistant, listo para ser utilizado en `weather.template`. El atributo `forecast` contiene los datos originales de la API de Meteocat.

### Crear tarjetas personalizadas

Utiliza estos datos para crear tarjetas en tu dashboard:

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## Predicción Horaria - {{ state_attr('sensor.barcelona_prediccion_horaria', 'forecast').nom }}
      
      **Disponibles:** {{ states('sensor.barcelona_prediccion_horaria') }}
      
      {% set forecast = state_attr('sensor.barcelona_prediccion_horaria', 'forecast') %}
      {% if forecast and forecast.dies %}
        {% for dia in forecast.dies[:2] %}
        ### {{ dia.data }}
        Temperatura: {{ dia.variables.temp.valors[:6] | join(', ') }}°C
        {% endfor %}
      {% endif %}

  - type: markdown
    content: |
      ## Predicción Diaria - Próximos días
      
      **Disponibles:** {{ states('sensor.Barcelona_prediccio_diaria') }}
      
      {% set forecast = state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') %}
      {% if forecast and forecast.dies %}
        {% for dia in forecast.dies[:5] %}
        **{{ dia.data }}**: {{ dia.variables.tmin.valor }}°C - {{ dia.variables.tmax.valor }}°C
        {% endfor %}
      {% endif %}
```

### Sensores template personalizados

Puedes crear sensores template para extraer datos específicos:

```yaml
template:
  - sensor:
      - name: "Temperatura actual Barcelona"
        unit_of_measurement: "°C"
        state: >
          {% set forecast = state_attr('sensor.Barcelona_prediccio_horaria', 'forecast') %}
          {% if forecast and forecast.dies %}
            {{ forecast.dies[0].variables.temp.valors[now().hour] }}
          {% else %}
            unknown
          {% endif %}
      
      - name: "Temperatura máxima mañana"
        unit_of_measurement: "°C"
        state: >
          {% set forecast = state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') %}
          {% if forecast and forecast.dies | length > 1 %}
            {{ forecast.dies[1].variables.tmax.valor }}
          {% else %}
            unknown
          {% endif %}
      
      - name: "Lluvia prevista hoy"
        unit_of_measurement: "mm"
        state: >
          {% set forecast = state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') %}
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
  - alias: "Aviso temperatura alta mañana"
    trigger:
      - platform: time
        at: "20:00:00"
    condition:
      - condition: template
        value_template: >
          {% set forecast = state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') %}
          {{ forecast.dies[1].variables.tmax.valor | float > 30 }}
    action:
      - service: notify.mobile_app
        data:
          message: "¡Mañana hará más de 30°C!"
```

### Explorar los datos

Utiliza **Developer Tools → Template** de Home Assistant para explorar la estructura completa de los datos:

```yaml
# Ver toda la estructura de predicción horaria
{{ state_attr('sensor.Barcelona_prediccio_horaria', 'forecast') }}

# Ver toda la estructura de predicción diaria
{{ state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') }}
```

> **Consejo:** Las estructuras de datos siguen exactamente el formato de la API de Meteocat. Consulta la [documentación oficial de la API](https://apidocs.meteocat.gencat.cat/) para conocer todos los campos disponibles.

## Limitaciones

### Cuotas de la API

La API de Meteocat tiene límites de peticiones que dependen del plan contratado. Consulta la [documentación oficial de Meteocat](https://apidocs.meteocat.gencat.cat/documentacio/consums/) para conocer los límites actualizados de cada plan.

Cada entrada de la integración crea **sensores de cuotas** que muestran las peticiones disponibles de los planes relevantes (Predicción y XEMA), filtrando aquellos que no se utilizan (Referencia, XDDE).

Esta integración está optimizada para minimizar el uso:
- Solo 2 actualizaciones automáticas al día (6:00 y 14:00)
- Las cuotas se consultan **después** de las otras APIs para contabilizar correctamente
- Los sensores de cuotas te permiten monitorizar el uso en tiempo real

**Consejo**: Si necesitas más peticiones, puedes crear múltiples entradas con diferentes API Keys.

### Otras limitaciones

- Las predicciones municipales dependen de la disponibilidad en la API de Meteocat
- En Modo Estación, algunas estaciones pueden no tener municipio asociado para predicciones
- Requiere conexión a Internet

## Troubleshooting

### Error "cannot_connect"
- Verifica que la clave API sea correcta
- Comprueba la conexión a Internet
- Asegúrate de que no has superado los límites de cuotas

### No se muestran predicciones
- Algunas estaciones pueden no tener municipio asociado
- Espera a la siguiente actualización programada

### Cuotas agotadas
- Añade la estación con una API Key diferente
- Espera al reset de cuotas (consultable en los sensores)

## Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork del repositorio
2. Crea una rama para tu característica
3. Haz commit de los cambios
4. Envía un Pull Request

## Licencia

Este proyecto está licenciado bajo GPL-3.0 - ver [LICENSE](LICENSE) para detalles.

## Agradecimientos

- [Servicio Meteorológico de Cataluña](https://www.meteo.cat/) por proporcionar la API
- Comunidad de Home Assistant

## Disclaimer

Esta es una integración **no oficial** creada por la comunidad para facilitar el uso de la API pública del Meteocat en Home Assistant.

- ❌ **NO** está afiliada, patrocinada ni aprobada por el Servicio Meteorológico de Cataluña
- ✅ **SÍ** utiliza la API oficial del Meteocat de manera legal y respetando sus condiciones de uso
- 💰 **Gratuita**: Proyecto de código abierto sin ánimo de lucro
- 🎯 **Propósito**: Simplificar la integración con Home Assistant sin necesidad de programar llamadas directas a la API

Para utilizar esta integración, es necesario que te registres en https://apidocs.meteocat.gencat.cat/ y obtengas tu propia clave API según las condiciones establecidas por Meteocat.

### Licencia y Garantías

Este software se distribuye bajo la **licencia GPL-3.0** (GNU General Public License v3.0):

- ✅ **Software libre**: Puedes usar, modificar y redistribuir este código
- 📖 **Código abierto**: Todo el código fuente está disponible públicamente
- 🔄 **Copyleft**: Las modificaciones deben mantener la misma licencia GPL-3.0
- ⚠️ **Sin garantías**: Este software se proporciona "TAL CUAL" (AS IS), sin ningún tipo de garantía, ni explícita ni implícita, incluyendo pero sin limitarse a las garantías de comercialización, idoneidad para un propósito particular y no infracción. En ningún caso los autores serán responsables de ninguna reclamación, daño u otra responsabilidad.

Consulta el archivo [LICENSE](LICENSE) para la licencia completa.

---

[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg
