# Changelog

Tots els canvis notables del projecte es documenten aquí.

El format es basa en [Keep a Changelog](https://keepachangelog.com/ca/1.0.0/),
i el projecte segueix [Semantic Versioning](https://semver.org/lang/ca/).

## [1.2.5] - 2025-12-11

### Corregit
- **Correcció crítica**: S'arregla error `KeyError: 'municipality_name'` a l'entitat weather local
- L'entitat weather local ara utilitza un nom per defecte quan no hi ha informació de municipi
- S'assegura que la informació de municipi i comarca es guarda sempre als entries del mode local
- S'afegeixen millores de robustesa al config flow per gestionar casos on les dades d'API són incompletes
- **Millora del mode local**: Ara té paritat completa amb el mode extern (sensors disponibles, entitat weather, etc.)
- S'afegeixen logs de debug per ajudar en el diagnòstic de problemes futurs

### Millorat
- Millora de l'experiència d'usuari en mode local amb totes les funcionalitats disponibles
- Config flow més robust per gestionar dades d'API variables

## [1.2.4] - 2025-12-11

### Corregit
- **Correcció crítica**: Millor gestió d'entrades existents sense clau API
- S'afegeixen missatges d'error clars per a entrades antigues que falten la clau API
- S'afegeixen tests de regressió per prevenir que el problema torni a ocórrer
- **Correcció crítica**: S'arregla que les estacions locals es creaven incorrectament com a mode extern
- S'assegura que el camp CONF_MODE s'inclou correctament a totes les entrades de configuració
- S'afegeixen tests de regressió per verificar que el mode es configura correctament

## [1.2.3] - 2025-12-11

### Corregit
- **Correcció crítica**: S'arregla error `KeyError: 'api_key'` que impedia completar la configuració
- S'assegura que l'api_key i api_base_url s'inclouen correctament a les dades d'entrada
- S'afegeixen tests regressius per prevenir que aquest error torni a ocórrer

## [1.2.2] - 2025-12-11

### Millorat
- Millora de l'exemple de mapping personalitzat amb totes les condicions climàtiques de Home Assistant
- Etiquetes de camps obligatoris més clares amb "(obligatori)" als formularis de configuració
- Unificació de la terminologia: canvi d'"Entitat" a "Sensor" per millor consistència
- Experiència d'usuari millorada amb exemples més complets i textos més clars

## [1.2.1] - 2025-12-11

### Millorat
- Millores en les traduccions i textos de la interfície de configuració
- Actualització dels textos de mapeig de condicions climàtiques per millor usabilitat
- Correcció d'icones de botons per utilitzar icones vàlides de Material Design

### Corregit
- Correcció d'errors en la configuració d'estacions externes amb mapeig personalitzat
- Assegurar que les dades d'API es propaguen correctament en totes les configuracions
- Validació de traduccions corregida per complir amb els requisits de Home Assistant

## [1.2.0] - 2025-12-11

### Millorat
- Cobertura de tests significativament millorada (>90%) apropant-se al nivell Silver de Home Assistant
- Tests comprehensius afegits per weather.py, coordinator.py i config_flow.py
- Millores en el tractament d'errors i casos límit en les propietats del temps
- Tests de gestió d'errors d'API i casos de dades faltants

### Corregit
- Correcció de constructors de tests per utilitzar mocks adequats de Home Assistant
- Millores en la gestió de zones horàries en tests de planificació

---

### Afegit
- Millora de la gestió de l'URL de l'API: ara es garanteix que la URL de proves s'utilitza sempre si està configurada.
- Debug logging millorat per traçar totes les crides a l'API i la URL utilitzada.

### Millorat
- Camps requerits (condició, temperatura, humitat) marcats visualment a la UI de configuració.
- Traduccions revisades i errors de JSON corregits.

### Corregit
- Correcció de l'icona del botó "refresh measurements".
- Ordre correcte dels passos del config flow en mode local (mapping després de sensors).
- Cobertura de tests ampliada (302/302 passats).

---
## [1.1.9] - 2025-12-10

### Afegit
- Pantalla de mapping en el config flow per mode local: permet personalitzar la correspondència de condicions meteorològiques.
- Test que verifica que la pantalla de mapping es mostra i que la lògica backend la crida.

### Millorat
- Camps requerits (condició, temperatura, humitat) marcats visualment a la UI de configuració.
- Traduccions revisades i errors de JSON corregits.
- Versió sincronitzada entre manifest i git tag.

### Corregit
- Ordre correcte dels passos del config flow en mode local (mapping després de sensors).
- Cobertura de tests ampliada (302/302 passats).

---
## [1.1.6] - 2025-12-10

### Afegit
- Marcat visual dels camps requerits (condició, temperatura, humitat) a la UI de configuració del temps per plantilla.
- Afegit test de regressió per garantir la correcta serialització de l'ozó.

### Millorat
- Millora de la gestió de l'ozó: ara es mostra com a extra_state_attribute i es serialitza correctament.
- Traduccions i esquema de configuració revisats per compatibilitat amb Home Assistant.

---
## [1.1.5] - 2025-12-10

### Afegit
- Nova pantalla de configuració per a la personalització de la correspondència de condicions meteorològiques (condition mapping) durant el config flow.

### Canviat
- Conversió automàtica de la velocitat del vent a km/h a l'entitat Weather (abans en m/s).

### Corregit
- Millores de robustesa i cobertura de tests per a la lògica de sensors locals i externs, especialment per a la velocitat del vent i la configuració avançada.

---
## [1.0.8] - 2025-12-09

### Corregit
- Afegides claus de traducció faltants per als sensors d'actualització de predicció (`strings.json`).

### Millorat
- Millora significativa de la cobertura de tests (90%).
- Afegits tests per a `api.py`, `button.py`, `coordinator.py` i `sensor.py`.

## [1.0.7] - 2025-12-09

### Afegit
- Sensors separats per al seguiment d'actualitzacions de mesures i prediccions en mode estació
  - 3 sensors per a mesures (horàries): última actualització, pròxima actualització, hora configurada
  - 3 sensors per a predicció (programades): última actualització predicció, pròxima actualització predicció
- Millor visibilitat sobre quan s'actualitzen les dades de l'estació vs les prediccions

### Millorat
- Millora en l'estabilitat dels tests unitaris i de components.
- Correcció de rutes en els fitxers de traducció durant els tests.

## [1.0.6] - 2025-12-09

### Afegit
- Actualitzacions horàries per a les dades de les estacions (temperatura, humitat, etc.).
- Model d'actualització híbrid: prediccions segons horari programat, dades d'estació cada hora.

### Canviat
- En mode estació, les mesures s'actualitzen cada hora mentre que les prediccions segueixen l'horari configurat

## [1.0.5] - 2025-12-09

### Canviat
- Reestructuració del conjunt de tests en carpetes `unit` i `component` per millorar l'organització i l'execució en CI.
- Separació dels workflows de GitHub Actions per a tests unitaris i de components.

## [1.0.4] - 2025-12-08

### Corregit
- Corregit error de traducció en el flux d'opcions on la variable `{measurements_info}` no es proporcionava correctament en mode municipi.
- Corregit problema de visibilitat del camp "Tercera actualització" en el flux de configuració i opcions.

## [1.0.0] - 2025-11-29

Primera versió estable de la integració Meteocat Community Edition per a Home Assistant.

### Afegit

- **Mode Estació (XEMA)**: Integració completa amb estacions meteorològiques XEMA
  - Dades meteorològiques en temps real
  - Entitat Weather amb condicions actuals i prediccions
  - Suport per a múltiples estacions

- **Mode Municipi**: Mode de només prediccions sense estació
  - Sensor de predicció horària (72 hores)
  - Sensor de predicció diària (8 dies)

- **Gestió d'actualitzacions**:
  - Hores d'actualització configurables (per defecte: 06:00 i 14:00)
  - Botó d'actualització manual
  - Sensors de timestamp (última actualització, pròxima actualització)

- **Sistema d'esdeveniments**: Event `meteocat_community_edition_data_updated` en cada actualització
  - Conté mode, codis estació/municipi i timestamp

- **Sensors de quotes API**: Monitoratge en temps real de peticions disponibles
  - Plans suportats: Predicció, Referència, XDDE, XEMA
  - Mostra límit total, peticions utilitzades i data de reset

- **Retry logic amb exponential backoff**:
  - Automàtic en errors de xarxa
  - Màxim 3 retries amb delays creixents (1s, 2s, 4s)
  - Suport per a rate limiting (HTTP 429 amb Retry-After header)

- **Flux de re-autenticació**: Gestió automàtica de claus API expirades
  - ConfigEntryAuthFailed per a casos de credencials invàlides
  - Flux UI per a introduir nova clau sense eliminar la integració

- **Internacionalització**: Traduccions completes en:
  - Català (ca)
  - Castellà (es)
  - Anglès (en)

- **Suite de tests complet**: 200+ tests amb alta cobertura
  - Proves d'API, sensors, configuració, coordinació i retry logic
  - Proves de grupament de dispositius i triggers

- **CI/CD**:
  - GitHub Actions per a Python 3.11 i 3.12
  - pytest, flake8, HACS i Hassfest checks

- **Documentació complet**:
  - READMEs en 3 idiomes
  - Exemple d'automacions i Lovelace dashboard
  - Guies de qualitat i contribució

### Canviat

- Sensor binari d'estat: nom canviat a "Última actualització correcte" per a major claredat
- Entitat del sensor binari: ja no inclou el nom del dispositiu en el seu nom visual
- Sensor de Província: millora per a no crear-se si la dada no està disponible

### Seguretat

- Claus API emmascarades als logs
- Emmagatzematge segur de credencials via config entries de Home Assistant

---

## Plantilla per a futures versions

```
## [X.Y.Z] - YYYY-MM-DD

### Afegit
- Noves funcionalitats

### Canviat
- Canvis en funcionalitats existents

### Deprecat
- Funcionalitats que s'eliminaran aviat

### Eliminat
- Funcionalitats eliminades

### Corregit
- Correccions de bugs

### Seguretat
- Correccions de seguretat
```

