# Testing Guide

## Overview

Janus-1 features a comprehensive test suite validating all aspects of the chip design:

- **Memory Hierarchy**: Cache behavior, LRU eviction, bank conflicts
- **Prefetcher**: Stream detection, lookahead optimization, bandwidth limiting
- **Trace Generation**: Realistic LLM workloads, synthetic patterns
- **Integration**: End-to-end system validation
- **Benchmarks**: Performance regression testing
- **Models**: Power/area/performance analytical models

## Quick Start

### Run All Tests

```bash
# Unix/Linux/Mac
bash scripts/run_validation.sh

# Windows
scripts\run_validation.bat
```

### Run Specific Test Suites

```bash
# Memory hierarchy tests
pytest tests/test_memory_hierarchy.py -v

# Integration tests
pytest tests/test_integration.py -v

# All tests with coverage
pytest tests/ --cov=src --cov-report=html
```

### Run Tests by Category

```bash
# Fast tests only (skip slow integration tests)
pytest tests/ -v -m "not slow"

# Integration tests only
pytest tests/ -v -m integration

# Performance benchmarks
pytest tests/ -v -m performance
```

## Test Organization

### test_memory_hierarchy.py

**Validates memory hierarchy correctness:**

- `TestMemoryHierarchyCorrectness`: Basic cache operations
  - T1 hit/miss behavior
  - LRU eviction policy
  - Bank conflict detection
  - Write-allocate policy

- `TestPrefetcherBehavior`: Prefetcher functionality
  - Sequential stream detection
  - Random access (no prefetching)
  - Lookahead depth optimization
  - Issue width bandwidth limiting

- `TestLatencyCharacteristics`: Timing validation
  - T1 hit latency (1 cycle)
  - T2 miss latency (3+ cycles)
  - Percentile calculations (P50/P90/P99)

- `TestStressScenarios`: Edge cases and stress testing
  - Large traces (100K ops)
  - Capacity misses
  - Bank conflicts
  - Empty/minimal traces

- `TestConfigurationVariations`: Parameter sweeps
  - Varying T1 sizes (8-64 MB)
  - Bank count scaling
  - Different cache line sizes

- `TestMetricsAccuracy`: Reporting validation
  - Hit rate calculations
  - Bandwidth accounting
  - Cycle counting

**Coverage: 100+ test cases**

### test_trace_generator.py

**Validates trace generation:**

- `TestLLMTraceGeneration`: LLM workload realism
  - Parameter scaling
  - Spatial locality
  - Read/write ratios

- `TestSequentialTraceGeneration`: Sequential patterns
  - Basic sequential access
  - Custom strides
  - Operation types

- `TestRandomTraceGeneration`: Random patterns
  - Address range constraints
  - Low locality verification
  - Reproducibility with seeds

- `TestStridedTraceGeneration`: Strided access
  - Stride patterns
  - Address wraparound

- `TestTraceCharacteristics`: Quality metrics
  - Address alignment
  - No duplicate consecutive reads
  - Length scaling
  - Operation validity

**Coverage: 50+ test cases**

### test_integration.py

**End-to-end system validation:**

- `TestEndToEndSimulation`: Complete workflows
  - LLM inference pipeline
  - Sequential workload (>95% hit rate)
  - Random workload (<50% hit rate)
  - Mixed workloads

- `TestPerformanceCharacteristics`: Design targets
  - 99.9%+ hit rate for LLM
  - P99 latency ≤ 1-2 cycles
  - Prefetcher effectiveness (>40% improvement)

- `TestScalability`: System scaling
  - Large traces (50K ops)
  - Cache capacity scaling
  - Multi-bank scaling

- `TestRobustness`: Error handling
  - Large address values
  - Deterministic results
  - Write-only traces

- `TestConfigurationValidation`: Config validation
  - Default configuration validity
  - Custom configurations

**Coverage: 30+ test cases**

### test_benchmarks.py

**Benchmark infrastructure validation:**

- `TestBenchmarkAccuracy`: Measurement precision
  - Cycle count accuracy
  - Latency precision
  - Hit rate calculations

- `TestBenchmarkReproducibility`: Determinism
  - Identical results across runs
  - Trace generator reproducibility

- `TestPerformanceRegression`: Baseline validation
  - LLM workload targets
  - Sequential workload performance
  - Simulation runtime performance

- `TestBenchmarkCoverage`: Scenario coverage
  - High/low locality workloads
  - Realistic LLM traces

- `TestBenchmarkUtilities`: Reporting
  - Metrics accessibility
  - Report generation

**Coverage: 25+ test cases**

### test_models.py

