# Tests de Meteocat Community Edition

## 🎯 Objectiu: Home Assistant Silver Level + HACS

Aquesta integració té com a objectiu:

- 🏆 **Home Assistant Silver Level**: Cobertura de codi > 95%
- ✅ **Validació HACS**: Complir tots els requisits per ser acceptada
- ✅ **Tests comprehensius** per totes les funcionalitats
- ✅ **Validació Hassfest** sense errors
- ✅ **GitHub Actions CI/CD** configurats

**Estat actual**: **192 tests**, **>95% cobertura** ✅

Quan desenvolupis noves funcionalitats o facis canvis:
1. Afegeix tests que cobreixin **tots els casos** (happy path + edge cases)
2. Verifica que la cobertura es mantingui **>95%**
3. Assegura't que **tots els tests passen**

---

## Instal·lació de dependències

Per executar els tests, necessites instal·lar Home Assistant i les dependències de test:

```bash
pip install homeassistant
pip install -r requirements-test.txt
```

### ⚠️ Limitació important en Windows

**Els tests NO funcionen en Windows** perquè Home Assistant depèn del mòdul `fcntl` que només està disponible en sistemes Linux/Unix. Això és una limitació coneguda de Home Assistant, no d'aquesta integració.

**Solucions per executar els tests:**
1. **Utilitzar WSL2 (Windows Subsystem for Linux)** - recomanat
2. **Utilitzar GitHub Actions** - els tests s'executen automàticament al CI/CD
3. **Utilitzar un entorn Linux** (màquina virtual, contenidor Docker, etc.)

**Proves manuals en Windows:**
- Instal·la la integració directament a la teva instància de Home Assistant
- Verifica manualment totes les funcionalitats (veure secció "Proves manuals recomanades" més avall)

## Executar tots els tests

```bash
pytest tests/
```

## Executar tests específics

```bash
# Tests de sensors
pytest tests/test_sensor.py -v

# Tests de l'API
pytest tests/test_api.py -v

# Tests del botó
pytest tests/test_button.py -v

# Tests del coordinator
pytest tests/test_coordinator.py -v

# Tests d'agrupació de dispositius
pytest tests/test_device_grouping.py -v

# Tests de configuració
pytest tests/test_config_flow.py -v
```

## Executar un test concret

```bash
pytest tests/test_sensor.py::test_quota_sensor_normalizes_plan_names -v
```

## Tests amb cobertura

```bash
pytest tests/ --cov=custom_components.meteocat_community_edition --cov-report=html
```

## Tests principals

### test_sensor.py
- `test_quota_sensor_normalizes_plan_names`: Verifica que els noms dels plans es normalitzen correctament (Predicció, Referència, XDDE, XEMA)
- `test_quota_sensor_entity_id_xema_mode`: Verifica que els entity_id inclouen el codi d'estació en mode XEMA
- `test_quota_sensor_entity_id_municipal_mode`: Verifica que els entity_id són correctes en mode Municipal
- `test_quota_sensor_device_info`: Verifica que els sensors usen el device_name correcte per agrupar-se
- `test_forecast_sensor_daily`: Verifica el sensor de temperatura màxima
- `test_forecast_sensor_hourly`: Verifica el sensor de temperatura horària
- `test_uv_sensor`: Verifica el sensor d'índex UV
- `test_last_update_sensor`: Verifica el sensor de darrera actualització
- `test_next_update_sensor`: Verifica el sensor de pròxima actualització (usa coordinator.next_scheduled_update)
- `test_timestamp_sensors_device_info`: Verifica que els sensors de timestamp s'agrupen correctament
- `test_station_comarca_name_sensor`: Verifica sensor de comarca en mode estació
- `test_station_municipality_name_sensor`: Verifica sensor de municipi en mode estació
- `test_station_provincia_name_sensor`: Verifica sensor de província en mode estació
- `test_municipality_latitude_sensor`: Verifica sensor de latitud en mode municipi
- `test_municipality_longitude_sensor`: Verifica sensor de longitud en mode municipi
- `test_municipality_provincia_name_sensor`: Verifica sensor de província en mode municipi

### test_sensor_setup.py
- `test_station_mode_creates_all_geographic_sensors_when_data_available`: Verifica creació de sensors geogràfics en mode estació
- `test_station_mode_skips_municipality_when_not_available`: Verifica omissió de sensors opcionals sense dades
- `test_municipality_mode_creates_all_sensors_when_data_available`: Verifica creació de sensors en mode municipi
- `test_municipality_mode_skips_coordinates_when_not_available`: Verifica omissió de coordenades opcionals
- `test_municipality_mode_creates_lat_without_lon`: Verifica creació independent de lat/lon

