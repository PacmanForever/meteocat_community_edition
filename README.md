# Meteocat (Community Edition)

[![hacs][hacsbadge]][hacs]
[![Version](https://img.shields.io/github/v/tag/PacmanForever/meteocat_community_edition?label=version)](https://github.com/PacmanForever/meteocat_community_edition/tags)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

[![Tests](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests.yml/badge.svg)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests.yml)
[![Validate HACS](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hacs.yml/badge.svg)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hacs.yml)
[![Validate Hassfest](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hassfest.yml/badge.svg)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hassfest.yml)

![Home Assistant](https://img.shields.io/badge/home%20assistant-2024.1.0%2B-blue)

**Idiomes**: **Català** | [English](README.en.md) | [Español](README.es.md)

Integració **comunitària** i **no oficial** per a Home Assistant del Servei Meteorològic de Catalunya (Meteocat).

> 📢 **Integració de la Comunitat**
>
> Aquesta és una integració **creada per la comunitat**, **gratuïta** i de **codi obert**. No està afiliada, patrocinada ni aprovada pel Servei Meteorològic de Catalunya.
>
> ✅ **Ús Legal i Oficial de l'API**: Utilitza l'[**API oficial del Meteocat**](https://apidocs.meteocat.gencat.cat/) de manera completament legal i seguint les seves condicions d'ús.
>
> 🎯 **Objectiu**: Facilitar la integració amb Home Assistant sense necessitat de conèixer el funcionament intern de l'API. No té cap finalitat comercial ni busca obtenir cap benefici econòmic.

> **Beta:** Aquesta integració es troba en fase *beta*. No es garanteix el correcte funcionament i pot contenir errors; utilitza-la sota la teva pròpia responsabilitat.

> [!IMPORTANT]
> **Cal registrar-se a l'API de Meteocat** per obtenir una clau API:
> - 🆓 **Pla ciutadà** (gratuït)
> - 💼 **Pla empresa** (de pagament)
>
> Registra't a: https://apidocs.meteocat.gencat.cat/

**Idiomes**: **Català** | [English](README.en.md) | [Español](README.es.md)

## Característiques

- 🌡️ **Dades meteorològiques en temps real** de les estacions XEMA
- 📊 **Prediccions horàries** (72 hores) i **diàries** (8 dies)
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
5. Selecciona **"Predicció municipal""
6. Selecciona la **comarca**
7. Selecciona el **municipi**
8. Configura les **hores d'actualització** (per defecte 06:00 i 14:00)

Això crearà:
- **Sensor de predicció horària** (72h en atributs) - Per utilitzar en `weather.template`
- **Sensor de predicció diària** (8 dies en atributs) - Per utilitzar en `weather.template`
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

La integració crea diferents entitats segons el mode configurat:

### Mode Estació XEMA (Dades en temps real + Predicció)

Aquest mode està pensat per obtenir dades d'una estació meteorològica oficial del Meteocat.

**Dispositiu**: `{Nom Estació} {Codi}` (ex: "Barcelona - Raval YM")

| Tipus | Entitat | Descripció |
|-------|---------|------------|
| **Weather** | `weather.{estacio}_{codi}` | Entitat principal. Mostra l'estat actual (temperatura, humitat, vent, pressió, pluja) obtingut de l'estació XEMA i la predicció (horària i diària) del municipi on es troba l'estació. |
| **Sensor** | `sensor.{estacio}_{codi}_quota_{pla}` | Un sensor per a cada pla de quotes (Predicció, Referència, XDDE, XEMA). Mostra les peticions restants. |
| **Binary Sensor** | `binary_sensor.{estacio}_{codi}_update_state` | Indica l'estat de l'última actualització (`OFF` = Correcte, `ON` = Error). |
| **Sensor** | `sensor.{estacio}_{codi}_last_update` | Timestamp de l'última actualització exitosa. |
| **Sensor** | `sensor.{estacio}_{codi}_next_update` | Timestamp de la pròxima actualització programada. |
| **Sensor** | `sensor.{estacio}_{codi}_update_time_{n}` | Mostra les hores d'actualització configurades (ex: 06:00, 14:00). |
| **Sensor** | `sensor.{estacio}_{codi}_altitude` | Altitud de l'estació (metres). |
| **Sensor** | `sensor.{estacio}_{codi}_latitude` | Latitud de l'estació. |
| **Sensor** | `sensor.{estacio}_{codi}_longitude` | Longitud de l'estació. |
| **Sensor** | `sensor.{estacio}_{codi}_comarca_name` | Nom de la comarca. |
| **Sensor** | `sensor.{estacio}_{codi}_municipality_name` | Nom del municipi (si disponible). |
| **Sensor** | `sensor.{estacio}_{codi}_provincia_name` | Nom de la província (si disponible). |
| **Button** | `button.{estacio}_{codi}_refresh` | Botó per forçar una actualització manual immediata. |

### Mode Predicció Municipal (Només Predicció)

Aquest mode està pensat per a usuaris que ja tenen una estació meteorològica pròpia (Netatmo, Ecowitt, etc.) i només volen les prediccions oficials.

**Dispositiu**: `{Nom Municipi}` (ex: "Barcelona")

| Tipus | Entitat | Descripció |
|-------|---------|------------|
| **Sensor** | `sensor.{municipi}_prediccio_horaria` | L'estat mostra les hores disponibles. Els atributs contenen la predicció completa per a 72h. |
| **Sensor** | `sensor.{municipi}_prediccio_diaria` | L'estat mostra els dies disponibles. Els atributs contenen la predicció completa per a 8 dies. |
| **Sensor** | `sensor.{municipi}_quota_{pla}` | Un sensor per a cada pla de quotes (Predicció, Referència, XDDE, XEMA). Mostra les peticions restants. |
| **Binary Sensor** | `binary_sensor.{municipi}_update_state` | Indica l'estat de l'última actualització (`OFF` = Correcte, `ON` = Error). |
| **Sensor** | `sensor.{municipi}_last_update` | Timestamp de l'última actualització exitosa. |
| **Sensor** | `sensor.{municipi}_next_update` | Timestamp de la pròxima actualització programada. |
| **Sensor** | `sensor.{municipi}_update_time_{n}` | Mostra les hores d'actualització configurades. |
| **Sensor** | `sensor.{municipi}_municipality_name` | Nom del municipi. |
| **Sensor** | `sensor.{municipi}_comarca_name` | Nom de la comarca. |
| **Sensor** | `sensor.{municipi}_provincia_name` | Nom de la província (si disponible). |
| **Sensor** | `sensor.{municipi}_municipality_latitude` | Latitud del municipi (si disponible). |
| **Sensor** | `sensor.{municipi}_municipality_longitude` | Longitud del municipi (si disponible). |
| **Button** | `button.{municipi}_refresh` | Botó per forçar una actualització manual immediata. |

> **Nota:** En el Mode Municipi **NO es crea cap entitat `weather`**. Has de fer servir els sensors de predicció per crear la teva pròpia entitat `weather.template` o mostrar les dades en targetes personalitzades.

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
- Primera actualització: 5 crides (stations + measurements + forecast + hourly + quotes)
- Actualitzacions posteriors: 4 crides (measurements + forecast + hourly + quotes)
- **Mitjana diària**: ~13 crides (1 inicial + 2 programades × 4)

**Mode Municipal**:
- Cada actualització: 3 crides (forecast + hourly + quotes)
- **Mitjana diària**: ~6 crides (2 programades × 3)

#### Càlcul mensual (30 dies)

| Mode | Crides/dia | Crides/mes | Quota restant* | Actualitzacions manuals disponibles |
|------|-----------|-----------|----------------|-------------------------------------|
| **Estació** | 13 | 390 | 610 | ~20/dia (610÷30) |
| **Municipal** | 6 | 180 | 820 | ~27/dia (820÷30) |

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

### Exemple d'entitat Weather personalitzada

⚠️ **Nota important**: El component `weather.template` requereix preprocessar les dades ja que l'API de Meteocat retorna estructures complexes. És més pràctic utilitzar **targetes personalitzades** o **sensors template** per mostrar les prediccions.

#### Afegir prediccions a una entitat weather local

Si tens una estació meteorològica local i vols afegir-hi les prediccions de Meteocat, pots utilitzar una entitat `weather.template`:

```yaml
weather:
  - platform: template
    name: "Casa amb Predicció"
    condition_template: "{{ states('weather.la_meva_estacio_local') }}"
    temperature_template: "{{ state_attr('weather.la_meva_estacio_local', 'temperature') }}"
    humidity_template: "{{ state_attr('weather.la_meva_estacio_local', 'humidity') }}"
    # ... altres camps de la teva estació local ...
    
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
```

### Explorar les dades

Utilitza **Developer Tools → Template** de Home Assistant per explorar l'estructura completa de les dades:

```yaml
# Veure tota l'estructura de predicció horària
{{ state_attr('sensor.Barcelona_prediccio_horaria', 'forecast') }}

# Veure tota l'estructura de predicció diària
{{ state_attr('sensor.Barcelona_prediccio_diaria', 'forecast') }}
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

[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg


