# Contribuir a Meteocat (Community Edition)

¡Gracias por querer contribuir! 🎉

## Cómo contribuir

### Reportar problemas

Si encuentras un error o tienes una idea para mejorar la integración:

1. Comprueba que no exista ya un issue similar
2. Crea un nuevo issue con:
   - Descripción clara del problema o mejora
   - Pasos para reproducir (si es un error)
   - Versión de Home Assistant
   - Logs relevantes (si aplica)

### Proponer cambios

1. Fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/mejora-increible`)
3. Haz los cambios y commits (`git commit -am 'Añade mejora increíble'`)
4. Push a la rama (`git push origin feature/mejora-increible`)
5. Abre un Pull Request

### Estándares de código

- Sigue PEP 8 para Python
- Añade docstrings a funciones y clases
- Escribe tests para nuevas funcionalidades
- Actualiza la documentación si es necesario

### Tests

**🎯 Objetivo de calidad: Home Assistant Silver Level + HACS**

Esta integración tiene como objetivo:
- 🏆 **Home Assistant Silver Level**: Cobertura de código > 95%
- ✅ **Validación HACS**: Cumplir requisitos para ser aceptada en HACS
- ✅ **Tests exhaustivos** para todas las funcionalidades
- ✅ **Validación Hassfest** sin errores
- ✅ **GitHub Actions CI/CD**

Por ello, cuando añadas nuevas funcionalidades:
1. **Escribe tests** que cubran todos los casos (happy path + edge cases)
2. **Verifica la cobertura** con `pytest --cov`
3. **Asegúrate de que todos los tests pasan**

Ejecuta los tests antes de hacer un PR:

```bash
# Tests básicos
pytest tests/ -v

# Tests con cobertura
pytest tests/ -v --cov=custom_components.meteocat_community_edition --cov-report=term-missing

# Verificar que la cobertura sea >95%
pytest tests/ --cov=custom_components.meteocat_community_edition --cov-report=html
```

**Estado actual**: 102 tests, >95% cobertura ✅

## Código de conducta

Sé respetuoso y constructivo. Queremos una comunidad acogedora para todos.

## Licencia

Al contribuir, aceptas que tus contribuciones se licencien bajo GPL-3.0.