### test_binary_sensor.py (19 tests)
- `test_binary_sensor_initialization_station_mode`: Verifica inicialització en mode estació amb device class problem
- `test_binary_sensor_initialization_municipality_mode`: Verifica inicialització en mode municipi
- `test_binary_sensor_success_state`: Verifica estat OFF quan actualització exitosa (lògica invertida: OFF = no problem)
- `test_binary_sensor_failure_state`: Verifica estat ON quan actualització falla (ON = problem detected)
- `test_binary_sensor_no_data`: Verifica estat ON quan no hi ha dades (problem)
- `test_binary_sensor_station_mode_requires_measurements_or_forecast`: Verifica detecció de problemes en mode estació
- `test_binary_sensor_municipality_mode_requires_forecast`: Verifica detecció de problemes en mode municipi
- `test_binary_sensor_quota_exhausted_station_mode`: Verifica detecció de quotes exhaurides en mode estació
- `test_binary_sensor_quota_exhausted_municipality_mode`: Verifica detecció de quotes exhaurides en mode municipi
- `test_binary_sensor_always_available`: Verifica disponibilitat constant fins i tot quan coordinator falla
- `test_binary_sensor_device_info_station_mode`: Verifica informació de dispositiu en mode estació
- `test_binary_sensor_device_info_municipality_mode`: Verifica informació de dispositiu en mode municipi
- `test_binary_sensor_icon_when_ok`: Verifica icona check-circle quan no hi ha problemes
- `test_binary_sensor_icon_when_problem`: Verifica icona alert-circle quan hi ha problemes
- `test_binary_sensor_attributes_when_ok`: Verifica atributs correctes en estat ok
- `test_binary_sensor_attributes_when_error`: Verifica atributs amb missatges d'error específics
- `test_binary_sensor_device_class_is_problem`: Verifica device_class és PROBLEM
- `test_binary_sensor_entity_category_is_diagnostic`: Verifica entity_category és DIAGNOSTIC
- `test_binary_sensor_translation_key`: Verifica translation_key correcte per a traduccions
- **Lògica**: ON = problema detectat (inclou quotes exhaurides), OFF = sense problemes
- **Device class**: problem (no connectivity)
- **Detecció intel·ligent**: Comprova disponibilitat de dades, no només success flag

### test_quota_exhausted_setup.py
- `test_estacio_first_refresh_tolerates_missing_measurements`: Verifica setup MODE_ESTACIO amb quotes exhaurides
- `test_estacio_subsequent_update_fails_without_measurements`: Verifica fallada en updates posteriors sense dades
- `test_estacio_first_refresh_tolerates_missing_forecasts`: Verifica tolerància a forecasts mancants
- `test_municipi_first_refresh_tolerates_missing_forecasts`: Verifica setup MODE_MUNICIPI amb quotes exhaurides
- `test_municipi_subsequent_update_fails_without_forecasts`: Verifica fallada en updates posteriors
- `test_is_first_refresh_flag_resets_after_successful_update`: Verifica reset del flag _is_first_refresh
- `test_is_first_refresh_flag_resets_even_with_missing_data`: Verifica reset del flag amb dades mancants

### test_button.py
- `test_button_entity_id_xema_mode`: Verifica que el botó té entity_id correcte en mode XEMA
- `test_button_entity_id_municipal_mode`: Verifica que el botó té entity_id correcte en mode Municipal
- `test_button_device_info_xema`: Verifica que el botó s'agrupa correctament en mode XEMA
- `test_button_press_triggers_refresh`: Verifica que el botó dispara l'actualització

### test_device_grouping.py
- `test_all_entities_share_same_device_identifier`: Verifica que totes les entitats comparteixen el mateix identificador de dispositiu
- `test_all_entities_share_same_device_name`: Verifica que totes les entitats usen el mateix nom de dispositiu ("Granollers YM" en Mode Estació)
- `test_entity_ids_include_station_code`: Verifica que tots els entity_id inclouen el codi de l'estació

### test_api.py
- `test_get_comarques`: Verifica la crida a comarques
- `test_get_stations`: Verifica la crida a estacions
- `test_api_error_handling`: Verifica el maneig d'errors
- `test_get_station_measurements`: Verifica la crida a mesures d'estació
- `test_get_quotes`: Verifica la crida a quotes/consums
- `test_get_municipal_forecast`: Verifica la crida a Predicció municipal
- `test_get_uv_index`: Verifica la crida a índex UV

### test_coordinator.py
- `test_coordinator_xema_mode_update`: Verifica l'actualització en mode XEMA
- `test_coordinator_municipal_mode_update`: Verifica l'actualització en mode Municipal
- `test_coordinator_calculates_next_update`: Verifica el càlcul de la pròxima actualització
- `test_coordinator_handles_api_error`: Verifica el maneig d'errors de l'API
- `test_coordinator_quotes_fetched_after_other_apis`: Verifica que quotes es criden després de les altres APIs
- `test_coordinator_handles_missing_quotes`: Verifica que continua funcionant si quotes falla
- `test_coordinator_finds_municipality_for_station`: Verifica que troba el codi de municipi per l'estació

### test_config_flow.py
- Tests bàsics de constants i configuració
- **Nota**: Els tests complets del config flow requereixen Home Assistant instal·lat

## Proves manuals recomanades

A Windows, la millor opció és **provar la integració directament a Home Assistant**:

1. Copia la carpeta `custom_components/meteocat_community_edition` al teu Home Assistant
2. Reinicia Home Assistant
3. Afegeix la integració des de la UI
4. Comprova especialment:
   - Tots els sensors d'una estació s'agrupen sota un únic dispositiu amb nom "Estació YM" (o el nom que sigui)
   - Els entity_id inclouen el codi d'estació (per exemple: `sensor.granollers_ym_quota_prediccio`)
   - Els noms dels sensors de quota són nets: "Peticions disponibles Predicció"
   - El botó "Actualitzar dades" actualitza immediatament el timestamp
   - Els sensors de timestamp mostren "fa X segons/minuts"

## Notes

- Els tests són unit tests que verifiquen la lògica del codi sense necessitar una instància real de Home Assistant executant-se
- Es fan servir mocks per simular les respostes de l'API
- Els tests verifiquen especialment:
  - Normalització de noms de plans de quotes
  - Agrupació correcta de dispositius (tots sota "Granollers YM")
  - Entity IDs únics amb codi d'estació
  - Noms de dispositiu amb codi vs noms d'entitat sense codi
  - Timestamp capturats al moment correcte
