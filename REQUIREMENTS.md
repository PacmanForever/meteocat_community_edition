# Requeriments de Software - Meteocat Community Edition

## 1. Modes d'operació

### 1.1. MODE_EXTERNAL (Mode Estació Externa)
- Configuració basada en estacions meteorològiques XEMA
- Selecció per comarca i estació
- Accés a dades de mesures i prediccions en temps real de l'estació
- **Entitat Weather**: Crea una entitat weather amb les dades de l'estació i prediccions

### 1.2. MODE_LOCAL (Mode Estació Local)
- Configuració basada en municipis
- Selecció per comarca i municipi
- Accés a prediccions horàries i diàries

## 2. Sensors - MODE_EXTERNAL

### 2.1. Sensors de localització
- **Latitud de l'estació**: Coordenada geogràfica (graus)
- **Longitud de l'estació**: Coordenada geogràfica (graus)
- **Altitud de l'estació**: Altitud en metres

### 2.2. Sensors de context geogràfic
- **Comarca**: Comarca on es troba l'estació (sempre disponible)
- **Municipi**: Municipi de l'estació (si disponible a l'API)
- **Província**: Província de l'estació (si disponible a l'API)

### 2.3. Sensors de quota API
- **Peticions disponibles per cada pla**: Mostra consums restants
  - Predicció
  - Referència
  - XDDE
  - XEMA

### 2.4. Sensors de timestamps (Mesures - Horàries)
- **Última actualització**: Timestamp de la darrera actualització de mesures exitosa
  - Font de dades: `coordinator.last_successful_update_time`
- **Pròxima actualització**: Timestamp de la pròxima actualització de mesures programada
  - Font de dades: `coordinator.next_scheduled_update`
  - S'actualitza automàticament quan es programa la pròxima actualització
- Tots els sensors de timestamps són de categoria Diagnostic

### 2.5. Sensors de timestamps (Predicció - Programades)
- **Última actualització predicció**: Timestamp de la darrera actualització de predicció exitosa
  - Font de dades: `coordinator.last_forecast_update`
- **Pròxima actualització predicció**: Timestamp de la pròxima actualització de predicció programada
  - Font de dades: `coordinator.next_forecast_update`
  - S'actualitza automàticament quan es programa la pròxima actualització
- Tots els sensors de timestamps de predicció són de categoria Diagnostic

### 2.6. Sensors d'hores d'actualització
- **Hora actualització 1**: Hora configurada per la primera actualització de predicció
- **Hora actualització 2**: Hora configurada per la segona actualització de predicció
- Tots els sensors són de categoria Diagnostic

### 2.7. Sensor d'estat
- **Última actualització correcte**: Binary sensor de diagnòstic que indica l'estat de l'actualització de dades
  - Categoría: Diagnostic
  - Device class: Problem
  - Lògica: ON = problema detectat (última actualització fallida o dades mancants), OFF = sense problemes (actualització exitosa amb dades)
  - Detecció intel·ligent:
    - Detecta quotes exhaurides (quan update_success=True però no hi ha dades)
    - Detecta errors de xarxa/API
    - Respecta la configuració granular (només alerta si falta una dada habilitada)
    - Missatges d'error específics en atributs
  - Sempre disponible (reporta errors fins i tot quan el coordinator falla)

## 3. Sensors - MODE_LOCAL

### 3.1. Sensors de predicció
- **Predicció horària**: 72 hores de predicció amb dades completes als atributs (si habilitada)
- **Predicció diària**: 8 dies de predicció amb dades completes als atributs (si habilitada)

