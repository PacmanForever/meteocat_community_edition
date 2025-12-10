# Quality Standards - Meteocat Community Edition

## 🎯 Goal: Home Assistant Silver Level + HACS Validation

This integration is designed to achieve:
- 🏆 **Home Assistant Silver Level** (>95% test coverage)
- ✅ **HACS Requirements** (validation to be accepted)

### Home Assistant Silver Requirements

| Criterion | Required | Current Status |
|-----------|----------|----------------|
| **Code coverage** | >95% | ✅ >95% (102 tests) |
| **Comprehensive tests** | Yes | ✅ 13 test files |
| **Hassfest validation** | 0 errors | ✅ Pass |
| **GitHub Actions CI/CD** | Configured | ✅ Active workflows |
| **Complete documentation** | Yes | ✅ 3 languages |
| **Error handling** | Robust | ✅ Retry + reauth |

---

## 📊 Test Coverage

### Current status

```
Total: 102 tests
Coverage: >95%
Test files: 13
Test code lines: 2,443+
```

### Test distribution

| Component | Tests | Coverage |
|-----------|-------|----------|
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
| **config_flow.py** | 1 | Basic |

### Covered areas

- ✅ **Sensors**: Quotas, forecasts, timestamps, update times
- ✅ **Weather entity**: All properties and edge cases
- ✅ **Device triggers**: Device-specific automations
- ✅ **Setup/Unload**: Complete lifecycle
- ✅ **Coordinator**: Updates in both modes
- ✅ **API client**: All calls with error handling
- ✅ **Button**: Manual refresh
- ✅ **Events**: Data update events
- ✅ **Retry logic**: Exponential backoff
- ✅ **Reauth**: Re-authentication without restart
- ✅ **Device grouping**: Correct entity grouping
- ✅ **Entity categories**: Correct diagnostic sensors

---

## 🔧 Running Tests

### Basic tests

```bash
pytest tests/ -v
```

### Tests with coverage

```bash
# Terminal coverage
pytest tests/ -v --cov=custom_components.meteocat_community_edition --cov-report=term-missing

# HTML coverage (detailed)
pytest tests/ --cov=custom_components.meteocat_community_edition --cov-report=html

# Verify >95% threshold
pytest tests/ --cov=custom_components.meteocat_community_edition --cov-fail-under=95
```

### Specific tests

```bash
# Per file
pytest tests/test_sensor.py -v
pytest tests/test_weather.py -v

# Specific test
pytest tests/test_sensor.py::test_update_time_sensor_entity_category -v
```

---

## 📋 Checklist for New Features

Before submitting a PR with new features:

### 1. Code
- [ ] Follows PEP 8
- [ ] Has docstrings
- [ ] Handles errors correctly
- [ ] No unused imports
- [ ] Uses type hints when possible

### 2. Tests
- [ ] Added tests for **all use cases**
- [ ] Covered **edge cases** (empty data, errors, etc.)
- [ ] Total coverage **>95%** maintained
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Tests documented in tests README.md

### 3. Documentation
- [ ] README.md updated (Catalan)
- [ ] README.en.md updated (English)
- [ ] README.es.md updated (Spanish)
- [ ] CHANGELOG.md updated
- [ ] info.md updated if needed
- [ ] Usage examples added if applicable

### 4. Integration
- [ ] Hassfest validation passes (`hassfest validate`)
- [ ] GitHub Actions pass (CI/CD)
- [ ] No deprecation warnings
- [ ] Compatible with recent HA versions

---

## 🎨 Code Standards

### Python (PEP 8)
- Indentation: 4 spaces
- Max line length: 100 characters (preferably 88 for Black compatibility)
- Ordered imports: standard library → third-party → local

### Naming
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private variables: `_leading_underscore`

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

## 🔄 Development Workflow

1. **Fork** the repository
2. **Branch** for the feature (`feature/feature-name`)
3. **Development** with tests
4. **Local verification**:
   ```bash
   pytest tests/ -v --cov --cov-fail-under=95
   flake8 custom_components/meteocat_community_edition/
   ```
5. **Commit** with clear messages
6. **Push** and **Pull Request**
7. **CI/CD** passes automatically
8. **Review** and merge

---

## 📈 Continuous Improvement

### Future goals
- [ ] Always maintain >95% coverage
- [ ] Add integration tests with real HA
- [ ] Document all edge cases
- [ ] Improve config_flow tests
- [ ] Add performance tests

### Metrics to monitor
- Test coverage (target: >95%)
- Test execution time (target: <2 min)
- Cyclomatic complexity (target: <10 per function)
- Code duplication (target: <3%)

---

## 🤖 AI Integration

### For GitHub Copilot / Claude / ChatGPT

This project is configured to:
- 🏆 **Maintain Home Assistant Silver Level** (>95% coverage)
- ✅ **Meet HACS validation** (requirements to be accepted)

When suggesting changes or new features:

1. **Always include tests** with >95% coverage
2. **Document** in all 3 languages (CA/EN/ES)
3. **Verify** PEP 8 compliance
4. **Check** that existing tests don't break
5. **Handle errors** appropriately
6. **Use** existing fixtures in `conftest.py`
7. **Bug fixes**: Every bug fix must include a regression test that reproduces the issue and verifies the fix.

### Important context
- Station Mode (XEMA): Real-time data + forecasts
- Municipal Mode: Forecasts only (to complement local stations)
- Diagnostic sensors: `EntityCategory.DIAGNOSTIC`
- Device grouping: All entities under a single device
- Events: `meteocat_community_edition_data_updated`
- Updates: 2 times per day (optimized for quotas)

---

**Last update**: 2025-11-25  
**Version**: 1.0.0  
**Status**: HA Silver Ready 🏆 | HACS Ready ✅
