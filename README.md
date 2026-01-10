# Meteocat (Community Edition)

[![hacs][hacsbadge]][hacs]
[![Version](https://img.shields.io/github/v/tag/PacmanForever/meteocat_community_edition?label=version)](https://github.com/PacmanForever/meteocat_community_edition/tags)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/PacmanForever/meteocat_community_edition/main/coverage.json)

[![Unit Tests](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests_unit.yml/badge.svg?branch=main)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests_unit.yml)
[![Component Tests](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests_component.yml/badge.svg?branch=main)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/tests_component.yml)
[![Validate HACS](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hacs.yml/badge.svg?branch=main)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hacs.yml)
[![Validate Hassfest](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hassfest.yml/badge.svg?branch=main)](https://github.com/PacmanForever/meteocat_community_edition/actions/workflows/validate_hassfest.yml)

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

> [!IMPORTANT]
> **Beta:** Aquesta integració es troba en fase *beta*. No es garanteix el correcte funcionament i pot contenir errors; utilitza-la sota la teva pròpia responsabilitat.
>  
> **Cal registrar-se a l'API de Meteocat** per obtenir una clau API:
> - 🆓 **Pla ciutadà** (gratuït)
> - 💼 **Pla empresa** (de pagament)
>
> Registra't a: https://apidocs.meteocat.gencat.cat/

## Característiques

- 🌡️ **Dades meteorològiques en temps real** de les estacions XEMA
- 📊 **Prediccions horàries** (72 hores) i **diàries** (8 dies)
- 📈 **Sensors de quotes API** per controlar l'ús
- 🏢 **Múltiples estacions** configurables
- 🏙️ **Mode Estació Local** per combinar sensors propis amb prediccions oficials
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

### Novetats en el flux de configuració

- **Pas de mapeig de condició climàtica**: En mode local, pots definir com es mapeja la condició climàtica (icona) de l'entitat Weather.
    - Pots triar entre:
        - **Automàtic (Meteocat)**: El valor de condició s'agafa directament de la predicció oficial de Meteocat.
        - **Personalitzat**: Pots definir un mapeig manual entre els valors del sensor local i les condicions suportades per Home Assistant.
    - Aquesta pantalla està completament traduïda a català, castellà i anglès.

- **Edició del mapping després de la configuració**: Les estacions locals ja configurades poden modificar el seu mapping de condició climàtica en qualsevol moment a través de les opcions de la integració.

- **Exemple de mapeig**: S'ofereix un exemple de mapeig a la pantalla per facilitar la configuració.

- **Millores en les etiquetes de la interfície**: Les pantalles de configuració tenen etiquetes més clares i descripcions simplificades.

### Notes sobre el comportament de la icona (Condició)

- **Mode Estació Externa**: La condició (icona de l'entitat weather) s'obté de les dades en temps real (XEMA), concretament de la variable de "Estat del cel" (codi 35). Per tant, funciona independentment de si s'ha activat la predicció.
- **Mode Estació Local**: La condició per defecte es basa en la **Predicció Diària** d'aquell municipi.
  - Si **desactives la predicció diària**, l'entitat weather no podrà determinar la condició global i la icona pot sortir en blanc i negre (estat desconegut/generic), llevat que hagis configurat una entitat local per a la condició ("Condició del cel") a les opcions.
  - Per garantir que la icona es mostri correctament en mode Local sense sensors personalitzats, es recomana mantenir activada la Predicció Diària.

## Entitats

- **Botons d'actualització**: Els botons "Actualitzar Mesures" i "Actualitzar Predicció" ara sempre mostren una icona.

## Opcions avançades

- **URL de l'API**: Quan configures una URL de proves, la integració utilitza aquesta URL per a totes les crides, mai la real si no està configurada.

## Traduccions

- Totes les pantalles, inclòs el nou pas de mapeig, estan traduïdes a català, castellà i anglès.

## Versionat

- La versió actual del manifest és `1.2.68` i coincideix amb l'últim tag de git.

## Tests

- La lògica de la pantalla de mapeig, la configuració, els botons i la gestió de l'API estan coberts per tests automàtics.

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

#### Mode Estació Local (Mesures locals i predicció de Meteocat)

> ⚠️ **Important:** Aquest mode està pensat **exclusivament** per a usuaris que tenen una **estació meteorològica local** (Davis, Netatmo, Ecowitt, etc.) i volen complementar-la amb les **prediccions horàries i diàries oficials** de Meteocat. Si no tens cap estació meteorològica local a Home Assistant, fes servir el **Mode Estació** que et proporcionarà tant dades de monitorització com de prediccions.

Aquest mode crea sensors amb les prediccions en els seus atributs, permetent-te utilitzar-les en entitats `weather.template` personalitzades que combinin dades de la teva estació local amb prediccions oficials.

1. A Home Assistant, ves a **Configuració** → **Dispositius i Serveis**
2. Fes clic a **Afegir integració**
3. Cerca **Meteocat (Community Edition)**
4. Introdueix la teva **clau API**
5. Selecciona **"Predicció municipal"**
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

Per configurar un endpoint personalitzat, modificar les hores d'actualització o canviar el mapping de condicions climàtiques:

1. Ves a **Configuració** → **Dispositius i Serveis**
2. Troba **Meteocat (Community Edition)**
3. Fes clic als 3 punts → **Opcions**
4. Modifica:
   - **URL base de l'API** (deixa valor per defecte o buit per a producció)
   - **Hores d'actualització** (format 24h: HH:MM)
   - **Tipus de mapeig de la condició climàtica** (només en Mode Estació Local)

### Configuració del mapping de condicions climàtiques (Mode Estació Local)

En **Mode Estació Local**, pots personalitzar com es determina la **condició climàtica** (l'icona que es mostra a la targeta del temps) de l'entitat `weather`.

#### Tipus de mapping disponibles

1. **Automàtic (Meteocat)** *(per defecte)*
   - La condició s'agafa directament de la predicció oficial del Meteocat
   - No requereix cap configuració addicional
   - Sempre mostra una condició vàlida basada en dades oficials

2. **Personalitzat**
   - Defineix el teu propi mapeig entre valors del teu sensor local i condicions de Home Assistant
   - Útil quan tens sensors que reporten valors numèrics (0, 1, 2...) que representen condicions
   - Permet integrar sensors personalitzats (ESPHome, etc.) amb lògica pròpia

#### Com configurar el mapping personalitzat

##### Primera configuració (durant la creació)

Quan configures una nova estació local:

1. Selecciona **"Predicció municipal"**
2. Selecciona la **comarca** i **municipi**
3. A la pantalla **"Tipus de mapeig de la condició climàtica"**, selecciona **"Personalitzat"**
4. **Selecciona el sensor** que conté el valor de condició (obligatori)
5. **Configura el mapeig** per a cada condició:
   - Apareixerà un formulari amb totes les condicions meteorològiques suportades per Home Assistant (Sunny, Cloudy, Rainy, etc.).
   - Per a cada condició, introdueix el valor (o valors) que retorna el teu sensor quan es dona aquesta condició.
   - Si el teu sensor retorna diversos valors per a una mateixa condició, separa'ls per comes (exemple: `1, 2` o `soleado, despejado`).
   - Els camps es poden deixar buits si el teu sensor no suporta algunes condicions.

> ℹ️ Les condicions disponibles corresponen als [valors estàndard de Home Assistant](https://developers.home-assistant.io/docs/core/entity/weather/#weather-conditions).

##### Editar mapping existent

Per modificar el mapping d'una estació ja configurada:

1. Ves a **Configuració** → **Dispositius i Serveis**
2. Troba la teva integració **Meteocat (Community Edition)**
3. Fes clic als 3 punts → **Opcions**
4. A **"Tipus de mapeig de la condició climàtica"**, canvia entre **"Meteocat"** o **"Personalitzat"**
5. Si selecciones **"Personalitzat"**, apareixerà la pantalla de configuració del mapping
6. Modifica el **sensor** i/o el **mapeig** segons calgui

> **💡 Consell**: Quan edites un mapping existent, l'edició acaba directament sense tornar als sensors, ja que ja està tot configurat.

#### Format del mapeig personalitzat

A la pantalla de configuració, apareixerà un formulari amb un camp per a cada condició climàtica suportada per Home Assistant.

- **Camps**: Cada camp correspon a una condició (ex: assolellat, plujós, etc.).
- **Valors**: Introdueix el valor numèric (o text) que el teu sensor local envia per a aquella condició.
- **Múltiples valors**: Si el teu sensor envia diferents valors per a una mateixa condició, separa'ls per comes (ex: `1, 2`).
- **Valors buits**: Deixa el camp buit si el teu sensor no suporta aquella condició.

**Exemple de configuració**:
Si el teu sensor retorna `0` per a "Clar (nit)" i `1` per a "Assolellat":
- Camp **clear-night**: `0`
- Camp **sunny**: `1`
- Camp **partlycloudy**: `2`
- Camp **cloudy**: `3`
- Camp **rainy**: `4`
- ...


#### Comportament quan no es pot determinar la condició

Si el valor del sensor no té una correspondència al mapeig, o si hi ha algun error:

- **La targeta del temps mostra**: "unknown" amb icona genèrica (blanc i negre)
- **Això és el comportament correcte** i indica que cal revisar la configuració del mapping
- **No es mostra cap icona de color** per evitar mostrar informació incorrecta

#### Canviar entre tipus de mapping

Pots canviar lliurement entre **"Meteocat"** i **"Personalitzat"** en qualsevol moment:

- **De Meteocat a Personalitzat**: Apareix la pantalla de configuració del mapping
- **De Personalitzat a Meteocat**: S'eliminen les dades de mapping personalitzat i es torna al comportament per defecte

## Entitats

La integració crea diferents entitats segons el mode configurat:

### Mode Estació Externa (Mesures i predicció de Meteocat)

Aquest mode està pensat per obtenir dades d'una estació meteorològica oficial del Meteocat.

**Dispositiu**: `{Nom Estació} {Codi}` (ex: "Barcelona - Raval YM")

| Tipus | Entitat | Descripció |
|-------|---------|------------|
| **Weather** | `weather.{estacio}_{codi}` | Entitat principal. Mostra l'estat actual (temperatura, humitat, vent, pressió, pluja) obtingut de l'estació XEMA i la predicció (horària i diària) del municipi on es troba l'estació. |
| **Sensor** | `sensor.{estacio}_{codi}_precipitation` | Precipitació diària acumulada (mm) (Si l'estació en disposa). |
| **Sensor** | `sensor.{estacio}_{codi}_utci_index` | Índex UTCI (Sensació tèrmica). Només disponible si l'estació té Temperatura, Humitat i Vent. |
| **Sensor** | `sensor.{estacio}_{codi}_utci_literal` | Estat de Confort Tèrmic. Text i icona que indica el nivell d'estrès tèrmic basat en l'UTCI. |
| **Sensor** | `sensor.{estacio}_{codi}_beaufort_index` | Índex Beaufort (0-17). Només disponible si l'estació té Vent. |
| **Sensor** | `sensor.{estacio}_{codi}_beaufort_description` | Descripció Beaufort. Text que descriu la força del vent segons l'escala. |
| **Sensor** | `sensor.{estacio}_{codi}_quota_disponible_{pla}` | Un sensor per a cada pla de quotes rellevant (Predicció, XEMA). Mostra les peticions restants. |
| **Binary Sensor** | `binary_sensor.{estacio}_{codi}_update_state` | Indica l'estat de l'última actualització (`OFF` = Correcte, `ON` = Error). |
| **Sensor** | `sensor.{estacio}_{codi}_last_update` | Timestamp de l'última actualització de mesures (horària). |
| **Sensor** | `sensor.{estacio}_{codi}_next_update` | Timestamp de la pròxima actualització de mesures (horària). |
| **Sensor** | `sensor.{estacio}_{codi}_last_forecast_update` | Timestamp de l'última actualització de predicció. |
| **Sensor** | `sensor.{estacio}_{codi}_next_forecast_update` | Timestamp de la pròxima actualització de predicció programada. |
| **Sensor** | `sensor.{estacio}_{codi}_update_time_{n}` | Mostra les hores d'actualització de predicció configurades (ex: 06:00, 14:00). |
| **Sensor** | `sensor.{estacio}_{codi}_altitude` | Altitud de l'estació (metres). |
| **Sensor** | `sensor.{estacio}_{codi}_latitude` | Latitud de l'estació. |
| **Sensor** | `sensor.{estacio}_{codi}_longitude` | Longitud de l'estació. |
| **Sensor** | `sensor.{estacio}_{codi}_comarca_name` | Nom de la comarca. |
| **Sensor** | `sensor.{estacio}_{codi}_municipality_name` | Nom del municipi (si disponible). |
| **Sensor** | `sensor.{estacio}_{codi}_provincia_name` | Nom de la província (si disponible). |
| **Button** | `button.{estacio}_{codi}_refresh` | Botó per forçar una actualització manual immediata. |

### Mode Estació Local (Mesures locals i predicció de Meteocat)

Aquest mode està pensat per a usuaris que tenen una estació meteorològica pròpia (Netatmo, Ecowitt, ESPHome, etc.) integrada a Home Assistant.

Permet crear una entitat `weather` que combina:
1. **Dades actuals**: Dels teus sensors locals (Temperatura, Humitat, Pressió, Vent, Intensitat de Pluja).
2. **Predicció**: Oficial del Meteocat per al teu municipi.

> **Nota sobre la pluja**: Si configures el sensor d'**Intensitat de Pluja**, l'entitat mostrarà l'estat "Plujós" quan detecti precipitació. Si no plou, mostrarà la predicció de Meteocat (ex: "Sol", "Ennuvolat").

**Dispositiu**: `{Nom Municipi}` (ex: "Barcelona")

| Tipus | Entitat | Descripció |
|-------|---------|------------|
| **Weather** | `weather.{municipi}` | Entitat principal. Mostra l'estat actual (dels teus sensors) i la predicció (del Meteocat). Si la condició climàtica no es pot determinar, mostra "unknown" amb icona genèrica. |
| **Sensor** | `sensor.{municipi}_utci_index` | Temperatura UTCI (Sensació tèrmica). Només disponible si has configurat Temperatura, Humitat i Vent locals. |
| **Sensor** | `sensor.{municipi}_utci_literal` | Estrès tèrmic. Text i icona que indica el nivell d'estrès tèrmic basat en l'UTCI. |
| **Sensor** | `sensor.{municipi}_beaufort_index` | Índex Beaufort (0-17). Només disponible si has configurat Vent local. |
| **Sensor** | `sensor.{municipi}_beaufort_description` | Descripció Beaufort. Text que descriu la força del vent segons l'escala. |
| **Sensor** | `sensor.{municipi}_prediccio_horaria` | L'estat mostra les hores disponibles. Els atributs contenen la predicció completa per a 72h. |
| **Sensor** | `sensor.{municipi}_prediccio_diaria` | L'estat mostra els dies disponibles. Els atributs contenen la predicció completa per a 8 dies. |
| **Sensor** | `sensor.{municipi}_quota_disponible_{pla}` | Un sensor per a cada pla de quotes rellevant (Predicció). Mostra les peticions restants. |
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

> **Nota:** Durant la configuració, se't demanarà que seleccionis els sensors de la teva estació local per alimentar l'entitat `weather`.

### Valors de Temperatura UTCI (Estrès Tèrmic)

El sensor "Estrès tèrmic" mostra un text i una icona segons el valor de la temperatura UTCI.

**Mètode de càlcul (v1.2.82+)**:
El càlcul de la temperatura UTCI utilitza l'estàndard científic basat en el **polinomi de regressió de sisè grau de Bröde et al. (2012)**. Aquest mètode integra:
- Temperatura de l'aire ($T_a$)
- Humitat relativa (RH) i pressió de vapor ($P_a$)
- Velocitat del vent a 10m ($v_{10m}$, ajustada des de l'alçada del sensor)

A diferència de fórmules simplificades, aquest model capta millor les interaccions complexes entre humitat i vent, especialment en condicions de fred. *Nota: S'assumeix $T_{mrt} \approx T_a$ (condicions d'ombra).*

| Rang UTCI (ºC) | Estat | Icona |
|-----------|-------|-------|
| > 46 | Estrès extrem per calor | `thermometer-alert` |
| 38 a 46 | Estrès molt fort per calor | `thermometer-alert` |
| 32 a 38 | Estrès fort per calor | `thermometer-alert` |
| 26 a 32 | Estrès moderat per calor | `thermometer-alert` |
| 9 a 26 | Confort (Sense estrès) | `check-circle-outline` |
| 0 a 9 | Estrès moderat per fred | `snowflake-alert` |
| -13 a 0 | Estrès fort per fred | `snowflake-alert` |
| -27 a -13 | Estrès molt fort per fred | `snowflake-alert` |
| < -27 | Estrès extrem per fred | `snowflake-alert` |

### Escala Beaufort (Vent)

A més de la velocitat del vent en km/h, la integració ofereix l'escala Beaufort (0-17) i la seva descripció associada. Aquesta escala és útil per entendre els efectes del vent en mar i terra.

**Nota**: Encara que l'escala tradicional arriba fins a 12 (Huracà), aquesta integració suporta l'escala ampliada fins a 17, utilitzada en meteorologia extrema.

| Índex | Descripció | km/h (aprox) |
|-------|------------|--------------|
| 0 | Calma | < 1 |
| 1 | Ventolina | 1 - 5 |
| 2 | Fluixet (Brisa molt feble) | 6 - 11 |
| 3 | Fluix (Brisa feble) | 12 - 19 |
| 4 | Bonancible (Brisa moderada) | 20 - 28 |
| 5 | Fresquet (Brisa fresca) | 29 - 38 |
| 6 | Fresc (Brisa forta) | 39 - 49 |
| 7 | Frescàs (Vent fort) | 50 - 61 |
| 8 | Temporal (Vent molt fort) | 62 - 74 |
| 9 | Temporal fort | 75 - 88 |
| 10 | Temporal molt fort | 89 - 102 |
| 11 | Temporal violent | 103 - 117 |
| 12+ | Huracà | > 117 |

## Actualització de dades

### 📊 Sistema d'actualitzacions programades

La integració està **optimitzada per estalviar quota de l'API** i assegurar que arribes a final de mes sense problemes, però mantenint les dades de l'estació actualitzades.

#### Comportament del sistema

Les dades s'actualitzen de la següent manera:

1. **Dades de l'estació (XEMA)**: S'actualitzen **cada hora** (al minut 0).
2. **Prediccions i Quotes**: S'actualitzen **NOMÉS** a les hores programades (per defecte a les **06:00** i **14:00**).
3. **Manualment**: Quan prems el botó "Actualitzar dades" (s'actualitza tot).

#### Consum de quota per actualització

**Mode Estació (XEMA)**:
- **Cada hora**: 1 crida (measurements + quotes)
- **A les hores de predicció**: 3 crides addicionals (forecast + hourly + quotes)
- **Mitjana diària**: ~30 crides (24 hores × 1 + 2 prediccions × 3)

**Mode Estació Local**:
- **A les hores de predicció**: 3 crides (forecast + hourly + quotes)
- **Mitjana diària**: ~6 crides (2 programades × 3)

#### Càlcul mensual (30 dies)

| Mode | Crides/dia | Crides/mes | Quota restant* | Actualitzacions manuals disponibles |
|------|-----------|-----------|----------------|-------------------------------------|
| **Estació XEMA** | ~30 | ~900 | ~100 | ~3/dia (100÷30) |
| **Estació Local** | ~6 | ~180 | ~820 | ~27/dia (820÷30) |

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
- Consumeix quota de l'API (5 crides en mode Estació XEMA, 4 en mode Estació Local)
- Útil per obtenir dades fresques abans d'un esdeveniment o viatge

## Esdeveniments

Cada entrada de la integració dispara un **esdeveniment** (`meteocat_community_edition_data_updated`) cada cop que s'actualitzen les dades, tant si és una actualització automàtica programada com si és manual (via botó).

Aquest esdeveniment conté la següent informació:

- **`mode`**: Mode de l'entrada (`external` o `local`)
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
          mode: external
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
          mode: local
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

## Detall dels sensors de predicció

Tant en el **Mode Estació XEMA** com en el **Mode Estació Local**, es creen sensors addicionals amb les dades de predicció en brut. Això és útil si vols crear targetes personalitzades o automatitzacions avançades.

### Sensors disponibles

- **`sensor.{municipi}_prediccio_horaria`**: Predicció de les pròximes 72 hores
- **`sensor.{municipi}_prediccio_diaria`**: Predicció dels pròxims 8 dies  
- **`sensor.{municipi}_quota_{pla}`**: Consums API (Predicció)
- **`binary_sensor.{municipi}_update_state`**: Estat de l'última actualització predicció (OFF=OK, ON=Error)
- **`sensor.{municipi}_last_update`**: Darrera actualització
- **`sensor.{municipi}_next_update`**: Pròxima actualització programada
- **`button.{municipi}_refresh`**: Botó per actualitzar manualment

### Accedir a les dades de predicció

Els sensors emmagatzemen les prediccions completes als seus **atributs**:

#### Predicció horària (`sensor.{municipi}_prediccio_horaria`)

L'estat del sensor mostra el nombre d'hores disponibles (ex: "72 hores").

Atributs disponibles:
```yaml
# Accedir a totes les dades de predicció horària (Format original API Meteocat)
{{ state_attr('sensor.barcelona_prediccio_horaria', 'forecast') }}

# Accedir a les dades en format Home Assistant (llest per weather.template)
{{ state_attr('sensor.barcelona_prediccio_horaria', 'forecast_ha') }}

# Exemple: accedir a les temperatures d'avui (Format original)
{{ state_attr('sensor.barcelona_prediccio_horaria', 'forecast').dies[0].variables.temp.valors }}
```

#### Predicció diària (`sensor.{municipi}_prediccio_diaria`)

L'estat del sensor mostra el nombre de dies disponibles (ex: "8 dies").

Atributs disponibles:
```yaml
# Accedir a totes les dades de predicció diària (Format original API Meteocat)
{{ state_attr('sensor.barcelona_prediccio_diaria', 'forecast') }}

# Accedir a les dades en format Home Assistant (llest per weather.template)
{{ state_attr('sensor.barcelona_prediccio_diaria', 'forecast_ha') }}

# Exemple: temperatura màxima de demà
{{ state_attr('sensor.barcelona_prediccio_diaria', 'forecast').dies[1].variables.tmax.valor }}
```

### Crear targetes personalitzades

Utilitza aquestes dades per crear targetes al teu dashboard:

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## Predicció horària - {{ state_attr('sensor.barcelona_prediccio_horaria', 'forecast').nom }}
      
      **Available:** {{ states('sensor.barcelona_prediccio_horaria') }}
      
      {% set forecast = state_attr('sensor.barcelona_prediccio_horaria', 'forecast') %}
      {% if forecast and forecast.dies %}
        {% for dia in forecast.dies[:2] %}
        ### {{ dia.data }}
        Temperature: {{ dia.variables.temp.valors[:6] | join(', ') }}°C
        {% endfor %}
      {% endif %}

  - type: markdown
    content: |
      ## Predicció diària - Next days
      
      **Available:** {{ states('sensor.barcelona_prediccio_diaria') }}
      
      {% set forecast = state_attr('sensor.barcelona_prediccio_diaria', 'forecast') %}
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

Cada entrada de la integració crea **sensors de quotes** que mostren les peticions disponibles dels plans rellevants (Predicció i XEMA), filtrant aquells que no s'utilitzen (Referència, XDDE).

Aquesta integració està optimitzada per minimitzar l'ús:
- Només 2 actualitzacions automàtiques al dia (6:00 i 14:00)
- Les quotes es consulten **després** de les altres APIs per comptabilitzar correctament
- Els sensors de quotes et permeten monitoritzar l'ús en temps real

#### 💡 **Múltiples API Keys per maximitzar l'ús**

Degut a que el **pla domèstic** permet poques consultes al mes, el sistema permet crear **diverses estacions amb API keys diferents** per poder **exprimir les limitacions de l'API**.

**Avantatges:**
- Cada estació utilitza la seva pròpia quota independent
- Pots monitoritzar l'ús de cada API key per separat
- Ideal per usuaris amb múltiples estacions o necessitats elevades de dades

**Com fer-ho:**
1. Registra múltiples comptes a l'API de Meteocat (cada compte té la seva quota independent)
2. Afegeix cada estació amb una API key diferent
3. Utilitza els sensors de quotes per controlar l'ús de cada compte

**Consell**: Si necessites més peticions, pots crear múltiples entrades amb diferents API Keys.

### Altres limitacions

- Les prediccions municipals depenen de la disponibilitat a l'API de Meteocat
- En **Mode Estació Externa**, algunes estacions poden no tenir municipi associat per a prediccions
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




