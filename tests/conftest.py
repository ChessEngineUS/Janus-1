#!/usr/bin/env python3
"""
Pytest Configuration and Fixtures
==================================

Shared test fixtures and configuration for Janus-1 test suite.

Author: Janus-1 Design Team
License: MIT
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def default_config():
    """Provide default simulation configuration."""
    from src.simulator.janus_sim import SimulationConfig
    return SimulationConfig()


@pytest.fixture
def default_simulator(default_config):
    """Provide fresh simulator instance with default config."""
    from src.simulator.janus_sim import JanusSim
    return JanusSim(default_config)


@pytest.fixture
def small_sequential_trace():
    """Provide small sequential trace for quick tests."""
    from src.benchmarks.trace_generator import generate_sequential_trace
    return generate_sequential_trace(start_addr=0x10000, num_accesses=50)


@pytest.fixture
def small_llm_trace():
    """Provide small LLM trace for quick tests."""
    from src.benchmarks.trace_generator import generate_llm_trace
    return generate_llm_trace(context_length=128, hidden_dim=1024)


@pytest.fixture
def large_llm_trace():
    """Provide large LLM trace for performance tests."""
    from src.benchmarks.trace_generator import generate_llm_trace
    return generate_llm_trace(context_length=2048, hidden_dim=4096)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", 'slow: marks tests as slow (deselect with -m "not slow")'
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance benchmarks"
    )
    config.addinivalue_line(
        "markers", "stress: marks tests as stress tests"
    )
