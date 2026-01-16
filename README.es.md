# Meteocat (Community Edition)

[![hacs][hacsbadge]][hacs]
[![Version](https://img.shields.io/github/v/tag/PacmanForever/meteocat_community_edition?label=version)](https://github.com/PacmanForever/meteocat_community_edition/tags)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

[![Unit Tests](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests_unit.yml/badge.svg?branch=main)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests_unit.yml)
[![Component Tests](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests_component.yml/badge.svg?branch=main)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests_component.yml)
[![Validate HACS](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hacs.yml/badge.svg?branch=main)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hacs.yml)
[![Validate Hassfest](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hassfest.yml/badge.svg?branch=main)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hassfest.yml)

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
> **Es necesario registrarse en la API de Meteocat** para obtener una clave API:
> - 🆓 **Plan ciudadano** (gratuito)
> - 💼 **Plan empresa** (de pago)
>
> Regístrate en: https://apidocs.meteocat.gencat.cat/

## Características

- 🌡️ **Datos meteorológicos actualizados** de las estaciones XEMA
- 📊 **Predicciones horarias** (72 horas) y **diarias** (8 días)
- 📈 **Sensores de cuotas API** para controlar el uso
- 🏢 **Múltiples estaciones** configurables
- 🏙️ **Modo Estación Local** para combinar datos locales con predicciones oficiales
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

### Novedades en el flujo de configuración

- **Paso de mapeo de condición climática**: En modo local, después de seleccionar los sensores, aparece una pantalla para definir cómo se mapea la condición climática (icono) de la entidad Weather.
    - Puedes elegir entre:
        - **Automático (Meteocat)**: El valor de condición se toma directamente de la predicción oficial de Meteocat.
        - **Personalizado**: Puedes definir un mapeo manual entre los valores del sensor local y las condiciones soportadas por Home Assistant (ejemplo: `{ "0": "clear-night", "1": "sunny", "2": "cloudy", "3": "rainy" }`).
    - Esta pantalla está completamente traducida al catalán, español e inglés.

- **Ejemplo de mapeo**: Se ofrece un ejemplo de mapeo en la pantalla para facilitar la configuración.

## Entidades

- **Botones de actualización**: Los botones "Actualizar Medidas" y "Actualizar Predicción" ahora siempre muestran un icono.

## Opciones avanzadas

- **URL de la API**: Cuando configuras una URL de pruebas, la integración utiliza esa URL para todas las llamadas, nunca la real si no está configurada.

## Traducciones

- Todas las pantallas, incluido el nuevo paso de mapeo, están traducidas al catalán, español e inglés.

## Versionado

- La versión actual del manifest es `1.2.89` y coincide con el último tag de git.

## Tests

- La lógica de la pantalla de mapeo, la configuración, los botones y la gestión de la API están cubiertos por tests automáticos.

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

#### Modo Estación Local (Medidas locales y predicción de Meteocat)

> ⚠️ **Importante:** Este modo está pensado **exclusivamente** para usuarios que tienen una **estación meteorológica local** (Davis, Netatmo, Ecowitt, etc.) y quieren complementarla con las **predicciones horarias y diarias oficiales** de Meteocat. Si no tienes ninguna estación meteorológica local en Home Assistant, usa el **Modo Estación** que te proporcionará tanto datos de monitorización como de predicciones.

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

### Configuración del mapeo de condiciones climáticas (Modo Estación Local)

En **Modo Estación Local**, puedes personalizar cómo se determina la **condición climática** (el icono que se muestra en la tarjeta del tiempo) de la entidad `weather`.

#### Tipos de mapeo disponibles

1. **Automático (Meteocat)** *(por defecto)*
   - La condición se toma directamente de la predicción oficial de Meteocat
   - No requiere configuración adicional
   - Siempre muestra una condición válida basada en datos oficiales

2. **Personalizado**
   - Define tu propio mapeo entre valores de tu sensor local y condiciones de Home Assistant
   - Útil cuando tienes sensores que reportan valores numéricos (0, 1, 2...) que representan condiciones
   - Permite integrar sensores personalizados (ESPHome, etc.) con lógica propia

#### Cómo configurar el mapeo personalizado

##### Primera configuración (durante la creación)

Cuando configuras una nueva estación local:

1. Selecciona **"Predicción municipal"**
2. Selecciona la **comarca** y **municipio**
3. En la pantalla **"Tipo de mapeo de la condición climática"**, selecciona **"Personalizado"**
4. **Selecciona el sensor** que contiene el valor de condición (obligatorio)
5. **Configura el mapeo** para cada condición:
   - Aparecerá un formulario con todas las condiciones meteorológicas soportadas por Home Assistant (Sunny, Cloudy, Rainy, etc.).
   - Para cada condición, introduce el valor (o valores) que devuelve tu sensor cuando se da esta condición.
   - Si tu sensor devuelve varios valores para una misma condición, sepáralos por comas (ejemplo: `1, 2` o `soleado, despejado`).
   - Los campos se pueden dejar vacíos si tu sensor no soporta algunas condiciones.

> ℹ️ Las condiciones disponibles corresponden a los [valores estándar de Home Assistant](https://developers.home-assistant.io/docs/core/entity/weather/#weather-conditions).

##### Editar mapeo existente

Para modificar el mapeo de una estación ya configurada:

1. Ve a **Configuración** → **Dispositivos y Servicios**
2. Encuentra tu integración **Meteocat (Community Edition)**
3. Haz clic en los 3 puntos → **Opciones**
4. En **"Tipo de mapeo de la condición climática"**, cambia entre **"Meteocat"** o **"Personalizado"**
5. Si seleccionas **"Personalizado"**, aparecerá la pantalla de configuración del mapeo
6. Modifica el **sensor** y/o el **mapeo** según sea necesario

> **💡 Consejo**: Cuando editas un mapeo existente, la edición termina directamente sin volver a los sensores, ya que ya está todo configurado.

#### Formato del mapeo personalizado

En la pantalla de configuración, aparecerá un formulario con un campo para cada condición climática soportada por Home Assistant.

- **Campos**: Cada campo corresponde a una condición (ej: soleado, lluvioso, etc.).
- **Valores**: Introduce el valor numérico (o texto) que tu sensor local envía para esa condición.
- **Múltiples valores**: Si tu sensor envía diferentes valores para una misma condición, sepáralos por comas (ej: `1, 2`).
- **Valores vacíos**: Deja el campo vacío si tu sensor no soporta esa condición.

**Ejemplo de configuración**:
Si tu sensor devuelve `0` para "Claro (noche)" y `1` para "Soleado":
- Campo **clear-night**: `0`
- Campo **sunny**: `1`
- Campo **partlycloudy**: `2`
- Campo **cloudy**: `3`
- Campo **rainy**: `4`
- ...

#### Comportamiento cuando no se puede determinar la condición

Si el valor del sensor no tiene una correspondencia en el mapeo, o si hay algún error:

- **La tarjeta del tiempo muestra**: "unknown" con icono genérico (blanco y negro)
- **Esto es el comportamiento correcto** e indica que hay que revisar la configuración del mapeo
- **No se muestra ningún icono de color** para evitar mostrar información incorrecta

#### Cambiar entre tipos de mapeo

Puedes cambiar libremente entre **"Meteocat"** y **"Personalizado"** en cualquier momento:

- **De Meteocat a Personalizado**: Aparece la pantalla de configuración del mapeo
- **De Personalizado a Meteocat**: Se eliminan los datos de mapeo personalizado y se vuelve al comportamiento por defecto

## Entidades

### Modo Estación Externa (Medidas y predicción de Meteocat)

Para cada estación configurada se crean:

#### Weather Entity
- `weather.{estacion}_{codigo}`: Entidad principal con datos actuales y predicciones
- Ejemplo: `weather.Barcelona_ym`

#### Sensor de Precipitación
- **Precipitación diaria**: Precipitación diaria acumulada (mm) (Si la estación dispone de ella)
- Entity ID: `sensor.{estacion}_{codigo}_precipitation`

#### Sensor UTCI (Sensación térmica)
- **Temperatura UTCI**: Calcula la sensación térmica basada en temperatura, humedad y viento (si están disponibles).
- Entity ID: `sensor.{estacion}_{codigo}_utci_index`
- **Estado de Confort Térmico**: Texto e icono que indica el nivel de estrés térmico basado en el UTCI.
- Entity ID: `sensor.{estacion}_{codigo}_utci_literal`

#### Sensores Beaufort (Nuevo v1.2.82)
- **Índice Beaufort**: Número (0-17) que indica la fuerza del viento.
- Entity ID: `sensor.{estacion}_{codigo}_beaufort_index`
- **Descripción Beaufort**: Texto descriptivo de la fuerza del viento.
- Entity ID: `sensor.{estacion}_{codigo}_beaufort_description`
- *Nota: Solo aparecen si la estación tiene datos de viento.*

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

#### Sensores de Timestamps (Mediciones - Horarias)
- **Última actualización**: Timestamp de la última actualización de mediciones exitosa
- **Próxima actualización**: Timestamp de la próxima actualización de mediciones programada
- Entity IDs: `sensor.{estacion}_{codigo}_last_update`, `sensor.{estacion}_{codigo}_next_update`

#### Sensores de Timestamps (Predicción - Programadas)
- **Última actualización predicción**: Timestamp de la última actualización de predicción exitosa
- **Próxima actualización predicción**: Timestamp de la próxima actualización de predicción programada
- Entity IDs: `sensor.{estacion}_{codigo}_last_forecast_update`, `sensor.{estacion}_{codigo}_next_forecast_update`

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

### Modo Estación Local (Medidas locales y predicción de Meteocat)

Este modo está pensado para usuarios que tienen una estación meteorológica propia (Netatmo, Ecowitt, ESPHome, etc.) integrada en Home Assistant.

Permite crear una entidad `weather` que combina:
1. **Datos actuales**: De tus sensores locales (Temperatura, Humedad, Presión, Viento, Intensidad de Lluvia).
2. **Predicción**: Oficial del Meteocat para tu municipio.

> **Nota sobre la lluvia**: Si configuras el sensor de **Intensidad de Lluvia**, la entidad mostrará el estado "Lluvioso" cuando detecte precipitación. Si no llueve, mostrará la predicción de Meteocat (ej: "Sol", "Nublado").

Para cada municipio configurado se crean:

#### Weather Entity
- `weather.{municipio}`: Entidad principal. Muestra el estado actual (de tus sensores) y la predicción (del Meteocat).

#### Sensor UTCI
- **Nombre**: {Municipio} Temperatura UTCI
- **Entity ID**: `sensor.{municipio}_utci_index`
- Estado: Sensación térmica calculada (si se han configurado los sensores necesarios)

#### Sensor UTCI Literal
- **Nombre**: {Municipio} Estrés térmico
- Entity ID: `sensor.{municipi}_utci_literal`
- Estado: Descripción del estrés térmico e icono correspondiente

#### Sensores Beaufort (Local)
- **Índice Beaufort**: Número (0-17) calculado a partir de tu sensor de viento local.
- Entity ID: `sensor.{municipio}_beaufort_index`
- **Descripción Beaufort**: Texto descriptivo.
- Entity ID: `sensor.{municipio}_beaufort_description`
- *Nota: Requiere configurar un sensor de viento local.*

#### Sensor Predicción horaria
- **Nombre**: {Municipio} Predicción horaria
- **Entity ID**: `sensor.{municipio}_prediccio_horaria`
- Estado: Número de horas de predicción disponibles (ej: "72 horas")
- Atributos: Datos completos de predicción horaria (72h)

#### Sensor Predicción diaria
- **Nombre**: {Municipio} Predicción diaria
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

### Valores de Temperatura UTCI (Estrés Térmico)

El sensor "Estado de Confort Térmico" muestra un texto y un icono según el valor del índice UTCI:

| Rango UTCI (ºC) | Estado | Icono |
|-----------|-------|-------|
| > 46 | Estrés extremo por calor | `thermometer-alert` |
| 38 a 46 | Estrés muy fuerte por calor | `thermometer-alert` |
| 32 a 38 | Estrés fuerte por calor | `thermometer-alert` |
| 26 a 32 | Estrés moderado por calor | `thermometer-alert` |
| 9 a 26 | Confort (Sin estrés) | `check-circle-outline` |
| 0 a 9 | Estrés moderado por frío | `snowflake-alert` |
| -13 a 0 | Estrés fuerte por frío | `snowflake-alert` |
| -27 a -13 | Estrés muy fuerte por frío | `snowflake-alert` |
| < -27 | Estrés extremo por frío | `snowflake-alert` |

### Escala Beaufort (Viento)

La integración también ofrece la escala Beaufort (0-17) y su descripción.

| Índice | Descripción | km/h (aprox) |
|-------|------------|--------------|
| 0 | Calma | < 1 |
| 1 | Ventolina | 1 - 5 |
| 2 | Brisa muy débil | 6 - 11 |
| 3 | Brisa ligera | 12 - 19 |
| 4 | Brisa moderada | 20 - 28 |
| 5 | Brisa fresca | 29 - 38 |
| 6 | Brisa fuerte | 39 - 49 |
| 7 | Viento fuerte | 50 - 61 |
| 8 | Temporal | 62 - 74 |
| 9 | Temporal fuerte | 75 - 88 |
| 10 | Temporal muy fuerte | 89 - 102 |
| 11 | Temporal violento | 103 - 117 |
| 12+ | Huracán | > 117 |

## Actualización de datos

### 📊 Sistema de actualizaciones programadas

La integración está **optimizada para ahorrar cuota de la API** y asegurar que llegas a final de mes sin problemas, manteniendo los datos de la estación actualizados.

#### Comportamiento del sistema

Los datos se actualizan de la siguiente manera:

1. **Datos de la estación (XEMA)**: Se actualizan **cada hora** (en el minuto 0).
2. **Predicciones y Cuotas**: Se actualizan **SOLO** a las horas programadas (por defecto a las **06:00** y **14:00**).
3. **Manualmente**: Cuando pulsas el botón "Actualizar datos" (se actualiza todo).

#### Consumo de cuota por actualización

**Modo Estación (XEMA)**:
- **Cada hora**: 1 llamada (measurements + cuotas)
- **A las horas de predicción**: 3 llamadas adicionales (forecast + hourly + quotes)
- **Media diaria**: ~30 llamadas (24 horas × 1 + 2 predicciones × 3)

**Modo Estación Local**:
- **A las horas de predicción**: 3 llamadas (forecast + hourly + quotes)
- **Media diaria**: ~6 llamadas (2 programadas × 3)

#### Cálculo mensual (30 días)

| Modo | Llamadas/día | Llamadas/mes | Cuota restante* | Actualizaciones manuales disponibles |
|------|-------------|--------------|-----------------|-------------------------------------|
| **Estación XEMA** | ~30 | ~900 | ~100 | ~3/día (100÷30) |
| **Estación Local** | ~6 | ~180 | ~820 | ~27/día (820÷30) |

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
- Consume cuota de la API (5 llamadas en modo Estación XEMA, 4 en modo Estación Local)
- Útil para obtener datos frescos antes de un evento o viaje

## Eventos

Cada entrada de la integración dispara un **evento** (`meteocat_community_edition_data_updated`) cada vez que se actualizan los datos, tanto si es una actualización automática programada como si es manual (vía botón).

Este evento contiene la siguiente información:

- **`mode`**: Modo de la entrada (`external` o `local`)
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
          mode: external
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
          mode: local
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

## Detalle de los sensores de predicción

Tanto en el **Modo Estación XEMA** como en el **Modo Estación Local**, se crean sensores adicionales con los datos de predicción en bruto. Esto es útil si quieres crear tarjetas personalizadas o automatizaciones avanzadas.

### Sensores disponibles

El Modo Estación Local crea estos sensores:

### Sensores disponibles

- **`sensor.{municipio}_prediccion_horaria`**: Predicción de las próximas 72 horas
- **`sensor.{municipio}_prediccion_diaria`**: Predicción de los próximos 8 días  
- **`sensor.{municipio}_quota_{plan}`**: Consumos API (Predicción)
- **`binary_sensor.{municipio}_update_state`**: Estado de la última actualización (OFF=OK, ON=Error)
- **`sensor.{municipio}_last_update`**: Última actualización
- **`sensor.{municipio}_next_update`**: Próxima actualización programada
- **`button.{municipio}_refresh`**: Botón para actualizar manualmente
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
{{ state_attr('sensor.barcelona_prediccio_horaria', 'forecast') }}

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
{{ state_attr('sensor.barcelona_prediccio_horaria', 'forecast').dies[0].variables.temp.valors }}
```

#### Predicción diaria (`sensor.{municipio}_prediccion_diaria`)

El estado del sensor muestra el número de días disponibles (ej: "8 días").

Atributos disponibles:
```yaml
# Acceder a todos los datos de predicción diaria
{{ state_attr('sensor.barcelona_prediccio_diaria', 'forecast') }}

# La estructura contiene:
# - dies: array de días con predicciones
#   - data: fecha del día (ej: "2025-11-24")
#   - variables:
#     - tmax: temperatura máxima
#     - tmin: temperatura mínima
#     - ppcp: precipitación total
#     - etc.

# Ejemplo: temperatura máxima de mañana
{{ state_attr('sensor.barcelona_prediccio_diaria', 'forecast').dies[1].variables.tmax.valor }}

# Ejemplo: temperatura mínima de mañana
{{ state_attr('sensor.barcelona_prediccio_diaria', 'forecast').dies[1].variables.tmin.valor }}
```

### Ejemplo de entidad Weather personalizada



### Crear tarjetas personalizadas

Utiliza estos datos para crear tarjetas en tu dashboard:

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## Predicción Horaria - {{ state_attr('sensor.barcelona_prediccio_horaria', 'forecast').nom }}
      
      **Disponibles:** {{ states('sensor.barcelona_prediccio_horaria') }}
      
      {% set forecast = state_attr('sensor.barcelona_prediccio_horaria', 'forecast') %}
      {% if forecast and forecast.dies %}
        {% for dia in forecast.dies[:2] %}
        ### {{ dia.data }}
        Temperatura: {{ dia.variables.temp.valors[:6] | join(', ') }}°C
        {% endfor %}
      {% endif %}

  - type: markdown
    content: |
      ## Predicción diaria - Próximos días
      
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

#### 💡 **Múltiples API Keys para maximizar el uso**

Debido a que el **plan doméstico** permite pocas consultas al mes, el sistema permite crear **múltiples estaciones con API keys diferentes** para poder **exprimir las limitaciones de la API**.

**Ventajas:**
- Cada estación utiliza su propia cuota independiente
- Puedes monitorizar el uso de cada API key por separado
- Ideal para usuarios con múltiples estaciones o necesidades elevadas de datos

**Cómo hacerlo:**
1. Registra múltiples cuentas en la API de Meteocat (cada cuenta tiene su cuota independiente)
2. Agrega cada estación con una API key diferente
3. Utiliza los sensores de cuotas para controlar el uso de cada cuenta

**Consejo**: Si necesitas más peticiones, puedes crear múltiples entradas con diferentes API Keys.

### Otras limitaciones

- Las predicciones municipales dependen de la disponibilidad en la API de Meteocat
- En **Modo Estación Externa**, algunas estaciones pueden no tener municipio asociado para predicciones
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
