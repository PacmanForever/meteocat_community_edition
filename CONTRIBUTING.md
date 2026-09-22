# Contributing to Meteocat (Community Edition)

Gràcies per voler contribuir! 🎉

## Com contribuir

### Reportar problemes

Si trobes un error o tens una idea per millorar la integració:

1. Comprova que no existeixi ja un issue similar
2. Crea un nou issue amb:
   - Descripció clara del problema o millora
   - Passos per reproduir (si és un error)
   - Versió de Home Assistant
   - Logs rellevants (si escau)

### Proposar canvis

1. Fork del repositori
2. Crea una branca per la teva característica (`git checkout -b feature/millora-increible`)
3. Fes els canvis i commits (`git commit -am 'Afegeix millora increïble'`)
4. Push a la branca (`git push origin feature/millora-increible`)
5. Obre un Pull Request

### Estàndards de codi

- Segueix PEP 8 per Python
- Afegeix docstrings a funcions i classes
- Escriu tests per noves funcionalitats
- **Sempre afegeix un test de regressió quan arreglis un error**
- Actualitza la documentació si cal

### Tests

**🎯 Objectiu de qualitat: Home Assistant Silver Level + HACS**

Aquesta integració té com a objectiu:
- 🏆 **Home Assistant Silver Level**: Cobertura de codi > 95%
- ✅ **Validació HACS**: Complir requisits per ser acceptada a HACS
- ✅ **Tests comprehensius** per totes les funcionalitats
- ✅ **Validació Hassfest** sense errors
- ✅ **GitHub Actions CI/CD**

Per això, quan afegeixis noves funcionalitats o arreglis errors:
1. **Escriu tests** que cobreixin tots els casos (happy path + edge cases)
2. **Correcció d'errors**: Si arregles un bug, has d'afegir un test que falli sense la correcció i passi amb ella (test de regressió).
3. **Verifica la cobertura** amb `pytest --cov`
4. **Assegura't que tots els tests passen**
5. **No esborris tests**: Si fas tests que poden executar-se en el servidor GitHub i donen cobertura, no els esborris. S'han de mantenir per evitar feina repetida.

### Continuous Integration (CI)

Aquest projecte utilitza GitHub Actions per garantir la qualitat i compatibilitat:

1. **Unit Tests (`tests.yml`)**: S'executa a cada Push/PR. Verifica que el codi funciona amb les versions actuals.
2. **HA Daily Compatibility Check (`daily_compatibility.yml`)**: S'executa diàriament (06:00 UTC). Verifica la compatibilitat amb:
   - L'última versió **Stable** de Home Assistant.
3. **Validacions**: `validate_hacs.yml` (HACS Validation Tests) i `validate_hassfest.yml` (HA Validation Tests) asseguren el compliment dels estàndards.

Executa els tests abans de fer un PR:

```bash
# Tests bàsics
pytest tests/ -v

# Tests amb cobertura
pytest tests/ -v --cov=custom_components.meteocat_community_edition --cov-report=term-missing

# Verificar que la cobertura sigui >95%
pytest tests/ --cov=custom_components.meteocat_community_edition --cov-report=html
```

**Estat actual**: 102 tests, >95% cobertura ✅

## Codi de conducta

Sigues respectuós i constructiu. Volem una comunitat acollidora per a tothom.

## Llicència

En contribuir, acceptes que les teves contribucions es llicenciïn sota GPL-3.0.
