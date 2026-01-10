# Contributing to Janus-1

Thank you for your interest in contributing to Janus-1! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Areas for Contribution](#areas-for-contribution)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Our Standards

**Positive behaviors include:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors include:**
- Harassment, trolling, or insulting/derogatory comments
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of computer architecture and machine learning

### Setting Up Your Development Environment

1. **Fork the repository**
   ```bash
   # Click the "Fork" button on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Janus-1.git
   cd Janus-1
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/ChessEngineUS/Janus-1.git
   ```

4. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

6. **Verify installation**
   ```bash
   pytest tests/ -v
   ```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a new branch
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clean, well-documented code
- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run tests
pytest tests/ -v

# Check code coverage
pytest tests/ --cov=src --cov-report=term

# Run linting
flake8 src tests --max-line-length=88 --extend-ignore=E203,W503

# Check formatting
black --check src tests

# Type checking (optional but recommended)
mypy src --ignore-missing-imports
```

### 4. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add: Brief description of changes"
```

**Commit Message Guidelines:**
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Fix bug" not "Fixes bug")
- Start with a verb: Add, Fix, Update, Remove, Refactor
- Keep first line under 72 characters
- Add detailed description if needed

Examples:
```
Add: Implement HBM memory technology model
Fix: Correct P99 latency calculation in simulator
Update: Enhance prefetcher FSM documentation
Refactor: Simplify bank conflict logic
```

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Then:
1. Go to GitHub and create a Pull Request
2. Fill out the PR template
3. Link related issues if applicable
4. Wait for review and address feedback

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 88 characters (Black default)
- **Formatting**: Use [Black](https://github.com/psf/black) for automatic formatting
- **Import order**: Use [isort](https://pycqa.github.io/isort/) for organizing imports
- **Type hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

### Example Code Style

```python
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """Configuration for memory hierarchy simulation.
    
    Attributes:
        cache_size_mb: Size of cache in megabytes.
        latency_cycles: Access latency in clock cycles.
        num_banks: Number of memory banks.
    """
    cache_size_mb: int = 32
    latency_cycles: int = 1
    num_banks: int = 4


def calculate_hit_rate(
    hits: int, 
    misses: int, 
    precision: Optional[int] = None
) -> float:
    """Calculate cache hit rate percentage.
    
    Args:
        hits: Number of cache hits.
        misses: Number of cache misses.
        precision: Optional decimal places for rounding.
    
    Returns:
        Hit rate as percentage (0-100).
    
    Raises:
        ValueError: If hits or misses are negative.
    
    Example:
        >>> calculate_hit_rate(99, 1)
        99.0
    """
    if hits < 0 or misses < 0:
        raise ValueError("Hits and misses must be non-negative")
    
    total = hits + misses
    if total == 0:
        return 0.0
    
    rate = (hits / total) * 100
    return round(rate, precision) if precision else rate
```

### Docstring Format (Google Style)

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """Brief one-line description.
    
    More detailed description if needed. Explain what the function does,
    any important algorithms or assumptions, and key behaviors.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
    
    Returns:
        Description of return value.
    
    Raises:
        ExceptionType: When and why this exception is raised.
    
    Example:
        >>> function_name(value1, value2)
        expected_output
    """
```

---

## Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Name test files as `test_<module_name>.py`
- Name test functions as `test_<functionality>`
- Use pytest fixtures for common setup
- Aim for >80% code coverage

### Test Structure

```python
import pytest
from src.simulator.janus_sim import JanusSim


@pytest.fixture
def basic_sim():
    """Fixture providing a basic simulator instance."""
    return JanusSim()


def test_simulator_initialization(basic_sim):
    """Test that simulator initializes with correct defaults."""
    assert basic_sim.config.t1_sram_size_mb == 32
    assert basic_sim.config.t1_latency_cycles == 1
    assert basic_sim.cycle == 0


def test_cache_hit_simple(basic_sim):
    """Test basic cache hit scenario."""
    trace = [("READ", 0x1000)]
    basic_sim.run(trace)
    metrics = basic_sim.get_metrics()
    
    # First access is always a miss
    assert metrics.t1_misses == 1
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_simulator.py -v

# Run specific test function
pytest tests/test_simulator.py::test_cache_hit_simple -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run with detailed output
pytest tests/ -vv -s
```

---

## Documentation

### Code Documentation

- **All public functions/classes** must have docstrings
- **Complex algorithms** should have inline comments
- **Type hints** should be used for all function signatures
- **Examples** should be included in docstrings where helpful

### Updating Documentation

When making changes, update:
- Function/class docstrings
- README.md (if adding new features)
- API reference in `docs/api_reference.md`
- Architecture docs if changing design

---

## Submitting Changes

### Pull Request Process

1. **Ensure all tests pass** and coverage is maintained
2. **Update documentation** for any new features
3. **Add entries to CHANGELOG.md** under "Unreleased"
4. **Create descriptive PR title** following commit message guidelines
5. **Fill out PR template** completely
6. **Request review** from maintainers

### Pull Request Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Coverage maintained or improved

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. Maintainers will review your PR within 1-2 weeks
2. Address any requested changes
3. Once approved, maintainers will merge your PR
4. Your contribution will be included in the next release

---

## Areas for Contribution

### High Priority

1. **FPGA/Hardware Implementation**
   - Verilog/SystemVerilog RTL for prefetcher
   - FPGA emulation of memory hierarchy
   - Synthesis results and timing analysis

2. **Extended Workloads**
   - Encoder-decoder model traces
   - Vision transformer memory patterns
   - Real hardware profiling data

3. **Alternative Memory Technologies**
   - HBM (High Bandwidth Memory) modeling
   - ReRAM/PCRAM analysis
   - 3D-stacked memory architectures

### Medium Priority

4. **Optimization Algorithms**
   - Adaptive prefetching strategies
   - Dynamic power management
   - Thermal-aware scheduling

5. **Validation and Benchmarking**
   - Additional LLM models (Mistral, Phi-2, Gemma)
   - Comparison with commercial accelerators
   - Real-world deployment scenarios

6. **Visualization and Analysis**
   - Interactive dashboards
   - Real-time simulation visualization
   - Performance profiling tools

### Documentation

7. **Tutorials and Examples**
   - Getting started guides
   - Advanced usage examples
   - Integration with ML frameworks

8. **Academic Papers**
   - Extended literature review
   - Comparative analysis
   - Case studies

---

## Questions?

If you have questions:

- **GitHub Issues**: [Create an issue](https://github.com/ChessEngineUS/Janus-1/issues)
- **Discussions**: [Join the discussion](https://github.com/ChessEngineUS/Janus-1/discussions)
- **Email**: Contact maintainers via GitHub

---

## License

By contributing to Janus-1, you agree that your contributions will be licensed under the MIT License.

---

## Recognition

All contributors will be recognized in:
- Repository README.md
- Release notes
- Academic paper acknowledgments (for significant contributions)

---

Thank you for contributing to Janus-1! Your efforts help advance edge AI research. 🚀
