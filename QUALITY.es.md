# Estándares de Calidad - Meteocat Community Edition

## 🎯 Objetivo: Home Assistant Silver Level + Validación HACS

Esta integración está diseñada para cumplir:
- 🏆 **Home Assistant Silver Level** (>95% cobertura de tests)
- ✅ **Requisitos HACS** (validación para ser aceptada)

### Requisitos Home Assistant Silver

| Criterio | Requerido | Estado Actual |
|----------|-----------|---------------|
| **Cobertura de código** | >95% | ✅ >95% (102 tests) |
| **Tests exhaustivos** | Sí | ✅ 13 archivos de test |
| **Validación Hassfest** | 0 errores | ✅ Pass |
| **GitHub Actions CI/CD** | Configurado | ✅ Workflows activos |
| **Documentación completa** | Sí | ✅ 3 idiomas |
| **Gestión de errores** | Robusta | ✅ Retry + reauth |

---

## 📊 Cobertura de Tests

### Estado actual

```
Total: 102 tests
Cobertura: >95%
Archivos de test: 13
Líneas de código de test: 2,443+
```

### Distribución de tests

| Componente | Tests | Cobertura |
|------------|-------|-----------|
| **sensor.py** | 18 | >95% |
| **weather.py** | 15 | >95% |
| **device_trigger.py** | 7 | 100% |
| **__init__.py** | 10 | >95% |
| **coordinator.py** | 7 | >95% |
| **button.py** | 7 | >95% |
| **api.py** | 7 | >95% |
| **update_times.py** | 9 | >95% |
| **retry_logic.py** | 8 | >95% |
| **reauth.py** | 5 | >95% |
| **events.py** | 5 | >95% |
| **device_grouping.py** | 3 | 100% |
| **config_flow.py** | 1 | Básico |

### Áreas cubiertas

- ✅ **Sensores**: Cuotas, predicciones, timestamps, update times
- ✅ **Entidad Weather**: Todas las propiedades y casos límite
- ✅ **Device triggers**: Automatizaciones por dispositivo
- ✅ **Setup/Unload**: Ciclo de vida completo
- ✅ **Coordinator**: Actualizaciones en ambos modos
- ✅ **Cliente API**: Todas las llamadas con manejo de errores
- ✅ **Botón**: Actualización manual
- ✅ **Eventos**: Eventos de actualización de datos
- ✅ **Lógica de reintentos**: Exponential backoff
- ✅ **Reauth**: Re-autenticación sin reiniciar
- ✅ **Agrupación de dispositivos**: Agrupación correcta de entidades
- ✅ **Categorías de entidades**: Sensores de diagnóstico correctos

---

## 🔧 Ejecutar Tests

### Tests básicos

```bash
pytest tests/ -v
```

### Tests con cobertura

```bash
# Cobertura en terminal
pytest tests/ -v --cov=custom_components.meteocat_community_edition --cov-report=term-missing

# Cobertura en HTML (detallado)
pytest tests/ --cov=custom_components.meteocat_community_edition --cov-report=html

# Verificar umbral >95%
pytest tests/ --cov=custom_components.meteocat_community_edition --cov-fail-under=95
```

### Tests específicos

```bash
# Por archivo
pytest tests/test_sensor.py -v
pytest tests/test_weather.py -v

# Test concreto
pytest tests/test_sensor.py::test_update_time_sensor_entity_category -v
```

---

## 📋 Checklist para Nuevas Funcionalidades

Antes de hacer un PR con nuevas funcionalidades:

### 1. Código
- [ ] Sigue PEP 8
- [ ] Tiene docstrings
- [ ] Gestiona errores correctamente
- [ ] No hay imports sin usar
- [ ] Utiliza type hints cuando sea posible

### 2. Tests
- [ ] Añadidos tests para **todos los casos de uso**
- [ ] Cubiertos **casos límite** (datos vacíos, errores, etc.)
- [ ] Cobertura total **>95%** mantenida
- [ ] Todos los tests pasan (`pytest tests/ -v`)
- [ ] Tests documentados en README.md de tests

