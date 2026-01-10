"""Tests for memory hierarchy simulator."""

import pytest
import collections
from typing import List, Tuple


def test_import_simulator():
    """Test that simulator module can be imported."""
    from src.simulator.janus_sim import (
        JanusSim,
        SimulationConfig,
        SimulationMetrics,
    )

    assert JanusSim is not None
    assert SimulationConfig is not None
    assert SimulationMetrics is not None


def test_simulation_config_defaults():
    """Test SimulationConfig default values."""
    from src.simulator.janus_sim import SimulationConfig

    config = SimulationConfig()
    assert config.t1_sram_size_mb == 32
    assert config.t1_sram_banks == 4
    assert config.t2_edram_banks == 14
    assert config.cache_line_size_bytes == 128
    assert config.prefetch_look_ahead == 16


def test_janus_sim_initialization():
    """Test JanusSim initialization."""
    from src.simulator.janus_sim import JanusSim

    sim = JanusSim()
    assert sim is not None
    assert sim.cycle == 0
    assert sim.t1_hits == 0
    assert sim.t1_misses == 0


def test_simple_simulation_run():
    """Test running a simple simulation."""
    from src.simulator.janus_sim import JanusSim

    # Create simple linear trace
    trace = [("READ", i * 128) for i in range(100)]

    sim = JanusSim()
    sim.run(trace)
    metrics = sim.get_metrics()

    # Basic sanity checks
    # Note: The simulator may issue prefetches which count as misses,
    # so we check that we have all 100 read operations completed
    assert len(metrics.read_latencies) == 100
    assert metrics.total_cycles > 0
    assert metrics.hit_rate >= 0.0
    assert metrics.hit_rate <= 100.0
    # At least most reads should complete
    assert metrics.t1_hits >= 95


def test_cache_hit_rate():
    """Test that repeated accesses get cached."""
    from src.simulator.janus_sim import JanusSim

    # Access same addresses twice
    trace = [("READ", 0), ("READ", 128), ("READ", 0), ("READ", 128)]

    sim = JanusSim()
    sim.run(trace)
    metrics = sim.get_metrics()

    # Should have some hits from repeated accesses
    assert metrics.t1_hits >= 2


def test_metrics_properties():
    """Test SimulationMetrics property calculations."""
    from src.simulator.janus_sim import SimulationMetrics

    metrics = SimulationMetrics(
        t1_hits=99,
        t1_misses=1,
        total_cycles=1000,
        read_latencies=[1, 1, 1, 2, 3],
        prefetch_bandwidth=50,
        compute_bandwidth=100,
    )

    assert metrics.hit_rate == 99.0
    assert metrics.p50_latency == 1.0
    assert metrics.p99_latency > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
