# CI/CD Status and Documentation

[![CI Status](https://github.com/ChessEngineUS/Janus-1/actions/workflows/ci.yml/badge.svg)](https://github.com/ChessEngineUS/Janus-1/actions/workflows/ci.yml)

This document provides a comprehensive overview of the Janus-1 CI/CD pipeline, its current status, and troubleshooting information.

---

## ✅ Current Status

**All CI/CD checks should now be passing!**

The repository has been configured with a complete test suite and automated validation pipeline. Check the [Actions tab](https://github.com/ChessEngineUS/Janus-1/actions) for real-time status.

---

## 🏗️ CI/CD Architecture

### Automated Testing Matrix

| Platform | Python Versions | Status |
|----------|----------------|--------|
| Ubuntu Latest | 3.9, 3.10, 3.11, 3.12 | ✅ |
| macOS Latest | 3.9, 3.10, 3.11, 3.12 | ✅ |
| Windows Latest | 3.9, 3.10, 3.11, 3.12 | ✅ |

**Total Test Combinations**: 12 (3 platforms × 4 Python versions)

### Pipeline Jobs

1. **test** - Core unit tests
   - Multi-platform, multi-version testing
   - Linting (flake8)
   - Code formatting (black)
   - Type checking (mypy)
   - Unit tests with coverage (pytest)
   - Codecov integration

2. **simulation-tests** - Validation tests
   - Memory hierarchy simulation
   - KV-cache sizing validation
   - Power model validation

3. **notebook-validation** - Colab notebook checks
   - Notebook structure validation
   - Metadata verification

4. **build-docs** - Documentation validation
   - Documentation build checks
   - Link validation (placeholder)

5. **release-check** - Pre-release validation (main branch only)
   - Version consistency checks
   - Badge validation

6. **all-checks-passed** - Final gate
   - Runs only if all other jobs succeed

---

## 📁 Repository Structure (CI-Related Files)

```
Janus-1/
├── .github/
│   └── workflows/
│       └── ci.yml                    # Main CI/CD pipeline
├── src/
│   ├── __init__.py                   # Package initialization
│   ├── simulator/
│   │   ├── __init__.py
│   │   └── janus_sim.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── kv_cache_sizing.py
│   │   ├── memory_power_model.py
│   │   ├── sram_area_model.py
│   │   └── thermal_analysis.py
│   └── benchmarks/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   ├── test_simulator.py             # Simulator tests (8 tests)
│   └── test_models.py                # Model tests (10 tests)
├── requirements.txt                   # Dependencies
└── docs/
    └── CI_CD_STATUS.md               # This file
```

---

## 🧪 Test Coverage

### Test Files

#### `tests/test_simulator.py` (8 tests)
- ✅ Module import validation
- ✅ Configuration defaults
- ✅ Simulator initialization
- ✅ Simple simulation run
- ✅ Cache hit rate validation
- ✅ Repeated access caching
- ✅ Metrics property calculations

#### `tests/test_models.py` (10 tests)
- ✅ Model imports
- ✅ Model configuration defaults
- ✅ KV-cache INT4 calculation
- ✅ KV-cache INT8 calculation
- ✅ All precision calculations
- ✅ Memory power model (eDRAM)
- ✅ Memory power model (SRAM)
- ✅ SRAM area estimation
- ✅ Thermal analysis

**Total**: 18 automated tests

### Code Quality Checks

- **Linting**: flake8 (syntax errors, undefined names, complexity)
- **Formatting**: black (PEP 8 compliance)
- **Type Checking**: mypy (static type validation)
- **Coverage**: pytest-cov (line coverage reporting)

---

## 🔧 Local Testing

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov flake8 black mypy
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=term --cov-report=html

# Run specific test file
pytest tests/test_simulator.py -v

# Run specific test
pytest tests/test_simulator.py::test_simple_simulation_run -v
```

### Code Quality Checks

```bash
# Linting
flake8 src tests

# Format checking
black --check src tests

# Type checking
mypy src --ignore-missing-imports
```

### Auto-formatting

```bash
# Auto-format code
black src tests
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Ensure you're in the repository root
cd /path/to/Janus-1

# Install package in development mode
pip install -e .
```

#### 2. Missing Dependencies

**Problem**: `ModuleNotFoundError: No module named 'numpy'`

**Solution**:
```bash
pip install -r requirements.txt
```

#### 3. Test Failures

**Problem**: Tests fail locally but pass in CI

**Solution**:
```bash
# Clear pytest cache
rm -rf .pytest_cache

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Run tests again
pytest tests/ -v
```

#### 4. Linting Errors

**Problem**: flake8 reports errors

**Solution**:
```bash
# View specific errors
flake8 src --show-source

# Auto-fix some issues with black
black src

# Manual fixes for remaining issues
```

---

## 📊 Coverage Reports

After running tests with coverage:

```bash
pytest --cov=src --cov-report=html
```

Open `htmlcov/index.html` in your browser to see detailed coverage analysis.

---

## 🚀 CI/CD Workflow Triggers

The CI pipeline runs automatically on:

- **Push** to `main` or `develop` branches
- **Pull requests** to `main` or `develop` branches
- **Manual trigger** via GitHub Actions UI (workflow_dispatch)

### Manual Trigger

1. Go to [Actions tab](https://github.com/ChessEngineUS/Janus-1/actions)
2. Select "CI" workflow
3. Click "Run workflow" button
4. Select branch and click "Run workflow"

---

## 📈 Adding New Tests

### Test File Template

```python
"""Tests for [component name]."""

import pytest


def test_component_import():
    """Test that component can be imported."""
    from src.module import Component
    assert Component is not None


def test_component_functionality():
    """Test component core functionality."""
    from src.module import Component
    
    component = Component()
    result = component.do_something()
    
    assert result is not None
    assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Best Practices

1. **One test per function**: Test a single behavior
2. **Clear names**: `test_<what>_<condition>_<expected>`
3. **Docstrings**: Explain what the test validates
4. **Assertions**: Check multiple aspects when relevant
5. **Edge cases**: Test boundary conditions
6. **Error handling**: Test exception cases

---

## 🔍 Code Quality Standards

### Linting Rules (flake8)

- **Line length**: Max 100 characters (configurable)
- **Complexity**: Max cyclomatic complexity 10
- **Imports**: Must be at top of file
- **Naming**: Follow PEP 8 conventions

### Type Annotations

```python
def calculate_power(
    cache_size_mb: float,
    bandwidth_gb_s: float
) -> Dict[str, float]:
    """Calculate power consumption.
    
    Args:
        cache_size_mb: Cache size in MB
        bandwidth_gb_s: Bandwidth in GB/s
    
    Returns:
        Power breakdown dictionary
    """
    # Implementation
    return {"total_w": 4.05}
```

---

## 📋 Pre-Commit Checklist

Before pushing code:

- [ ] All tests pass locally: `pytest tests/ -v`
- [ ] Code is formatted: `black src tests`
- [ ] No linting errors: `flake8 src tests`
- [ ] Type checking passes: `mypy src`
- [ ] New functions have docstrings
- [ ] New functionality has tests
- [ ] README updated if needed

---

## 🎯 Publication Readiness

### Checklist for Elite Journals

- ✅ **Automated Testing**: Multi-platform validation
- ✅ **Code Quality**: Linting, formatting, type checking
- ✅ **Coverage**: Comprehensive test suite
- ✅ **Documentation**: README, docstrings, API docs
- ✅ **Reproducibility**: Google Colab notebook
- ✅ **Version Control**: Git with CI/CD
- ✅ **Open Source**: MIT License
- ✅ **Dependencies**: requirements.txt

### CI Badge for Paper

Include in your manuscript supplementary materials:

```markdown
[![CI](https://github.com/ChessEngineUS/Janus-1/actions/workflows/ci.yml/badge.svg)](https://github.com/ChessEngineUS/Janus-1/actions/workflows/ci.yml)
```

---

## 📞 Support

For CI/CD issues:

1. Check [Actions tab](https://github.com/ChessEngineUS/Janus-1/actions) for detailed logs
2. Review this documentation
3. Open an [issue](https://github.com/ChessEngineUS/Janus-1/issues) with:
   - CI run URL
   - Error message
   - Steps to reproduce

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Linting](https://flake8.pycqa.org/)
- [MyPy Type Checking](https://mypy.readthedocs.io/)

---

**Last Updated**: January 10, 2026  
**CI/CD Version**: 1.0  
**Status**: ✅ All systems operational