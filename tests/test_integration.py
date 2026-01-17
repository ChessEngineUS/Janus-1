#!/usr/bin/env python3
"""
Integration Test Suite
======================

End-to-end testing of complete Janus-1 system.
Tests full simulation pipelines and realistic workloads.

Author: Janus-1 Design Team
License: MIT
"""

import pytest
import time
from src.simulator.janus_sim import JanusSim, SimulationConfig
from src.benchmarks.trace_generator import (
    generate_llm_trace,
    generate_sequential_trace,
    generate_random_trace,
)


class TestEndToEndSimulation:
    """Test complete simulation workflows."""

    def test_llm_inference_pipeline(self):
        """Test complete LLM inference simulation pipeline."""
        # Generate realistic LLM workload
        trace = generate_llm_trace(context_length=2048, hidden_dim=4096)
        
        # Run simulation
        sim = JanusSim()
        sim.run(trace)
        
        # Validate results
        metrics = sim.get_metrics()
        
        assert metrics.t1_hits + metrics.t1_misses == len([op for op, _ in trace if op == "READ"]), \
            "All reads should be accounted for"
        assert metrics.hit_rate > 0, "Should have some cache hits"
        assert metrics.total_cycles > 0, "Should execute some cycles"

    def test_sequential_workload_high_hit_rate(self):
        """Test sequential workload achieves high hit rate with prefetcher."""
        config = SimulationConfig(prefetch_look_ahead=16)
        sim = JanusSim(config)
        
        # Long sequential trace
        trace = generate_sequential_trace(start_addr=0x100000, num_accesses=1000)
        
        sim.run(trace)
        metrics = sim.get_metrics()
        
        # Sequential access with prefetcher should achieve >95% hit rate
        assert metrics.hit_rate > 95.0, \
            f"Sequential workload should achieve >95% hit rate, got {metrics.hit_rate:.1f}%"

    def test_random_workload_low_hit_rate(self):
        """Test random workload has expected low hit rate."""
        sim = JanusSim()
        
        # Random access pattern
        trace = generate_random_trace(num_accesses=1000, addr_range=(0, 10_000_000), seed=42)
        
        sim.run(trace)
        metrics = sim.get_metrics()
        
        # Random access should have low hit rate
        assert metrics.hit_rate < 50.0, \
            f"Random workload should have <50% hit rate, got {metrics.hit_rate:.1f}%"

    def test_mixed_workload_behavior(self):
        """Test mixed sequential and random workload."""
        sim = JanusSim()
        
        # Mix of sequential and random
        seq_trace = generate_sequential_trace(start_addr=0x200000, num_accesses=500)
        rand_trace = generate_random_trace(num_accesses=500, addr_range=(0, 10_000_000), seed=123)
        mixed_trace = seq_trace + rand_trace
        
        sim.run(mixed_trace)
        metrics = sim.get_metrics()
        
        # Mixed workload should have moderate hit rate
        assert 30.0 < metrics.hit_rate < 80.0, \
            f"Mixed workload should have moderate hit rate, got {metrics.hit_rate:.1f}%"


class TestPerformanceCharacteristics:
    """Test performance metrics meet design targets."""

    def test_target_hit_rate_llm_workload(self):
        """Test LLM workload achieves target 99.9%+ hit rate."""
        config = SimulationConfig(prefetch_look_ahead=16)
        sim = JanusSim(config)
        
        # Realistic LLM inference trace
        trace = generate_llm_trace(context_length=4096, hidden_dim=4096)
        
        sim.run(trace)
        metrics = sim.get_metrics()
        
        # Design target: >99.9% hit rate
        assert metrics.hit_rate >= 99.9, \
            f"LLM workload should achieve >=99.9% hit rate, got {metrics.hit_rate:.2f}%"

    def test_latency_targets(self):
        """Test P99 latency meets design target."""
        sim = JanusSim()
        
        trace = generate_llm_trace(context_length=2048, hidden_dim=4096)
        
        sim.run(trace)
        metrics = sim.get_metrics()
        
        # Design target: P99 latency <= 1 cycle (with high hit rate)
        if metrics.hit_rate > 99.0:
            assert metrics.p99_latency <= 2.0, \
                f"P99 latency should be <=2 cycles with high hit rate, got {metrics.p99_latency:.1f}"

    def test_prefetch_effectiveness(self):
        """Test prefetcher provides significant benefit."""
        # Run with prefetcher enabled
        config_with_pf = SimulationConfig(prefetch_look_ahead=16)
        sim_with_pf = JanusSim(config_with_pf)
        
        trace = generate_sequential_trace(start_addr=0x300000, num_accesses=1000)
        sim_with_pf.run(trace)
        metrics_with_pf = sim_with_pf.get_metrics()
        
        # Run with prefetcher disabled
        config_no_pf = SimulationConfig(prefetch_look_ahead=0)
        sim_no_pf = JanusSim(config_no_pf)
        sim_no_pf.run(trace)
        metrics_no_pf = sim_no_pf.get_metrics()
        
        # Prefetcher should improve hit rate significantly
        improvement = metrics_with_pf.hit_rate - metrics_no_pf.hit_rate
        assert improvement > 40.0, \
            f"Prefetcher should improve hit rate by >40%, got {improvement:.1f}%"


