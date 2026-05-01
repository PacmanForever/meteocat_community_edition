# Copilot Instructions — Meteocat Community Edition

## Projecte

Integració custom de Home Assistant per consumir dades oficials de Meteocat i exposar-les com a entitats `weather`, `sensor`, `button` i `binary_sensor`.

- **Repo**: `PacmanForever/meteocat_community_edition`
- **Domain**: `meteocat_community_edition`
- **Idioma del codi**: anglès (comentaris, docstrings, noms de variables)
- **Idioma de comunicació**: català

## Entorn de desenvolupament

- **OS**: Linux (Debian/Ubuntu)
- **Python**: 3.13
- **Virtualenv**: `venv/` a l'arrel del projecte
- **Tests**: pytest, pytest-asyncio, pytest-cov, pytest-homeassistant-custom-component
- **Cobertura objectiu**: >=95%

## Arquitectura del codi

- `api.py`: Client HTTP de Meteocat, retries, autenticació, decodificació i errors d'API.
- `coordinator.py`: Coordinador central de dades, scheduling d'actualitzacions, quota API i fallback de dades.
- `weather.py`: Entitats `weather` per a mode extern i local. La condició climàtica externa prioritza forecast horari i només cau al diari si està activat.
- `sensor.py`: Sensors de mesures, forecast, quota, timestamps, geogràfics, UTCI i Beaufort.
- `config_flow.py`: Flux de configuració i opcions, amb suport per mode extern/local, predicció horària/diària i mapping de condicions.
- `button.py`: Botons de refresh manual de mesures i predicció.
- `binary_sensor.py`: Sensor diagnòstic d'estat d'actualització.
- `device_trigger.py`: Triggers de dispositiu basats en esdeveniments de dades actualitzades.
- `__init__.py`: Setup/unload d'entrades de configuració i càrrega de plataformes.

## Convencions

- Commits en anglès, format: `vX.Y.Z: brief description`
- Tags: `vX.Y.Z`
- Changelog: format `## [X.Y.Z] - YYYY-MM-DD` amb seccions `### Arreglat`, `### Canviat`, `### Afegit`
- Releases: manualment amb `gh release create` o via GitHub UI
- Sempre executar tots els tests abans de commit o release
- Respostes en català, codi en anglès

## Home Assistant — Patrons del projecte

- `PLATFORMS = [Platform.WEATHER, Platform.SENSOR, Platform.BUTTON, Platform.BINARY_SENSOR]`
- `hass.data[DOMAIN][entry_id]` encara s'utilitza per guardar `MeteocatCoordinator`
- `integration_type` actual al manifest: `service`
- `iot_class`: `cloud_polling`
- La integració fa servir `config_flow`

## Lliçons apreses (no repetir errors)

- **Condició externa**: No usar la variable XEMA `35` com a estat del cel; és precipitació. La condició en mode extern ha de prioritzar `forecast_hourly` i només usar `forecast` diari si està activat.
- **Consum de quota**: Si la predicció diària està desactivada a la configuració, no s'ha d'usar com a fallback de condició ni forçar consum extra.
- **Logs sensibles**: No logar `entry.data` complet ni fragments de l'API key.
- **ConfigEntry**: No mutar `entry.options` directament; usar una variable local amb fallback (`entry.options or {}`).
- **Reauth**: Evitar codi mort o estat residual després de `return self.async_abort(...)`.
- **Weather entity**: Existeix tant en mode extern com en mode local; la documentació i docstrings han d'estar alineats amb això.
- **Actualitzacions**: Respectar el model de scheduling del coordinator per evitar consum innecessari d'API.

## Preferències del projecte

- Prioritzar correcció i consistència sobre canvis cosmètics
- Fer canvis petits i enfocats
- No barrejar canvis aliens en commits o releases funcionals
- No crear fitxers `.md` de resum tret que es demani explícitament

## Validació mínima abans de donar una tasca per acabada

- Executar com a mínim els tests afectats pel canvi
- Si el canvi toca lògica funcional, executar la suite completa:
  - `./venv/bin/python -m pytest tests/component tests/unit -q`
