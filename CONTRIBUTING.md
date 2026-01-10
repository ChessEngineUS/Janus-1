# Contributing to Janus-1

Thank you for your interest in contributing to Janus-1! This document provides guidelines and best practices for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Areas for Contribution](#areas-for-contribution)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background or experience level.

### Expected Behavior

- Be respectful and professional
- Provide constructive feedback
- Focus on technical merit
- Welcome newcomers and help them learn

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or inflammatory comments
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of processor architecture and memory systems

### Setting Up Your Development Environment

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/Janus-1.git
cd Janus-1

# Add upstream remote
git remote add upstream https://github.com/ChessEngineUS/Janus-1.git

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies including dev tools
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Install pre-commit hooks (recommended)
pip install pre-commit
pre-commit install

# Verify installation
pytest tests/ -v
```

## Development Workflow

### Creating a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications
- `perf/` - Performance improvements

### Making Changes

1. **Write clear, focused commits**:
   ```bash
   git commit -m "Add INT4 quantization validation for Mistral model"
   ```

2. **Keep commits atomic** - One logical change per commit

3. **Write descriptive commit messages**:
   ```
   Add support for multi-head attention profiling
   
   - Implement attention trace generator
   - Add cycle-accurate timing model
   - Include validation against PyTorch reference
   - Update documentation with usage examples
   
   Closes #42
   ```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Imports**: Use absolute imports, group by stdlib/third-party/local
- **Type hints**: Required for all function signatures
- **Docstrings**: Google-style docstrings for all public APIs

### Code Formatting

```bash
# Format code with Black
black src tests

# Check formatting
black --check src tests

# Sort imports
isort src tests
```

### Linting

```bash
# Run flake8
flake8 src tests --max-line-length=88 --extend-ignore=E203,W503

# Run mypy for type checking
mypy src --ignore-missing-imports
```

### Example Code Style

```python
"""Module docstring explaining purpose."""

import collections
import sys
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.models.base import BaseModel


class MemoryHierarchy:
    """Simulate a two-tier memory hierarchy.
    
    This class implements a cycle-accurate model of SRAM + eDRAM
    memory system with bank conflicts and queuing delays.
    
    Args:
        t1_size_mb: Tier-1 SRAM size in megabytes
        t2_size_mb: Tier-2 eDRAM size in megabytes
        cache_line_size: Cache line size in bytes
        
    Attributes:
        cycle: Current simulation cycle
        hit_rate: Tier-1 cache hit rate
        
    Example:
        >>> mem = MemoryHierarchy(t1_size_mb=32, t2_size_mb=224)
        >>> mem.access(0x1000, op="READ")
        >>> print(f"Hit rate: {mem.hit_rate:.2f}%")
    """
    
    def __init__(
        self,
        t1_size_mb: int = 32,
        t2_size_mb: int = 224,
        cache_line_size: int = 128,
    ) -> None:
        """Initialize memory hierarchy."""
        self.t1_size_mb = t1_size_mb
        self.t2_size_mb = t2_size_mb
        self.cache_line_size = cache_line_size
        self._init_state()
    
    def access(
        self, 
        addr: int, 
        op: str = "READ"
    ) -> Tuple[bool, int]:
        """Access memory at specified address.
        
        Args:
            addr: Memory address to access
            op: Operation type ("READ" or "WRITE")
            
        Returns:
            Tuple of (hit, latency_cycles)
            
        Raises:
            ValueError: If operation type is invalid
        """
        if op not in ["READ", "WRITE"]:
            raise ValueError(f"Invalid operation: {op}")
        
        # Implementation...
        return True, 1
```

## Testing Guidelines

### Writing Tests

```python
import pytest
from src.simulator.janus_sim import JanusSim


class TestJanusSim:
    """Test suite for Janus simulator."""
    
    def test_cache_hit_basic(self):
        """Test that repeated accesses result in cache hits."""
        sim = JanusSim()
        trace = [("READ", 0x1000)] * 100
        
        sim.run(trace)
        metrics = sim.get_metrics()
        
        assert metrics.hit_rate > 99.0
        assert metrics.t1_hits == 99
        assert metrics.t1_misses == 1
    
    def test_stream_prefetch(self):
        """Test that sequential access triggers prefetching."""
        sim = JanusSim()
        # Generate sequential access pattern
        trace = [("READ", 0x1000 + i * 128) for i in range(100)]
        
        sim.run(trace)
        metrics = sim.get_metrics()
        
        # Should achieve very high hit rate with prefetching
        assert metrics.hit_rate > 95.0
        assert metrics.prefetch_bandwidth > 0
    
    @pytest.mark.parametrize("lookahead", [4, 8, 16, 32])
    def test_prefetch_lookahead(self, lookahead):
        """Test different prefetch lookahead depths."""
        from src.simulator.janus_sim import SimulationConfig
        
        config = SimulationConfig(prefetch_look_ahead=lookahead)
        sim = JanusSim(config)
        
        trace = [("READ", 0x1000 + i * 128) for i in range(100)]
        sim.run(trace)
        
        metrics = sim.get_metrics()
        assert metrics.total_cycles > 0
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_simulator.py -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run only fast tests (exclude slow integration tests)
pytest tests/ -v -m "not slow"
```

### Test Coverage Requirements

- All new code must have tests
- Aim for >80% code coverage
- Critical paths must have 100% coverage
- Include edge cases and error conditions

## Documentation

### Docstring Format (Google Style)

```python
def calculate_power(
    cache_size_mb: float,
    bandwidth_gb_s: float,
    technology: str = "eDRAM"
) -> Dict[str, float]:
    """Calculate power consumption for memory technology.
    
    Estimates dynamic and static power based on cache size,
    bandwidth, and technology parameters.
    
    Args:
        cache_size_mb: Cache size in megabytes
        bandwidth_gb_s: Memory bandwidth in GB/s
        technology: Technology type ("SRAM", "eDRAM", "MRAM")
        
    Returns:
        Dictionary with keys:
            - 'dynamic_w': Dynamic power in watts
            - 'static_w': Static power in watts
            - 'total_w': Total power in watts
            
    Raises:
        ValueError: If technology is not supported
        
    Example:
        >>> power = calculate_power(224, 20, "eDRAM")
        >>> print(f"Total: {power['total_w']:.2f} W")
        Total: 1.15 W
        
    Note:
        Power models are based on 3nm process technology.
        Static power includes leakage and refresh overhead.
        
    References:
        [1] Smith et al., "eDRAM Power Modeling", ISSCC 2024
    """
    # Implementation...
```

### Updating Documentation

- Update relevant `.md` files in `docs/`
- Add examples to docstrings
- Update README.md if adding major features
- Include references to papers/standards where applicable

## Pull Request Process

### Before Submitting

1. **Update your branch**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run the full test suite**:
   ```bash
   pytest tests/ -v --cov=src
   black --check src tests
   flake8 src tests
   mypy src
   ```

3. **Update documentation** if needed

4. **Write a clear PR description**

### PR Template

```markdown
## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement

## Changes Made

- Added X feature to support Y
- Fixed Z bug in module A
- Refactored B for better performance

## Testing

- [ ] All existing tests pass
- [ ] New tests added for new features
- [ ] Manual testing performed

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests provide good coverage

## Related Issues

Closes #123
Related to #456
```

### Review Process

1. Automated CI checks must pass
2. At least one maintainer review required
3. All review comments must be addressed
4. Final approval from project lead

## Areas for Contribution

### High Priority

- **FPGA Implementation**: Verilog/SystemVerilog for prefetcher FSM
- **Extended Validation**: Additional LLM models (Mistral, Phi-2, Gemma)
- **Workload Traces**: Real hardware profiling data
- **Power Optimization**: Dynamic voltage/frequency scaling

### Medium Priority

- **Documentation**: More examples and tutorials
- **Visualization**: Interactive dashboards for results
- **Memory Technologies**: HBM, ReRAM modeling
- **Compiler Integration**: INT4 code generation

### Good First Issues

- Documentation improvements
- Test coverage expansion
- Code cleanup and refactoring
- Example notebooks
- Bug fixes with clear reproduction steps

Look for issues tagged with `good-first-issue` or `help-wanted`.

## Questions?

If you have questions:

- Check existing [documentation](docs/)
- Search [issues](https://github.com/ChessEngineUS/Janus-1/issues)
- Ask in [discussions](https://github.com/ChessEngineUS/Janus-1/discussions)
- Contact maintainers

## Recognition

All contributors will be:

- Listed in CONTRIBUTORS.md
- Acknowledged in release notes
- Credited in academic publications (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Janus-1! 🚀