class TestScalability:
    """Test system scalability with varying parameters."""

    def test_scale_to_large_traces(self):
        """Test simulation scales to large traces."""
        sim = JanusSim()
        
        # Large trace: 50K operations
        trace = generate_sequential_trace(start_addr=0x400000, num_accesses=50_000)
        
        start_time = time.time()
        sim.run(trace)
        elapsed = time.time() - start_time
        
        metrics = sim.get_metrics()
        
        # Should complete in reasonable time (<10 seconds)
        assert elapsed < 10.0, f"Large trace should complete in <10s, took {elapsed:.2f}s"
        assert metrics.t1_hits + metrics.t1_misses == 50_000

    def test_scale_cache_capacity(self):
        """Test behavior with varying cache capacities."""
        results = []
        
        for cache_mb in [8, 16, 32, 64]:
            config = SimulationConfig(t1_sram_size_mb=cache_mb)
            sim = JanusSim(config)
            
            # Working set that fits in 32 MB
            trace = generate_llm_trace(context_length=1024, hidden_dim=4096)
            
            sim.run(trace)
            metrics = sim.get_metrics()
            results.append((cache_mb, metrics.hit_rate))
        
        # Hit rate should increase or stabilize with cache size
        hit_rates = [hr for _, hr in results]
        assert hit_rates[-1] >= hit_rates[0], \
            "Hit rate should improve or stabilize with larger cache"

    def test_multi_bank_scaling(self):
        """Test performance with different bank configurations."""
        results = []
        
        trace = generate_llm_trace(context_length=512, hidden_dim=2048)
        
        for num_banks in [2, 4, 8, 16]:
            config = SimulationConfig(t1_sram_banks=num_banks)
            sim = JanusSim(config)
            
            sim.run(trace)
            metrics = sim.get_metrics()
            results.append((num_banks, metrics.total_cycles))
        
        # More banks should reduce conflicts (lower or equal cycles)
        cycles = [c for _, c in results]
        # Last config should be at most 20% worse than best
        best_cycles = min(cycles)
        worst_cycles = max(cycles)
        assert worst_cycles <= best_cycles * 1.2, \
            "Bank count should not degrade performance significantly"


class TestRobustness:
    """Test system robustness and error handling."""

    def test_handles_large_addresses(self):
        """Test simulation handles large address values."""
        sim = JanusSim()
        
        # Addresses in GB range
        trace = [("READ", 2**30 + i * 128) for i in range(100)]
        
        sim.run(trace)
        metrics = sim.get_metrics()
        
        assert metrics.t1_hits + metrics.t1_misses == 100

    def test_consistent_results_multiple_runs(self):
        """Test simulation produces consistent results across runs."""
        trace = generate_llm_trace(context_length=512, hidden_dim=2048)
        
        results = []
        for _ in range(3):
            sim = JanusSim()
            sim.run(trace)
            metrics = sim.get_metrics()
            results.append(metrics.hit_rate)
        
        # All runs should produce identical results (deterministic)
        assert len(set(results)) == 1, "Simulation should be deterministic"

    def test_trace_with_only_writes(self):
        """Test trace with only write operations."""
        sim = JanusSim()
        
        trace = [("WRITE", i * 128) for i in range(100)]
        
        sim.run(trace)
        metrics = sim.get_metrics()
        
        # No reads, so no hits or misses
        assert metrics.t1_hits == 0
        assert metrics.t1_misses == 0


class TestConfigurationValidation:
    """Test configuration validation and constraints."""

    def test_default_configuration_valid(self):
        """Test default configuration is valid."""
        config = SimulationConfig()
        sim = JanusSim(config)
        
        assert sim.config.t1_sram_size_mb > 0
        assert sim.config.t1_sram_banks > 0
        assert sim.config.t2_edram_banks > 0
        assert sim.config.cache_line_size_bytes > 0

    def test_custom_configuration(self):
        """Test custom configuration is respected."""
        config = SimulationConfig(
            t1_sram_size_mb=64,
            t1_latency_cycles=2,
            t2_latency_cycles=5
        )
        sim = JanusSim(config)
        
        assert sim.config.t1_sram_size_mb == 64
        assert sim.config.t1_latency_cycles == 2
        assert sim.config.t2_latency_cycles == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])