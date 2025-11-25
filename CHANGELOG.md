# Changelog

Tots els canvis notables d'aquest projecte es documentaran en aquest fitxer.

El format està basat en [Keep a Changelog](https://keepachangelog.com/ca/1.0.0/),
i aquest projecte segueix [Semantic Versioning](https://semver.org/lang/ca/).

## [1.0.0] - 2025-11-25

### Afegit

#### Funcionalitats principals
- **Mode Estació (Mode XEMA)**: Integració completa amb estacions meteorològiques
  - Dades meteorològiques en temps real
  - Entitat Weather amb condicions actuals i prediccions
  - Suport per múltiples estacions

- **Mode Municipi**: Mode només prediccions sense estació
  - Sensor de predicció horària (72 hores)
  - Sensor de predicció diària (8 dies)
  - Sensor d'índex UV
  - Ideal per usuaris amb estació local que volen prediccions oficials

#### Gestió de dades
- **Hores d'actualització configurables**: Dues actualitzacions diàries personalitzables (per defecte: 06:00 i 14:00)
  - Optimitzat per no superar els límits del pla gratuït
  - Configurable via opcions de la integració
  - Sensors d'hores d'actualització per mostrar configuració

- **Actualització manual**: Botó per forçar actualització immediata

- **Sistema d'esdeveniments**: Event `meteocat_community_edition_data_updated` en cada actualització
  - Conté mode, codis estació/municipi i timestamp
  - Permet automatitzacions avançades

#### Gestió de quotes API
- **Sensors de quotes** per als 4 plans de l'API:
  - Predicció
  - Referència
  - XDDE
  - XEMA
- Monitoratge en temps real de peticions disponibles
- Atributs: límit total, peticions utilitzades, data de reset

#### Sensors de timestamps
- **Última actualització**: Timestamp darrera actualització exitosa
- **Pròxima actualització**: Timestamp pròxima actualització programada

#### Retry i gestió d'errors
- **Retry logic amb exponential backoff**: Retry automàtic en errors de xarxa
  - Màxim 3 retries amb delays creixents (1s, 2s, 4s)
  - Suport per rate limiting (HTTP 429 amb Retry-After header)
  - Sense retry en errors d'autenticació (401/403)

- **Flux de re-autenticació**: Gestió automàtica de claus API expirades
  - Integració amb ConfigEntryAuthFailed
  - Flux UI per introduir nova clau sense eliminar integració
  - Recàrrega automàtica després de re-autenticació exitosa

#### Internacionalització
- Traduccions completes en **català**, **castellà** i **anglès**
- Totes les cadenes UI, noms d'entitats i missatges d'error traduïts
- Selecció de comarca i municipi en idioma local

#### Qualitat i testing
- **GitHub Actions CI/CD**:
  - Testing automàtic en Python 3.11 i 3.12
  - pytest amb informes de cobertura
  - Integració amb Codecov
  - Validació HACS
  - Validació Hassfest
  - Linting amb flake8

- **Suite de tests completa** (38+ tests):
  - Tests unitaris per totes les plataformes (weather, sensor, button, event)
  - Tests de config flow
  - Tests de retry logic (8 tests)
  - Tests de flux de re-autenticació (5 tests)
  - ~85% cobertura de codi

#### Documentació
- READMEs complets en 3 idiomes (ca, en, es)
- Instruccions d'instal·lació detallades (HACS i manual)
- Guies de configuració per ambdós modes
- Exemples:
  - Automatitzacions basades en esdeveniments
  - Sensors template
  - Targetes Lovelace
  - Casos d'ús avançats
- Limitacions de quotes API explicades
- Guia de troubleshooting

#### Suport HACS
- Compatibilitat total amb HACS
- Suport per repositori personalitzat
- Configuració hacs.json
- info.md per UI de HACS

### Detalls tècnics

#### Plataformes
- `weather`: Entitat Weather per Mode Estació
- `sensor`: Prediccions, índex UV, quotes, timestamps, hores actualització
- `button`: Botó d'actualització manual
- `event`: Esdeveniments d'actualització de dades

#### Configuració
- Config flow amb selecció de comarca i estació/municipi
- Options flow per:
  - Endpoint API personalitzat (desenvolupament)
  - Personalització d'hores d'actualització
- Suport per múltiples entrades (diferents API keys)

#### Integració API
- Suport per Meteocat API v1
- Endpoints utilitzats:
  - `/xema/v1/estacions` (llista estacions)
  - `/xema/v1/estacions/{code}/mesurades` (mesures estació)
  - `/referencia/v1/comarques` (comarques)
  - `/referencia/v1/municipis` (municipis)
  - `/prediccio/v1/estacio/{code}` (prediccions estació)
  - `/prediccio/v1/municipi/{code}/horaria` (prediccions horàries)
  - `/prediccio/v1/municipi/{code}/diaria` (prediccions diàries)
  - `/prediccio/v1/uvi/{code}` (índex UV)
  - `/apidquoteslimits/v1/peticions-disponibles` (límits quota)

#### Dependències
- aiohttp >= 3.9.0
- Home Assistant >= 2024.1.0

### Canviat
- N/A (versió inicial)

### Deprecat
- N/A (versió inicial)

### Eliminat
- N/A (versió inicial)

### Corregit
- N/A (versió inicial)

### Seguretat
- Claus API emmascarades als logs
- Emmagatzematge segur de credencials via config entries de Home Assistant

---

## Plantilla per futures versions

```markdown
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

---

[1.0.0]: https://github.com/yourusername/meteocat-community-edition/releases/tag/v1.0.0
