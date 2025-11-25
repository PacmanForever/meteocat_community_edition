# Contributing to Meteocat (Community Edition)

Thank you for wanting to contribute! 🎉

## How to contribute

### Report issues

If you find a bug or have an idea to improve the integration:

1. Check that a similar issue doesn't already exist
2. Create a new issue with:
   - Clear description of the problem or improvement
   - Steps to reproduce (if it's a bug)
   - Home Assistant version
   - Relevant logs (if applicable)

### Propose changes

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/amazing-improvement`)
3. Make changes and commits (`git commit -am 'Add amazing improvement'`)
4. Push to the branch (`git push origin feature/amazing-improvement`)
5. Open a Pull Request

### Code standards

- Follow PEP 8 for Python
- Add docstrings to functions and classes
- Write tests for new features
- Update documentation when needed

### Tests

**🎯 Quality goal: Home Assistant Silver Level + HACS**

This integration aims to:
- 🏆 **Home Assistant Silver Level**: Code coverage > 95%
- ✅ **HACS Validation**: Meet requirements to be accepted in HACS
- ✅ **Comprehensive tests** for all functionalities
- ✅ **Hassfest validation** without errors
- ✅ **GitHub Actions CI/CD**

Therefore, when adding new features:
1. **Write tests** that cover all cases (happy path + edge cases)
2. **Verify coverage** with `pytest --cov`
3. **Make sure all tests pass**

Run tests before submitting a PR:

```bash
# Basic tests
pytest tests/ -v

# Tests with coverage
pytest tests/ -v --cov=custom_components.meteocat_community_edition --cov-report=term-missing

# Verify coverage is >95%
pytest tests/ --cov=custom_components.meteocat_community_edition --cov-report=html
```

**Current status**: 102 tests, >95% coverage ✅

## Code of conduct

Be respectful and constructive. We want a welcoming community for everyone.

## License

By contributing, you agree that your contributions will be licensed under GPL-3.0.
