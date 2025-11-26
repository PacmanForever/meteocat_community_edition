# Meteocat (Community Edition)

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

Integración **comunitaria** y **no oficial** para Home Assistant del Servicio Meteorológico de Cataluña (Meteocat).

>  **Integración de la Comunidad**
>
> Esta es una integración **creada por la comunidad**, **gratuita** y de **código abierto**. No está afiliada, patrocinada ni aprobada por el Servicio Meteorológico de Cataluña.
>
>  **Uso Legal y Oficial de la API**: Utiliza la [**API oficial del Meteocat**](https://apidocs.meteocat.gencat.cat/) de manera completamente legal y siguiendo sus condiciones de uso.
>
> 🎯 **Objetivo**: Facilitar la integración con Home Assistant sin necesidad de conocer el funcionamiento interno de la API. No tiene ningún fin comercial ni busca obtener ningún beneficio económico.

> [!IMPORTANT]
> **Es necesario registrarse en la API de Meteocat** para obtener una clave API:
> - 🆓 **Plan ciudadano** (gratuito)
> - 💼 **Plan empresa** (de pago)
>
> Regístrate en: https://apidocs.meteocat.gencat.cat/

**Idiomas**: [Català](README.md) | [English](README.en.md) | **Español**
## Característiques

- 🌡️ **Dades meteorològiques en temps real** de les estacions XEMA
- 📊 **Prediccions horàries** (72 hores) i **diàries** (8 dies)
- ☀️ **Índex UV** previst
- 📈 **Sensors de quotes API** per controlar l'ús
- 🏢 **Múltiples estacions** configurables
- 🏙️ **Mode Municipi** per obtenir només prediccions (sense estació)
- 🌍 Traduccions en **català**, **castellà** i **anglès**

## Instal·lació

### Via HACS (Recomanat)

1. Assegura't que tens [HACS](https://hacs.xyz/) instal·lat
2. A HACS, ves a "Integracions"
3. Fes clic al menú de 3 punts (dalt a la dreta) i selecciona "Repositoris personalitzats"
4. Afegeix aquest URL: `https://github.com/PacmanForever/meteocat_community_edition`
5. Categoria: `Integration`
6. Fes clic a "Afegir"
7. Cerca "Meteocat" i instal·la
8. Reinicia Home Assistant

### Manual

1. Descarrega la carpeta `custom_components/meteocat_community_edition`
2. Copia-la a `<config>/custom_components/meteocat_community_edition`
3. Reinicia Home Assistant

## Configuració

### Obtenir una API Key

1. Registra't a [https://apidocs.meteocat.gencat.cat/](https://apidocs.meteocat.gencat.cat/)
2. Segueix el [procés de registre](https://apidocs.meteocat.gencat.cat/documentacio/proces-de-registre/)
3. Obtindràs una clau API única

### Afegir una estació o municipi

#### Mode Estació (amb dades en temps real)

1. A Home Assistant, ves a **Configuració** → **Dispositius i Serveis**
2. Fes clic a **Afegir integració**
3. Cerca **Meteocat (Community Edition)**
4. Introdueix la teva **clau API**
5. Selecciona **"Estació XEMA"**
6. Selecciona la **comarca**
7. Selecciona l'**estació meteorològica**
8. Configura les **hores d'actualització** (per defecte 06:00 i 14:00)

Això crearà:
- **Entitat Weather** amb dades actuals de l'estació i prediccions
- **Sensors de quotes** API
- **Sensors d'hores d'actualització** configurades

#### Mode Municipi (només prediccions)

> ⚠️ **Important:** Aquest mode està pensat **exclusivament** per a usuaris que tenen una **estació meteorològica local** (personal, Netatmo, Ecowitt, etc.) i volen complementar-la amb les **prediccions horàries i diàries oficials** de Meteocat. Si no tens cap estació meteorològica local, utilitza el **Mode Estació** que et proporcionarà tant dades en temps real com prediccions.

Aquest mode crea sensors amb les prediccions en els seus atributs, permetent-te utilitzar-les en entitats `weather.template` personalitzades que combinin dades de la teva estació local amb prediccions oficials.

1. A Home Assistant, ves a **Configuració** → **Dispositius i Serveis**
2. Fes clic a **Afegir integració**
3. Cerca **Meteocat (Community Edition)**
4. Introdueix la teva **clau API**
5. Selecciona **"Prediccions municipals""
6. Selecciona la **comarca**
7. Selecciona el **municipi**
8. Configura les **hores d'actualització** (per defecte 06:00 i 14:00)

Això crearà:
- **Sensor de predicció horària** (72h en atributs) - Per utilitzar en `weather.template`
- **Sensor de predicció diària** (8 dies en atributs) - Per utilitzar en `weather.template`
- **Sensor d'índex UV**
- **Sensors de quotes** API
- **Sensors d'hores d'actualització** configurades

**Pots configurar múltiples estacions i municipis** (amb diferents API keys per incrementar els límits).

### Opcions avançades

Per configurar un endpoint personalitzat o modificar les hores d'actualització:

1. Ves a **Configuració** → **Dispositius i Serveis**
2. Troba **Meteocat (Community Edition)**
3. Fes clic als 3 punts → **Opcions**
4. Modifica:
   - **URL base de l'API** (deixa valor per defecte o buit per a producció)
   - **Hores d'actualització** (format 24h: HH:MM)

## Entitats

### Mode Estació XEMA

Per cada estació configurada es creen:

#### Weather Entity
- `weather.{estacio}_{codi}`: Entitat principal amb dades actuals i prediccions
- Exemple: `weather.Barcelona_ym`

#### Sensors de Quotes
- **Peticions disponibles Predicció**: Consums restants del pla Predicció
- **Peticions disponibles Referència**: Consums restants del pla Referència  
- **Peticions disponibles XDDE**: Consums restants del pla XDDE
- **Peticions disponibles XEMA**: Consums restants del pla XEMA
- Entity IDs: `sensor.{estacio}_{codi}_quota_{pla}`
- Exemple: `sensor.Barcelona_ym_quota_prediccio`
- Atributs: límit total, peticions utilitzades, data de reset

#### Sensors de Timestamps
- **Última actualització**: Timestamp de la darrera actualització exitosa
- **Pròxima actualització**: Timestamp de la pròxima actualització programada
- Entity IDs: `sensor.{estacio}_{codi}_last_update`, `sensor.{estacio}_{codi}_next_update`

#### Sensors d'Hores d'Actualització
- **Hora d'actualització 1**: Mostra la primera hora configurada (read-only)
- **Hora d'actualització 2**: Mostra la segona hora configurada (read-only)
- Entity IDs: `sensor.{estacio}_{codi}_update_time_1`, `sensor.{estacio}_{codi}_update_time_2`
- Format: HH:MM (24h)

#### Botó d'Actualització
- **Actualitzar dades**: Força una actualització immediata de totes les dades
- Entity ID: `button.{estacio}_{codi}_refresh`
- Exemple: `button.Barcelona_ym_refresh`

> **Nota:** Totes les entitats s'agrupen sota un únic dispositiu amb nom "{Estació} {Codi}" (ex: "Barcelona YM")

### Mode Prediccions Municipals

Per cada municipi configurat es creen:

#### Sensor Predicció Horària
- **Nom**: {Municipi} Predicció Horària
- **Entity ID**: `sensor.{municipi}_prediccio_horaria`
- Estat: Nombre d'hores de predicció disponibles (ex: "72 hores")
- Atributs: Dades completes de predicció horària (72h)

#### Sensor Predicció Diària
- **Nom**: {Municipi} Predicció Diària
- **Entity ID**: `sensor.{municipi}_prediccio_diaria`
- Estat: Nombre de dies de predicció disponibles (ex: "8 dies")
- Atributs: Dades completes de predicció diària (8 dies)

#### Sensor Predicció Índex UV
- **Nom**: {Municipi} Predicció Índex UV
- **Entity ID**: `sensor.{municipi}_prediccio_index_uv`
- Estat: Nombre de dies de predicció UV disponibles (ex: "3 dies")
- Atributs: Dades completes de previsió UV (dades horàries per 3 dies)

#### Sensors de Quotes
- **Peticions disponibles Predicció**: Consums restants del pla Predicció
- **Peticions disponibles Referència**: Consums restants del pla Referència  
- **Peticions disponibles XDDE**: Consums restants del pla XDDE
- **Peticions disponibles XEMA**: Consums restants del pla XEMA
- Entity IDs: `sensor.{municipi}_quota_{pla}`
- Exemple: `sensor.Barcelona_quota_prediccio`
- Atributs: límit total, peticions utilitzades, data de reset

#### Sensors de Timestamps
- **Última actualització**: Timestamp de la darrera actualització exitosa
- **Pròxima actualització**: Timestamp de la pròxima actualització programada
- Entity IDs: `sensor.{municipi}_last_update`, `sensor.{municipi}_next_update`

#### Sensors d'Hores d'Actualització
- **Hora d'actualització 1**: Mostra la primera hora configurada (read-only)
- **Hora d'actualització 2**: Mostra la segona hora configurada (read-only)
- Entity IDs: `sensor.{municipi}_update_time_1`, `sensor.{municipi}_update_time_2`
- Format: HH:MM (24h)

#### Botó d'Actualització
- **Actualitzar dades**: Força una actualització immediata de totes les dades
- Entity ID: `button.{municipi}_refresh`
- Exemple: `button.Barcelona_refresh`

> **Nota:** Totes les entitats s'agrupen sota un únic dispositiu amb nom "{Municipi}" (ex: "Barcelona")

## Actualització de dades

### 📊 Sistema d'actualitzacions programades

La integració està **optimitzada per estalviar quota de l'API** i assegurar que arribes a final de mes sense problemes.

#### Comportament del sistema

Les dades s'actualitzen **NOMÉS** en aquests casos:

1. **A l'inici**: Quan s'engega Home Assistant o s'activa la integració (1 vegada)
2. **A les hores programades**: Per defecte a les **06:00** i **14:00** (2 vegades/dia)
3. **Manualment**: Quan prems el botó "Actualitzar dades"

⚠️ **IMPORTANT**: La integració **NO fa polling automàtic**. Això vol dir que NO s'actualitza cada X minuts/hores de forma contínua, sinó que només ho fa als moments exactes configurats.

#### Consum de quota per actualització

Cada actualització fa les següents crides a l'API:

**Mode Estació (XEMA)**:
- Primera actualització: 6 crides (stations + measurements + forecast + hourly + uv + quotes)
- Actualitzacions posteriors: 5 crides (measurements + forecast + hourly + uv + quotes)
- **Mitjana diària**: ~16 crides (1 inicial + 2 programades × 5)

**Mode Municipal**:
- Cada actualització: 4 crides (forecast + hourly + uv + quotes)
- **Mitjana diària**: ~8 crides (2 programades × 4)

#### Càlcul mensual (30 dies)

| Mode | Crides/dia | Crides/mes | Quota restant* | Actualitzacions manuals disponibles |
|------|-----------|-----------|----------------|-------------------------------------|
| **Estació** | 16 | 480 | 520 | ~17/dia (520÷30) |
| **Municipal** | 8 | 240 | 760 | ~25/dia (760÷30) |

\* Assumint quota de 1000 crides/mes (pla Predicció estàndard)

#### Personalitzar hores d'actualització

Pots modificar les hores d'actualització a través de:

**Configuració** → **Dispositius i Serveis** → (3 punts de la integració) → **Opcions**

- **Hora d'actualització 1**: Primera hora del dia (format 24h: HH:MM)
- **Hora d'actualització 2**: Segona hora del dia (format 24h: HH:MM)

Exemples de configuració:
- **Predeterminat**: 06:00 i 14:00
- **Noctàmbul**: 10:00 i 22:00
- **Matiner**: 05:00 i 12:00

⚠️ **Recomanació**: Mantenir 2 actualitzacions diàries. Amb 3 o més actualitzacions diàries, pots esgotar la quota abans de final de mes.

#### Botó d'actualització manual

Cada entrada crea un botó **"Actualitzar dades"** que et permet forçar una actualització immediata quan la necessitis:

- No afecta les actualitzacions programades
- Consumeix quota de l'API (5 crides en mode Estació, 4 en mode Municipal)
- Útil per obtenir dades fresques abans d'un esdeveniment o viatge

## Esdeveniments

Cada entrada de la integració dispara un **esdeveniment** (`meteocat_community_edition_data_updated`) cada cop que s'actualitzen les dades, tant si és una actualització automàtica programada com si és manual (via botó).

Aquest esdeveniment conté la següent informació:

- **`mode`**: Mode de l'entrada (`estacio` o `municipi`)
- **`station_code`**: Codi de l'estació (només en Mode Estació)
- **`municipality_code`**: Codi del municipi (si està disponible)
- **`timestamp`**: Moment exacte de l'actualització (ISO 8601)

### Utilitzar esdeveniments en automatitzacions

Pots crear automatitzacions que es desencadenin quan hi hagi noves dades:

```yaml
automation:
  - alias: "Notificació quan s'actualitza Meteocat"
    trigger:
      - platform: event
        event_type: meteocat_community_edition_data_updated
        event_data:
          mode: estacio
          station_code: YM
    action:
      - service: notify.mobile_app
        data:
          message: "Noves dades meteorològiques disponibles de l'estació Barcelona!"

  - alias: "Actualitzar dashboard amb noves prediccions"
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

També pots escoltar l'esdeveniment sense filtres per actuar amb qualsevol actualització:

```yaml
automation:
  - alias: "Log actualitzacions Meteocat"
    trigger:
      - platform: event
        event_type: meteocat_community_edition_data_updated
    action:
      - service: logbook.log
        data:
          name: Meteocat
          message: >
            Actualització de dades completada: 
            Mode={{ trigger.event.data.mode }}, 
            Timestamp={{ trigger.event.data.timestamp }}
```

## Utilitzar les prediccions municipals en una entitat Weather personalitzada

> 💡 **Per a què serveix aquesta secció?** Si tens una **estació meteorològica local** (Netatmo, Ecowitt, personal, etc.) que proporciona dades actuals però **no té prediccions**, aquesta secció t'explica com combinar les dades de la teva estació amb les prediccions oficials de Meteocat utilitzant el **Mode Municipi**.

Si has configurat el **Mode Municipi**, pots utilitzar les dades dels sensors de predicció per crear la teva pròpia entitat Weather mitjançant el component [`weather.template` de Home Assistant](https://www.home-assistant.io/integrations/weather.template/), combinant:
- **Dades actuals** de la teva estació meteorològica local
- **Prediccions oficials** de Meteocat (horàries i diàries)

### Sensors disponibles en Mode Municipi

El Mode Municipi crea aquests sensors:

- **`sensor.{municipi}_prediccio_horaria`**: Predicció de les pròximes 72 hores
- **`sensor.{municipi}_prediccio_diaria`**: Predicció dels pròxims 8 dies  
- **`sensor.{municipi}_prediccio_index_uv`**: Predicció d'índex UV (3 dies)
- **`sensor.{municipi}_quota_{pla}`**: Consums API (Predicció, Referència, XDDE, XEMA)
- **`sensor.{municipi}_last_update`**: Darrera actualització
- **`sensor.{municipi}_next_update`**: Pròxima actualització programada
- **`button.{municipi}_refresh`**: Botó per actualitzar manualment

### Accedir a les dades de predicció

Els sensors emmagatzemen les prediccions completes als seus **atributs**::

#### Predicció Horària (`sensor.{municipi}_prediccio_horaria`)

L'estat del sensor mostra el nombre d'hores disponibles (ex: "72 hores").

Atributs disponibles:
```yaml
# Accedir a totes les dades de predicció horària
{{ state_attr('sensor.Barcelona_prediccio_horaria', 'forecast') }}

# L'estructura conté:
# - dies: array de dies amb prediccions
#   - data: data del dia (ex: "2025-11-24")
#   - variables: diccionari amb les variables meteorològiques
#     - temp: temperatura (valors per hora)
#     - hr: humitat relativa
#     - ws: velocitat del vent
#     - wd: direcció del vent
#     - ppcp: precipitació
#     - etc.

# Exemple: accedir a les temperatures d'avui
{{ state_attr('sensor.Barcelona_prediccio_horaria', 'forecast').dies[0].variables.temp.valors }}
```

#### Predicció Diària (`sensor.{municipi}_prediccio_diaria`)

L'estat del sensor mostra el nombre de dies disponibles (ex: "8 dies").

Atributs disponibles:
```yaml
# Accedir a totes les dades de predicció diària
{{ state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') }}

# L'estructura conté:
# - dies: array de dies amb prediccions
#   - data: data del dia (ex: "2025-11-24")
#   - variables:
#     - tmax: temperatura màxima
#     - tmin: temperatura mínima
#     - ppcp: precipitació total
#     - etc.

# Exemple: temperatura màxima de demà
{{ state_attr('sensor.Barcelona_prediccio_diaria', 'forecast').dies[1].variables.tmax.valor }}

# Exemple: temperatura mínima de demà
{{ state_attr('sensor.Barcelona_prediccio_diaria', 'forecast').dies[1].variables.tmin.valor }}
```

#### Predicció Índex UV (`sensor.{municipi}_prediccio_index_uv`)

L'estat del sensor mostra el nombre de dies de predicció UV disponibles (ex: "3 dies").

Atributs disponibles:
```yaml
# Accedir a totes les dades UV
{{ state_attr('sensor.Barcelona_prediccio_index_uv', 'uv_forecast') }}

# L'estructura conté:
# - ine: codi INE del municipi
# - nom: nom del municipi
# - uvi: array amb prediccions UV per dies (normalment 3 dies)
#   - date: data (ex: "2025-11-24")
#   - hours: array d'hores amb valors UV
#     - hour: hora (0-23)
#     - uvi: índex UV
#     - uvi_clouds: índex UV amb núvols

# Exemple: UV a les 12:00 d'avui
{% set uv_data = state_attr('sensor.Barcelona_prediccio_index_uv', 'uv_forecast') %}
{% if uv_data and uv_data.uvi %}
  {{ uv_data.uvi[0].hours | selectattr('hour', 'equalto', 12) | map(attribute='uvi') | first }}
{% endif %}

# Exemple: UV màxim d'avui
{% set uv_data = state_attr('sensor.Barcelona_prediccio_index_uv', 'uv_forecast') %}
{% if uv_data and uv_data.uvi %}
  {{ uv_data.uvi[0].hours | map(attribute='uvi') | max }}
{% endif %}
```

### Exemple d'entitat Weather personalitzada

⚠️ **Nota important**: El component `weather.template` requereix preprocessar les dades ja que l'API de Meteocat retorna estructures complexes. És més pràctic utilitzar **targetes personalitzades** o **sensors template** per mostrar les prediccions.

#### Afegir índex UV a una entitat weather local

Si tens una estació meteorològica local i vols afegir-hi la predicció d'índex UV de Meteocat, pots crear un sensor template que extregui el valor UV màxim:

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

Aquest sensor extreu el valor UV màxim del primer dia i pots utilitzar-lo en una entitat `weather.template`:

```yaml
weather:
  - platform: template
    name: "Casa amb UV"
    condition_template: "{{ states('weather.la_meva_estacio_local') }}"
    temperature_template: "{{ state_attr('weather.la_meva_estacio_local', 'temperature') }}"
    humidity_template: "{{ state_attr('weather.la_meva_estacio_local', 'humidity') }}"
    # ... altres camps de la teva estació local ...
    
    # Afegir índex UV de Meteocat
    uv_index_template: "{{ states('sensor.uv_index_weather') }}"
    
    # Prediccions horàries/diàries de Meteocat
    forecast_hourly_template: "{{ state_attr('sensor.Barcelona_prediccio_horaria', 'forecast') }}"
    forecast_daily_template: "{{ state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') }}"
```

> **Important**: Les prediccions de Meteocat segueixen l'estructura de la seva API, que pot no ser compatible directament amb `weather.template`. Consulta la documentació de [`weather.template`](https://www.home-assistant.io/integrations/weather.template/) per adaptar les dades al format esperat.

### Crear targetes personalitzades

Utilitza aquestes dades per crear targetes al teu dashboard:

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## Predicció Horària - {{ state_attr('sensor.Barcelona_prediccio_horaria', 'forecast').nom }}
      
      **Disponibles:** {{ states('sensor.Barcelona_prediccio_horaria') }}
      
      {% set forecast = state_attr('sensor.Barcelona_prediccio_horaria', 'forecast') %}
      {% if forecast and forecast.dies %}
        {% for dia in forecast.dies[:2] %}
        ### {{ dia.data }}
        Temperatura: {{ dia.variables.temp.valors[:6] | join(', ') }}°C
        {% endfor %}
      {% endif %}

  - type: markdown
    content: |
      ## Predicció Diària - Pròxims dies
      
      **Disponibles:** {{ states('sensor.Barcelona_prediccio_diaria') }}
      
      {% set forecast = state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') %}
      {% if forecast and forecast.dies %}
        {% for dia in forecast.dies[:5] %}
        **{{ dia.data }}**: {{ dia.variables.tmin.valor }}°C - {{ dia.variables.tmax.valor }}°C
        {% endfor %}
      {% endif %}

  - type: markdown
    content: |
      ## Predicció Índex UV
      
      **Disponibles:** {{ states('sensor.Barcelona_prediccio_index_uv') }}
      
      {% set uv = state_attr('sensor.Barcelona_prediccio_index_uv', 'uv_forecast') %}
      {% if uv and uv.uvi %}
        **UV Màxim avui:** {{ uv.uvi[0].hours | map(attribute='uvi') | max }}
        
        **Valors per hores:**
        {% for hour in uv.uvi[0].hours | selectattr('uvi', 'gt', 0) %}
        {{ hour.hour }}h: UV {{ hour.uvi }}
        {% endfor %}
      {% endif %}
```

### Sensors template personalitzats

Pots crear sensors template per extreure dades específiques:

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
      
      - name: "Temperatura màxima demà"
        unit_of_measurement: "°C"
        state: >
          {% set forecast = state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') %}
          {% if forecast and forecast.dies | length > 1 %}
            {{ forecast.dies[1].variables.tmax.valor }}
          {% else %}
            unknown
          {% endif %}
      
      - name: "Pluja prevista avui"
        unit_of_measurement: "mm"
        state: >
          {% set forecast = state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') %}
          {% if forecast and forecast.dies %}
            {{ forecast.dies[0].variables.ppcp.valor | default(0) }}
          {% else %}
            0
          {% endif %}
```

### Automatitzacions amb prediccions

Crea automatitzacions basades en les prediccions futures:

```yaml
automation:
  - alias: "Avís temperatura alta demà"
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
          message: "Demà farà més de 30°C!"

  - alias: "Avís UV alt"
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
          message: "Avui l'índex UV serà alt! Protegeix-te del sol."
```

### Explorar les dades

Utilitza **Developer Tools → Template** de Home Assistant per explorar l'estructura completa de les dades:

```yaml
# Veure tota l'estructura de predicció horària
{{ state_attr('sensor.Barcelona_prediccio_horaria', 'forecast') }}

# Veure tota l'estructura de predicció diària
{{ state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') %}

# Veure tota l'estructura UV
{{ state_attr('sensor.Barcelona_prediccio_index_uv', 'uv_forecast') }}
```

> **Consell:** Les estructures de dades segueixen exactament el format de l'API de Meteocat. Consulta la [documentació oficial de l'API](https://apidocs.meteocat.gencat.cat/) per conèixer tots els camps disponibles.

## Limitacions

### Quotes de l'API

L'API de Meteocat té límits de peticions que depenen del pla contractat. Consulta la [documentació oficial de Meteocat](https://apidocs.meteocat.gencat.cat/documentacio/consums/) per conèixer els límits actualitzats de cada pla.

Cada entrada de la integració crea **sensors de quotes** que mostren les peticions disponibles dels quatre plans (Predicció, Referència, XDDE, XEMA), independentment del pla contractat a la teva API key.

Aquesta integració està optimitzada per minimitzar l'ús:
- Només 2 actualitzacions automàtiques al dia (6:00 i 14:00)
- Les quotes es consulten **després** de les altres APIs per comptabilitzar correctament
- Els sensors de quotes et permeten monitoritzar l'ús en temps real

**Consell**: Si necessites més peticions, pots crear múltiples entrades amb diferents API Keys.

### Altres limitacions

- Les prediccions municipals depenen de la disponibilitat a l'API de Meteocat
- En Mode Estació, algunes estacions poden no tenir municipi associat per a prediccions
- Requereix connexió a Internet

## Troubleshooting

### Error "cannot_connect"
- Verifica que la clau API sigui correcta
- Comprova la connexió a Internet
- Assegura't que no has superat els límits de quotes

### No es mostren prediccions
- Algunes estacions poden no tenir municipi associat
- Espera a la següent actualització programada

### Quotes esgotades
- Afegeix l'estació amb una API Key diferent
- Espera al reset de quotes (consultable als sensors)

## Contribuir

Les contribucions són benvingudes! Si us plau:

1. Fork del repositori
2. Crea una branca per a la teva característica
3. Fes commit dels canvis
4. Envia un Pull Request

## Llicència

Aquest projecte està llicenciat sota GPL-3.0 - veure [LICENSE](LICENSE) per detalls.

## Agraïments

- [Servei Meteorològic de Catalunya](https://www.meteo.cat/) per proporcionar l'API
- Comunitat de Home Assistant

## Disclaimer

Aquesta és una integració **no oficial** creada per la comunitat per facilitar l'ús de l'API pública del Meteocat a Home Assistant.

- ❌ **NO** està afiliada, patrocinada ni aprovada pel Servei Meteorològic de Catalunya
- ✅ **SÍ** utilitza l'API oficial del Meteocat de manera legal i respectant les seves condicions d'ús
- 💰 **Gratuïta**: Projecte de codi obert sense ànim de lucre
- 🎯 **Propòsit**: Simplificar la integració amb Home Assistant sense necessitat de programar crides directes a l'API

Per utilitzar aquesta integració, cal que et registris a https://apidocs.meteocat.gencat.cat/ i obtinguis la teva pròpia clau API segons les condicions establertes pel Meteocat.

### Llicència i Garanties

Aquest programari es distribueix sota la **llicència GPL-3.0** (GNU General Public License v3.0):

- ✅ **Programari lliure**: Pots usar, modificar i redistribuir aquest codi
- 📖 **Codi obert**: Tot el codi font està disponible públicament
- 🔄 **Copyleft**: Les modificacions han de mantenir la mateixa llicència GPL-3.0
- ⚠️ **Sense garanties**: Aquest programari es proporciona "TAL QUAL" (AS IS), sense cap mena de garantia, ni explícita ni implícita, incloent-hi però sense limitar-se a les garanties de comercialització, idoneïtat per a un propòsit particular i no infracció. En cap cas els autors seran responsables de cap reclamació, dany o altra responsabilitat.

Consulta el fitxer [LICENSE](LICENSE) per la llicència completa.

---

[releases-shield]: https://img.shields.io/github/release/PacmanForever/meteocat_community_edition.svg
[releases]: https://github.com/PacmanForever/meteocat_community_edition/releases
[license-shield]: https://img.shields.io/github/license/PacmanForever/meteocat_community_edition.svg
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg

