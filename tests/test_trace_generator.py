"""Tests for memory trace generator."""

import pytest
import numpy as np
from src.benchmarks.trace_generator import (
    LLMTraceGenerator,
    generate_llm_trace,
    TraceStatistics
)


def test_trace_generator_initialization():
    """Test basic initialization of trace generator."""
    gen = LLMTraceGenerator(
        context_length=1024,
        hidden_dim=2048,
        num_layers=16,
        seed=42
    )
    
    assert gen.context_length == 1024
    assert gen.hidden_dim == 2048
    assert gen.num_layers == 16
    assert gen.head_dim == 2048 // 32  # Default num_heads=32


def test_generate_attention_trace():
    """Test generation of attention memory trace."""
    gen = LLMTraceGenerator(context_length=512, hidden_dim=1024, num_layers=8, seed=42)
    trace = gen.generate_attention_trace(generation_length=1)
    
    assert len(trace) > 0
    assert all(isinstance(op, str) and isinstance(addr, int) for op, addr in trace)
    assert all(op in ['READ', 'WRITE'] for op, _ in trace)


def test_generate_prefill_trace():
    """Test generation of prefill trace."""
    gen = LLMTraceGenerator(context_length=256, hidden_dim=512, num_layers=4, seed=42)
    trace = gen.generate_prefill_trace()
    
    # Prefill should have writes for all tokens in all layers
    expected_writes = gen.context_length * gen.num_layers
    assert len(trace) == expected_writes
    assert all(op == 'WRITE' for op, _ in trace)


def test_trace_addresses_aligned():
    """Test that all addresses are cache-line aligned."""
    gen = LLMTraceGenerator(context_length=128, cache_line_size=128, seed=42)
    trace = gen.generate_attention_trace(generation_length=1, add_noise=False)
    
    for _, addr in trace:
        assert addr % gen.cache_line_size == 0, f"Address {addr} not aligned"


def test_compute_statistics():
    """Test computation of trace statistics."""
    gen = LLMTraceGenerator(context_length=512, hidden_dim=1024, seed=42)
    trace = gen.generate_attention_trace(generation_length=1, add_noise=False)
    stats = gen.compute_statistics(trace)
    
    assert isinstance(stats, TraceStatistics)
    assert stats.total_accesses == len(trace)
    assert stats.unique_addresses > 0
    assert 0 <= stats.spatial_locality <= 1
    assert 0 <= stats.temporal_locality <= 1
    assert stats.address_entropy >= 0


def test_high_spatial_locality():
    """Test that sequential accesses have high spatial locality."""
    gen = LLMTraceGenerator(context_length=256, hidden_dim=512, seed=42)
    trace = gen.generate_attention_trace(generation_length=1, add_noise=False)
    stats = gen.compute_statistics(trace)
    
    # Without noise, should have very high spatial locality
    assert stats.spatial_locality > 0.85


def test_noise_reduces_spatial_locality():
    """Test that adding noise reduces spatial locality."""
    gen = LLMTraceGenerator(context_length=256, hidden_dim=512, seed=42)
    
    trace_no_noise = gen.generate_attention_trace(generation_length=1, add_noise=False)
    stats_no_noise = gen.compute_statistics(trace_no_noise)
    
    trace_with_noise = gen.generate_attention_trace(generation_length=1, add_noise=True, noise_level=0.1)
    stats_with_noise = gen.compute_statistics(trace_with_noise)
    
    assert stats_with_noise.spatial_locality < stats_no_noise.spatial_locality


def test_validate_trace_all_pass():
    """Test trace validation with clean trace."""
    gen = LLMTraceGenerator(context_length=512, hidden_dim=1024, seed=42)
    trace = gen.generate_attention_trace(generation_length=1, add_noise=False)
    validations = gen.validate_trace(trace)
    
    # All validations should pass for clean trace
    assert all(validations.values()), f"Some validations failed: {validations}"


def test_stride_distribution():
    """Test that stride distribution is computed correctly."""
    gen = LLMTraceGenerator(context_length=256, hidden_dim=512, seed=42)
    trace = gen.generate_attention_trace(generation_length=1, add_noise=False)
    stats = gen.compute_statistics(trace)
    
    # Should have stride distribution
    assert len(stats.stride_distribution) > 0
    
    # Most common stride should be cache_line_size for sequential access
    most_common_stride = max(stats.stride_distribution, key=stats.stride_distribution.get)
    assert most_common_stride == gen.cache_line_size or most_common_stride == -gen.cache_line_size


def test_working_set_size():
    """Test working set size calculation."""
    gen = LLMTraceGenerator(
        context_length=1024,
        hidden_dim=4096,
        num_layers=32,
        precision_bytes=0.5,  # INT4
        seed=42
    )
    trace = gen.generate_attention_trace(generation_length=1, add_noise=False)
    stats = gen.compute_statistics(trace)
    
    # Working set should be reasonable for model size
    # Roughly: 32 layers * 1024 tokens * 2 * 4096 * 0.5 bytes
    expected_kb = (32 * 1024 * 2 * 4096 * 0.5) / 1024
    
    # Allow 50% tolerance due to cache line effects
    assert 0.5 * expected_kb < stats.working_set_size_kb < 1.5 * expected_kb


def test_generate_report():
    """Test report generation."""
    gen = LLMTraceGenerator(context_length=256, hidden_dim=512, seed=42)
    trace = gen.generate_attention_trace(generation_length=1)
    report = gen.generate_report(trace)
    
    assert isinstance(report, str)
    assert len(report) > 0
    assert "MEMORY TRACE ANALYSIS REPORT" in report
    assert "Spatial Locality" in report
    assert "Validation Checks" in report


def test_convenience_function():
    """Test convenience function for trace generation."""
    trace = generate_llm_trace(
        context_length=512,
        hidden_dim=1024,
        num_layers=16,
        generation_length=1,
        seed=42
    )
    
    assert len(trace) > 0
    assert all(isinstance(op, str) and isinstance(addr, int) for op, addr in trace)


def test_reproducibility_with_seed():
    """Test that same seed produces same trace."""
    trace1 = generate_llm_trace(context_length=256, seed=42)
    trace2 = generate_llm_trace(context_length=256, seed=42)
    
    assert trace1 == trace2


def test_different_seeds_different_traces():
    """Test that different seeds produce different traces with noise."""
    trace1 = generate_llm_trace(context_length=256, seed=42)
    trace2 = generate_llm_trace(context_length=256, seed=123)
    
    # Traces should be different when noise is involved
    # (though structure may be similar)
    assert trace1 != trace2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