**Analytical model validation** (placeholder for future implementation):

- Memory power models (SRAM, eDRAM)
- Area estimation models
- Performance models (throughput, bandwidth)

## Test Fixtures

### conftest.py

Shared fixtures for all tests:

- `default_config`: Standard simulation configuration
- `default_simulator`: Fresh simulator instance
- `small_sequential_trace`: Quick test trace (50 ops)
- `small_llm_trace`: Quick LLM trace (128 tokens)
- `large_llm_trace`: Full LLM trace (2048 tokens)

### Custom Markers

- `@pytest.mark.slow`: Long-running tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.performance`: Performance benchmarks
- `@pytest.mark.stress`: Stress tests

## Coverage Targets

### Current Coverage

- **simulator/janus_sim.py**: 95%+ coverage
- **benchmarks/trace_generator.py**: 90%+ coverage
- **Overall**: 85%+ coverage

### View Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html  # Windows
```

## Performance Benchmarks

### Regression Tests

Automated regression testing ensures performance doesn't degrade:

- **LLM workload**: ≥99.5% hit rate
- **Sequential workload**: ≥98% hit rate
- **Simulation speed**: <5s for 10K ops

### Benchmark Execution

```bash
# Run performance-marked tests
pytest tests/ -v -m performance

# With detailed timing
pytest tests/ -v -m performance --durations=10
```

## Continuous Integration

GitHub Actions automatically runs full test suite on:

- Every push to main/develop
- Every pull request
- Weekly schedule (Mondays)

**Matrix testing:**
- **OS**: Ubuntu, macOS, Windows
- **Python**: 3.9, 3.10, 3.11, 3.12
- **Total**: 12 configurations

## Writing New Tests

### Test Structure

```python
import pytest
from src.simulator.janus_sim import JanusSim

class TestMyFeature:
    """Test description."""
    
    def test_basic_behavior(self):
        """Test basic functionality."""
        sim = JanusSim()
        trace = [("READ", 0x1000)]
        sim.run(trace)
        metrics = sim.get_metrics()
        
        assert metrics.t1_misses == 1
    
    @pytest.mark.slow
    def test_stress_scenario(self):
        """Test under stress."""
        # Large workload test
        pass
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Descriptive test names** (`test_t1_hit_after_initial_miss`)
3. **Clear docstrings** explaining what's tested
4. **Use fixtures** for common setup
5. **Mark slow tests** with `@pytest.mark.slow`
6. **Test both success and failure** paths
7. **Include edge cases** (empty, single element, maximum size)

### Assertion Guidelines

```python
# Good: Specific assertion with message
assert metrics.hit_rate > 99.0, f"Hit rate {metrics.hit_rate:.2f}% below target"

# Good: Multiple related assertions
assert metrics.t1_hits == 99
assert metrics.t1_misses == 1
assert metrics.hit_rate == 99.0

# Avoid: Multiple unrelated assertions
# (split into separate tests instead)
```

## Debugging Failed Tests

### Verbose Output

```bash
# Show stdout/stderr
pytest tests/test_memory_hierarchy.py -v -s

# Show local variables on failure
pytest tests/test_memory_hierarchy.py -v -l

# Drop into debugger on failure
pytest tests/test_memory_hierarchy.py --pdb
```

### Common Issues

**Import errors:**
```bash
# Ensure src is in PYTHONPATH
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
```

**Fixture not found:**
```bash
# Check conftest.py is present
ls tests/conftest.py
```

**Assertion failures:**
- Check if design targets have changed
- Verify trace generator produces expected patterns
- Review simulator logic for bugs

## Test Maintenance

### When to Update Tests

1. **Design changes**: Update performance targets
2. **New features**: Add feature-specific tests
3. **Bug fixes**: Add regression test
4. **API changes**: Update affected tests

### Test Review Checklist

- [ ] Tests pass locally
- [ ] Coverage maintained/improved
- [ ] No flaky tests (run 10× to verify)
- [ ] Documentation updated
- [ ] CI passes on all platforms

## Validation Report Generation

For publication/submission, generate comprehensive validation report:

```bash
python scripts/generate_validation_report.py
```

Generates:
- `results/validation_report.pdf`: Publication-ready report
- `results/test_coverage.html`: Interactive coverage
- `results/performance_metrics.json`: Benchmark data

## Contact

For testing questions:
- Open issue: [GitHub Issues](https://github.com/ChessEngineUS/Janus-1/issues)
- Discussions: [GitHub Discussions](https://github.com/ChessEngineUS/Janus-1/discussions)

---

**Last Updated**: January 2026  
**Test Suite Version**: 1.0  
**Coverage Target**: 85%+