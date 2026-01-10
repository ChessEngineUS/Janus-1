# Contributing to Janus-1

Thank you for your interest in contributing to Janus-1! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Areas for Contribution](#areas-for-contribution)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect:

- **Respectful communication** in all interactions
- **Constructive feedback** that helps improve the project
- **Recognition** of diverse perspectives and experiences
- **Focus on what is best** for the community and research advancement

### Unacceptable Behavior

- Harassment, discrimination, or personal attacks
- Trolling, insulting comments, or unconstructive criticism
- Publishing others' private information without permission
- Any conduct that would be inappropriate in a professional setting

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git for version control
- Basic understanding of computer architecture and machine learning

### Setting Up Development Environment

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Janus-1.git
cd Janus-1

# Add upstream remote
git remote add upstream https://github.com/ChessEngineUS/Janus-1.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (including dev dependencies)
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install

# Verify installation
pytest tests/ -v
```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a new branch for your feature/fix
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Write clean, well-documented code
- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
pytest tests/ -v --cov=src

# Run specific test file
pytest tests/test_simulator.py -v

# Check code formatting
black --check src tests

# Check linting
flake8 src tests --max-line-length=88 --extend-ignore=E203,W503

# Type checking (optional)
mypy src --ignore-missing-imports
```

### 4. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "Add feature: brief description

Detailed explanation of what was changed and why.
References #issue-number if applicable."
```

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Go to GitHub and create a Pull Request
```

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: 88 characters (Black default)
- **Formatting**: Use [Black](https://black.readthedocs.io/) for automatic formatting
- **Imports**: Organize imports using:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
- **Type hints**: Use type hints for function signatures

### Example Code Style

```python
"""Module docstring describing purpose.

Detailed description if needed.

Author: Your Name
License: MIT
"""

import os
import sys
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from src.simulator.janus_sim import JanusSim


class MyClass:
    """Class docstring with brief description.
    
    Attributes:
        attr1: Description of attribute
        attr2: Description of attribute
    """
    
    def __init__(self, param1: int, param2: str = "default"):
        """Initialize MyClass.
        
        Args:
            param1: Description of param1
            param2: Description of param2 with default
        """
        self.attr1 = param1
        self.attr2 = param2
    
    def my_method(self, input_data: List[int]) -> Tuple[float, float]:
        """Brief description of method.
        
        Args:
            input_data: Description of input parameter
            
        Returns:
            Tuple containing (mean, std) of input data
            
        Raises:
            ValueError: If input_data is empty
        """
        if not input_data:
            raise ValueError("Input data cannot be empty")
        
        mean = np.mean(input_data)
        std = np.std(input_data)
        return mean, std
```

### Documentation Standards

- **Module docstrings**: At the top of each file
- **Class docstrings**: Describe purpose and attributes
- **Function docstrings**: Use Google-style format:
  - Brief description
  - Args: Parameter descriptions with types
  - Returns: Return value description
  - Raises: Exception descriptions if applicable
- **Inline comments**: Use sparingly, prefer self-documenting code

### Naming Conventions

- **Functions and variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private methods**: `_leading_underscore`
- **Descriptive names**: Prefer `cache_hit_rate` over `chr`

---

## Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_<module_name>.py`
- Name test functions `test_<functionality>`
- Use descriptive test names that explain what is being tested

### Test Structure

```python
import pytest
from src.simulator.janus_sim import JanusSim


def test_simulation_hit_rate():
    """Test that simulator achieves expected hit rate."""
    # Arrange
    sim = JanusSim()
    trace = [("READ", 0x1000 + i * 128) for i in range(100)]
    
    # Act
    sim.run(trace)
    metrics = sim.get_metrics()
    
    # Assert
    assert metrics.hit_rate > 95.0
    assert metrics.t1_hits + metrics.t1_misses == 100


def test_invalid_configuration():
    """Test that invalid config raises appropriate error."""
    with pytest.raises(ValueError):
        config = SimulationConfig(t1_sram_size_mb=-1)
```

### Test Coverage

- Aim for **>80% code coverage** for new code
- Test both **happy paths** and **error cases**
- Include **edge cases** and **boundary conditions**

---

## Documentation

### Updating Documentation

When making changes, update:

- **README.md**: For user-facing changes
- **API documentation**: For code changes
- **Architecture docs**: For design changes
- **CHANGELOG.md**: Add entry for your contribution

### Documentation Format

- Use **Markdown** for all documentation
- Include **code examples** where appropriate
- Add **diagrams** for complex concepts (use Mermaid or ASCII art)
- Keep language **clear and concise**

---

## Pull Request Process

### Before Submitting

- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] New code has tests with good coverage
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up-to-date with main

### PR Description Template

```markdown
## Description

Brief description of what this PR does.

## Related Issue

Fixes #issue-number

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

Describe the tests you ran and how to reproduce:

1. Test scenario 1
2. Test scenario 2

## Checklist

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published
```

### Review Process

1. **Automated checks** run via CI/CD
2. **Code review** by maintainers (typically within 1-3 days)
3. **Feedback incorporation** - address review comments
4. **Approval and merge** once all checks pass

---

## Areas for Contribution

We welcome contributions in the following areas:

### High Priority

1. **FPGA Emulation**
   - Verilog/SystemVerilog implementation of prefetcher
   - Hardware validation of memory hierarchy
   - Timing analysis and optimization

2. **Extended Workloads**
   - Encoder-decoder model traces
   - Vision transformer workloads
   - Real hardware profiling data

3. **Alternative Memory Technologies**
   - HBM power/area models
   - ReRAM integration studies
   - 3D-stacked memory analysis

4. **Optimization Algorithms**
   - Dynamic voltage/frequency scaling
   - Advanced prefetching policies
   - Cache replacement policies

### Medium Priority

5. **Documentation Improvements**
   - Tutorial notebooks
   - API reference expansion
   - Architecture deep-dives

6. **Testing and Validation**
   - Additional test cases
   - Benchmark suite expansion
   - Performance regression tests

7. **Tooling and Infrastructure**
   - Docker containerization
   - Cloud deployment scripts
   - Visualization tools

### Good First Issues

- Documentation typo fixes
- Adding code examples
- Improving error messages
- Adding type hints to existing code
- Writing additional unit tests

Check the [Issues](https://github.com/ChessEngineUS/Janus-1/issues) page for specific tasks labeled `good first issue`.

---

## Questions?

If you have questions about contributing:

- **Open an issue** for general questions
- **Start a discussion** in [GitHub Discussions](https://github.com/ChessEngineUS/Janus-1/discussions)
- **Check existing issues** - your question might already be answered

---

## License

By contributing to Janus-1, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Janus-1! Your efforts help advance edge AI research. 🚀
