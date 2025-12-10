# Estàndards de Qualitat - Meteocat Community Edition

## 🎯 Objectiu: Home Assistant Silver Level + Validació HACS

Aquesta integració està dissenyada per complir:
- 🏆 **Home Assistant Silver Level** (>95% cobertura de tests)
- ✅ **Requisits de HACS** (validació per ser acceptada)

### Requisits Home Assistant Silver

| Criteri | Requerit | Estat Actual |
|---------|----------|--------------|
| **Cobertura de codi** | >95% | ✅ >95% (102 tests) |
| **Tests comprehensius** | Sí | ✅ 13 fitxers de test |
| **Validació Hassfest** | 0 errors | ✅ Pass |
| **GitHub Actions CI/CD** | Configurat | ✅ Workflows actius |
| **Documentació completa** | Sí | ✅ 3 idiomes |
| **Gestió d'errors** | Robust | ✅ Retry + reauth |

---

## 📊 Cobertura de Tests

### Estat actual

```
Total: 102 tests
Cobertura: >95%
Fitxers de test: 13
Línies de codi de test: 2,443+
```

### Distribució de tests

| Component | Tests | Cobertura |
|-----------|-------|-----------|
| **sensor.py** | 18 | >95% |
| **binary_sensor.py** | 15 | >95% |
| **weather.py** | 15 | >95% |
| **device_trigger.py** | 7 | 100% |
| **__init__.py** | 10 | >95% |
| **coordinator.py** | 7 | >95% |
| **coordinator_granular.py** | 4 | 100% |
| **button.py** | 7 | >95% |
| **api.py** | 7 | >95% |
| **update_times.py** | 10 | >95% |
| **retry_logic.py** | 8 | >95% |
| **reauth.py** | 5 | >95% |
| **events.py** | 5 | >95% |
| **device_grouping.py** | 3 | 100% |
| **config_flow.py** | 1 | Bàsic |

### Àrees cobertes

- ✅ **Sensors**: Quotes, prediccions, timestamps, update times
- ✅ **Binary Sensors**: Estat d'actualització, problemes de quota
- ✅ **Weather entity**: Totes les propietats i edge cases
- ✅ **Device triggers**: Automations per dispositiu
- ✅ **Setup/Unload**: Lifecycle complet
- ✅ **Coordinator**: Actualitzacions en ambdós modes, configuració granular
- ✅ **API client**: Totes les crides amb error handling
- ✅ **Button**: Actualització manual
- ✅ **Events**: Data update events
- ✅ **Retry logic**: Exponential backoff
- ✅ **Reauth**: Re-autenticació sense restart
- ✅ **Device grouping**: Agrupació correcta d'entitats
- ✅ **Entity categories**: Diagnostic sensors correctes
- ✅ **Update Times**: Suport per a 3 hores d'actualització configurables

---

## 🔧 Executar Tests

### Tests bàsics

```bash
pytest tests/ -v
```

### Tests amb cobertura

```bash
# Cobertura en terminal
pytest tests/ -v --cov=custom_components.meteocat_community_edition --cov-report=term-missing

# Cobertura en HTML (detallat)
pytest tests/ --cov=custom_components.meteocat_community_edition --cov-report=html

# Verificar threshold >95%
pytest tests/ --cov=custom_components.meteocat_community_edition --cov-fail-under=95
```

### Tests específics

```bash
# Per fitxer
pytest tests/test_sensor.py -v
pytest tests/test_weather.py -v

# Per test concret
pytest tests/test_sensor.py::test_update_time_sensor_entity_category -v
```

---

## 📋 Checklist per Noves Funcionalitats

Abans de fer un PR amb noves funcionalitats:

### 1. Codi
- [ ] Segueix PEP 8
- [ ] Té docstrings
- [ ] Gestiona errors correctament
- [ ] No hi ha imports no utilitzats
- [ ] Utilitza type hints quan sigui possible

### 2. Tests
- [ ] Afegits tests per **tots els casos d'ús**
- [ ] Coberts **edge cases** (dades buides, errors, etc.)
- [ ] Cobertura total **>95%** mantinguda
- [ ] Tots els tests passen (`pytest tests/ -v`)
- [ ] Tests documentats al README.md de tests

### 3. Documentació
- [ ] README.md actualitzat (català)
- [ ] README.en.md actualitzat (anglès)
- [ ] README.es.md actualitzat (castellà)
- [ ] CHANGELOG.md actualitzat
- [ ] info.md actualitzat si cal
- [ ] Exemples d'ús afegits si escau

### 4. Integració
- [ ] Validació Hassfest passa (`hassfest validate`)
- [ ] GitHub Actions passa (CI/CD)
- [ ] No hi ha warnings de deprecation
- [ ] Compatible amb versions recents de HA

---

## 🎨 Estàndards de Codi

### Python (PEP 8)
- Indentació: 4 espais
- Línia màxima: 100 caràcters (preferiblement 88 per compatibilitat Black)
- Imports ordenats: standard library → third-party → local

### Nomenclatura
- Classes: `PascalCase`
- Funcions/mètodes: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Variables privades: `_leading_underscore`

### Docstrings
```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
    """
```

---

## 🔄 Workflow de Desenvolupament

1. **Fork** del repositori
2. **Branch** per la funcionalitat (`feature/nom-funcionalitat`)
3. **Desenvolupament** amb tests
4. **Verificació local**:
   ```bash
   pytest tests/ -v --cov --cov-fail-under=95
   flake8 custom_components/meteocat_community_edition/
   ```
5. **Commit** amb missatges clars
6. **Push** i **Pull Request**
7. **CI/CD** passa automàticament
8. **Review** i merge

---

## 📈 Millora Contínua

### Objectius futurs
- [ ] Mantenir >95% cobertura sempre
- [ ] Afegir tests d'integració amb HA real
- [ ] Documentar tots els edge cases
- [ ] Millorar tests de config_flow
- [ ] Afegir tests de performance

### Mètriques a monitoritzar
- Cobertura de tests (target: >95%)
- Temps d'execució de tests (target: <2 min)
- Complexitat ciclomàtica (target: <10 per funció)
- Duplicació de codi (target: <3%)

---

## 🤖 Integració amb IA

### Per a GitHub Copilot / Claude / ChatGPT

Aquest projecte està configurat per:
- 🏆 **Mantenir Home Assistant Silver Level** (>95% cobertura)
- ✅ **Complir validació HACS** (requisits per ser acceptada)

Quan suggereixis canvis o nova funcionalitat:

1. **Sempre inclou tests** amb cobertura >95%
2. **Documenta** en els 3 idiomes (CA/EN/ES)
3. **Verifica** que compleix PEP 8
4. **Comprova** que no trenquis tests existents
5. **Gestiona errors** adequadament
6. **Utilitza** les fixtures existents a `conftest.py`
7. **Correcció d'errors**: Tot bug fix ha d'incloure un test de regressió que reprodueixi l'error i verifiqui la solució.

### Context important
- Mode Estació (XEMA): Dades en temps real + prediccions
- Mode Municipal: Només prediccions (per complementar estacions locals)
- Sensors diagnòstic: `EntityCategory.DIAGNOSTIC`
- Device grouping: Totes les entitats sota un únic dispositiu
- Events: `meteocat_community_edition_data_updated`
- Actualitzacions: Fins a 3 cops al dia (configurable)

---

**Última actualització**: 2025-11-25  
**Versió**: 1.0.0  
**Estat**: HA Silver Ready 🏆 | HACS Ready ✅