### 3.2. Sensors de context geogràfic
- **Municipi**: Nom del municipi (sempre disponible)
- **Comarca**: Comarca del municipi (sempre disponible)
- **Latitud del municipi**: Coordenada geogràfica (si disponible a l'API)
- **Longitud del municipi**: Coordenada geogràfica (si disponible a l'API)
- **Província**: Província del municipi (si disponible a l'API)

### 3.3. Sensors de quota API
- Igual que MODE_EXTERNAL

### 3.4. Sensors de timestamps
- Igual que MODE_EXTERNAL

### 3.5. Sensor d'estat
- **Última actualització correcte**: Binary sensor de diagnòstic que indica l'estat de l'actualització de dades
  - Categoría: Diagnostic
  - Device class: Problem
  - Lògica: ON = problema detectat (última actualització fallida o dades mancants), OFF = sense problemes (actualització exitosa amb dades)
  - Detecció intel·ligent:
    - Detecta quotes exhaurides (quan update_success=True però no hi ha dades)
    - Detecta errors de xarxa/API
    - Respecta la configuració granular (només alerta si falta una dada habilitada)
    - Missatges d'error específics en atributs
  - Sempre disponible (reporta errors fins i tot quan el coordinator falla)

## 4. Gestió de quota API

### 4.1. Sistema d'actualitzacions programades
- **Dades d'estació (XEMA)**: Actualització horària (cada hora al minut 0).
- **Prediccions i Quotes**: Actualització programada (per defecte 06:00 i 14:00).
- **NO polling automàtic constant**: update_interval=None, gestió pròpia de la planificació.

### 4.2. Consum estimat de quota
- **MODE_EXTERNAL**:
  - 24 crides/dia per mesures (1 per hora).
  - 3 crides addicionals per cada actualització programada (forecast + hourly + quotes).
- **MODE_LOCAL**:
  - 3 crides per cada actualització programada (forecast + hourly + quotes).
  - No hi ha consum horari.
- **Quotes separades** per cada pla API.

### 4.3. Sistema de retry intel·ligent
- Reintents automàtics en errors temporals (timeout, rate limit)
- **NO** consumeix quota extra: quotes només es consulten en actualització programada
- Retry a 60 segons després d'error temporal
- Màxim 3 reintents per petició

### 4.4. Optimització de quotes
- **Persistència de dades d'estació**: station_data cached a entry.data
  - Estalvia 1 crida get_stations() per cada reinici de HA
  - **Optimització de persistència**: Actualització atòmica de `entry.data` per evitar condicions de carrera i garantir que les dades es guarden correctament, evitant crides innecessàries en actualitzacions posteriors.
- **Dades de configuració**: Noms de municipi, comarca, província desats durant config_flow
  - NO requereixen crides API durant execució
- **Coordenades**: Desades durant configuració inicial
  - MODE_EXTERNAL: coordenades de l'estació
  - MODE_LOCAL: coordenades del municipi (si disponibles)
- **Programació d'actualitzacions**: Propietat `next_scheduled_update` al coordinator
  - Permet al sensor mostrar la pròxima actualització sense càlculs addicionals
  - S'actualitza automàticament quan es programa cada actualització
- **Setup tolerant a quotes exhaurides**: Durant la configuració inicial
  - Si les quotes estan exhaurides, la integració es configura igualment
  - Les dades s'obtindran en la propera actualització programada
  - Evita errors de "Configuració fallida" per límits de quota temporals

## 5. Events personalitzats

### 5.1. Event: meteocat_community_edition_data_updated
Disparat quan s'actualitzen les dades correctament.

**Atributs**:
- `mode`: MODE_EXTERNAL o MODE_LOCAL
- `station_code`: Codi estació (si MODE_EXTERNAL)
- `municipality_code`: Codi municipi
- `timestamp`: Moment de l'actualització
- `previous_update`: Timestamp actualització anterior
- `next_update`: Timestamp propera actualització

### 5.2. Event: meteocat_community_edition_next_update_changed
Disparat quan canvia la pròxima actualització programada.

**Atributs**:
- Igual que event anterior

## 6. Device Triggers

### 6.1. Trigger: data_updated
- S'activa quan es reben dades noves
- Permet automatitzacions basades en actualització de dades

## 7. Configuració

### 7.1. Flux de configuració (config_flow)
1. **API Key**: Clau d'accés a Meteocat API
2. **Tipus d'entrada**: Selecció MODE_EXTERNAL o MODE_LOCAL
3. **Comarca**: Selecció de comarca
4. **Estació/Municipi**: Selecció segons mode
5. **Configuració de dades**: Selecció de predicció diària i/o horària
6. **Hores actualització**: Configuració de fins a 3 hores diàries (format HH:MM)

### 7.2. Dades desades a entry.data
**MODE_EXTERNAL**:
- api_key, mode, station_code, station_name
- comarca_code, comarca_name
- update_time_1, update_time_2, update_time_3
- enable_forecast_daily, enable_forecast_hourly
- station_municipality_code, station_municipality_name (si disponible)
- station_provincia_code, station_provincia_name (si disponible)
- _station_data (cache de coordenades i altitud)

**MODE_LOCAL**:
- api_key, mode, municipality_code, municipality_name
- comarca_code, comarca_name
- update_time_1, update_time_2, update_time_3
- enable_forecast_daily, enable_forecast_hourly
- municipality_lat, municipality_lon (si disponible)
- provincia_code, provincia_name (si disponible)

### 7.3. Opcions configurables
- **API Base URL**: URL de l'API (opcional, per defecte producció)

## 8. Re-autenticació

### 8.1. Gestió d'errors d'autenticació
- Detecta errors 401/403 automàticament
- Marca integració com "reauth required"
- Flow de re-autenticació per actualitzar API key
- Manté la resta de configuració intacta

## 9. Validacions HACS i Home Assistant

### 9.1. HACS
- ✅ Validació hacs.json
- ✅ Campos vàlids: name, content_in_root, country, render_readme, homeassistant
- ✅ NO: iot_class (només a manifest.json)

### 9.2. Hassfest
- ✅ Validació manifest.json
- ✅ Camps vàlids per custom components
- ✅ NO: homeassistant field (només per core integrations)

## 10. Tests

### 10.1. Cobertura de tests
- **Coverage**: >95%
- **Total tests**: >195 tests (verificat amb pytest)

### 10.2. Àrees cobertes
- API client (requests, errors, retry logic)
- Config flow (tots els passos, validacions, errors)
- Coordinator (actualitzacions programades, retry, quota, configuració granular)
- Sensors (tots els tipus, valors, atributs)
- Sensor setup (creació condicional de sensors)
- Binary sensors (estat actualització, diagnostic, detecció ALL API calls)
- Binary sensor: Comprovació de TOTES les crides API segons mode i configuració
  - MODE_EXTERNAL: measurements (obligatori), forecast/forecast_hourly (si hi ha municipality_code i habilitat)
  - MODE_LOCAL: forecast, forecast_hourly (si habilitats)
- Coordinate sensors: Lectura de entry.data._station_data quan coordinator.data buit (quota exhausted)
- Weather entity (MODE_EXTERNAL - totes les propietats)
- Events personalitzats (data_updated, next_update_changed)
- Device triggers (data_updated)
- Re-autenticació (flow sense reinici)
- Persistència de dades (station_data, entry.data)
- Device grouping (identificadors compartits)
- Setup amb quotes exhaurides (tolerància durant configuració inicial)
- Next scheduled update (sensor mostra hora correcta)
- Retry logic (errors temporals, preservació de quota)

### 10.3. GitHub Actions
- **tests.yml**: Executa tots els tests en Python 3.11 i 3.12
- **validate_hacs.yml**: Validació HACS
- **validate_hassfest.yml**: Validació manifest.json

## 11. Qualitat de codi

### 11.1. Documentació
- Docstrings en tots els mòduls, classes i funcions
- Comentaris crítics per lògica complexa
- README complet amb exemples

### 11.2. Estructura
- Separació clara de responsabilitats
- API client separat del coordinator
- Config flow modular
- Constants centralitzades

### 11.3. Gestió d'errors
- Try-except amb logging adequat
- Errors específics (MeteocatAPIError, MeteocatAuthError)
- Fallbacks per dades opcionals
- Validacions d'entrada

## 12. Compatibilitat

### 12.1. Home Assistant
- Versió mínima: 2024.1.0 (especificat a hacs.json)
- Compatible amb arquitectura moderna de HA

### 12.2. Python
- Python 3.11+
- Python 3.12+ (testat)

### 12.3. HACS
- Compatible amb estructura de repositori custom
- Instal·lació via HACS custom repositories

## 13. Internacionalització

### 13.1. Idiomes suportats
- **Català** (ca.json) - Idioma principal
- **Castellà** (es.json)
- **Anglès** (en.json)

### 13.2. Traduccions completes
- Config flow (tots els passos)
- Errors i missatges
- Noms de sensors i entitats