### 3. Documentación
- [ ] README.md actualizado (catalán)
- [ ] README.en.md actualizado (inglés)
- [ ] README.es.md actualizado (español)
- [ ] CHANGELOG.md actualizado
- [ ] info.md actualizado si es necesario
- [ ] Ejemplos de uso añadidos si aplica

### 4. Integración
- [ ] Validación Hassfest pasa (`hassfest validate`)
- [ ] GitHub Actions pasa (CI/CD)
- [ ] No hay warnings de deprecación
- [ ] Compatible con versiones recientes de HA

---

## 🎨 Estándares de Código

### Python (PEP 8)
- Indentación: 4 espacios
- Línea máxima: 100 caracteres (preferiblemente 88 para compatibilidad Black)
- Imports ordenados: standard library → third-party → local

### Nomenclatura
- Clases: `PascalCase`
- Funciones/métodos: `snake_case`
- Constantes: `UPPER_SNAKE_CASE`
- Variables privadas: `_leading_underscore`

### Docstrings
```python
def function_name(param1: str, param2: int) -> bool:
    """Descripción breve.
    
    Descripción más larga si es necesaria.
    
    Args:
        param1: Descripción de param1
        param2: Descripción de param2
        
    Returns:
        Descripción del valor devuelto
        
    Raises:
        ValueError: Cuando param1 está vacío
    """
```

---

## 🔄 Flujo de Desarrollo

1. **Fork** del repositorio
2. **Branch** para la funcionalidad (`feature/nombre-funcionalidad`)
3. **Desarrollo** con tests
4. **Verificación local**:
   ```bash
   pytest tests/ -v --cov --cov-fail-under=95
   flake8 custom_components/meteocat_community_edition/
   ```
5. **Commit** con mensajes claros
6. **Push** y **Pull Request**
7. **CI/CD** pasa automáticamente
8. **Review** y merge

---

## 📈 Mejora Continua

### Objetivos futuros
- [ ] Mantener >95% cobertura siempre
- [ ] Añadir tests de integración con HA real
- [ ] Documentar todos los casos límite
- [ ] Mejorar tests de config_flow
- [ ] Añadir tests de rendimiento

### Métricas a monitorizar
- Cobertura de tests (target: >95%)
- Tiempo de ejecución de tests (target: <2 min)
- Complejidad ciclomática (target: <10 por función)
- Duplicación de código (target: <3%)

---

## 🤖 Integración con IA

### Para GitHub Copilot / Claude / ChatGPT

Este proyecto está configurado para:
- 🏆 **Mantener Home Assistant Silver Level** (>95% cobertura)
- ✅ **Cumplir validación HACS** (requisitos para ser aceptada)

Cuando sugieras cambios o nueva funcionalidad:

1. **Siempre incluye tests** con cobertura >95%
2. **Documenta** en los 3 idiomas (CA/EN/ES)
3. **Verifica** que cumple PEP 8
4. **Comprueba** que no rompes tests existentes
5. **Gestiona errores** adecuadamente
6. **Utiliza** las fixtures existentes en `conftest.py`
7. **Corrección de errores**: Todo bug fix debe incluir un test de regresión que reproduzca el error y verifique la solución.

### Contexto importante
- Modo Estación (XEMA): Datos en tiempo real + predicciones
- Modo Municipal: Solo predicciones (para complementar estaciones locales)
- Sensores de diagnóstico: `EntityCategory.DIAGNOSTIC`
- Agrupación de dispositivos: Todas las entidades bajo un único dispositivo
- Eventos: `meteocat_community_edition_data_updated`
- Actualizaciones: 2 veces al día (optimizado para cuotas)

---

**Última actualización**: 2025-11-25  
**Versión**: 1.0.0  
**Estado**: HA Silver Ready 🏆 | HACS Ready ✅
