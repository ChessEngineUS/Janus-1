#!/usr/bin/env python3
"""
Basic Memory Hierarchy Simulation
==================================

This example demonstrates how to run a simple cycle-accurate simulation
of the Janus-1 memory hierarchy with the Janus-Prefetch-1 engine.

Expected Output:
    T1 Hit Rate: 99.99%
    Average Latency: ~1.0 cycles
    Total Cycles: ~65536

Author: Janus-1 Research Team
License: MIT
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulator.janus_sim import JanusSim
from src.benchmarks.trace_generator import generate_llm_trace


def main():
    """Run basic memory hierarchy simulation."""
    
    print("=" * 60)
    print("Janus-1 Basic Memory Hierarchy Simulation")
    print("=" * 60)
    print()
    
    # Configuration
    context_length = 2048  # Tokens in context
    hidden_dim = 4096      # Model hidden dimension
    num_layers = 32        # Transformer layers
    
    print(f"Configuration:")
    print(f"  Context Length: {context_length} tokens")
    print(f"  Hidden Dimension: {hidden_dim}")
    print(f"  Layers: {num_layers}")
    print()
    
    # Generate synthetic workload trace
    print("Generating LLM inference trace...")
    trace = generate_llm_trace(
        context_length=context_length,
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        quantization='int4'  # 4-bit quantization
    )
    print(f"Generated {len(trace)} memory accesses")
    print()
    
    # Initialize simulator with default Janus-1 configuration
    print("Initializing Janus-1 simulator...")
    sim = JanusSim(
        t1_size_mb=32,        # 32 MB SRAM (T1)
        t2_size_mb=224,       # 224 MB eDRAM (T2)
        prefetch_depth=16,    # 16-line look-ahead
        cache_line_bytes=64   # 64-byte cache lines
    )
    print("Simulator initialized")
    print()
    
    # Run simulation
    print("Running cycle-accurate simulation...")
    results = sim.run(trace)
    print("Simulation complete")
    print()
    
    # Display results
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print()
    
    print(f"Memory Hierarchy Performance:")
    print(f"  T1 Hit Rate: {results['t1_hit_rate']:.2f}%")
    print(f"  T2 Hit Rate: {results['t2_hit_rate']:.2f}%")
    print(f"  Total Accesses: {results['total_accesses']:,}")
    print()
    
    print(f"Latency Statistics (cycles):")
    print(f"  Average: {results['avg_latency']:.2f}")
    print(f"  Median (P50): {results['p50_latency']:.2f}")
    print(f"  P90: {results['p90_latency']:.2f}")
    print(f"  P99: {results['p99_latency']:.2f}")
    print()
    
    print(f"Prefetcher Performance:")
    print(f"  Prefetch Accuracy: {results['prefetch_accuracy']:.2f}%")
    print(f"  Useful Prefetches: {results['useful_prefetches']:,}")
    print(f"  Wasted Prefetches: {results['wasted_prefetches']:,}")
    print()
    
    print(f"Total Simulation Cycles: {results['total_cycles']:,}")
    print()
    
    # Validation
    if results['t1_hit_rate'] > 99.9:
        print("✅ PASS: Hit rate exceeds 99.9% target")
    else:
        print("⚠️  WARNING: Hit rate below expected performance")
    
    print()
    print("Simulation complete. Results saved to results/basic_sim.json")
    
    # Save results
    sim.save_results('results/basic_sim.json')
    
    return results


if __name__ == "__main__":
    main()
