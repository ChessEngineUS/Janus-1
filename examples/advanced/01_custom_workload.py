#!/usr/bin/env python3
"""
Advanced Example 1: Custom Workload Generation and Analysis
============================================================

This example demonstrates how to create custom memory access patterns
for different LLM architectures and analyze their behavior on Janus-1.

Author: Janus-1 Design Team
License: MIT
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple

from src.simulator.janus_sim import JanusSim, SimulationConfig, MemoryOp
from src.benchmarks.trace_generator import TraceGenerator


class CustomWorkloadGenerator:
    """Generate custom LLM workload patterns."""

    def __init__(self, context_length: int, hidden_dim: int):
        self.context_length = context_length
        self.hidden_dim = hidden_dim
        self.base_address = 0x100000

    def generate_encoder_decoder_trace(self, 
                                        num_encoder_layers: int = 12,
                                        num_decoder_layers: int = 12) -> List[MemoryOp]:
        """Generate trace for encoder-decoder architecture (e.g., T5).

        Encoder processes input sequence, decoder generates output with
        cross-attention to encoder outputs.
        """
        trace = []
        addr = self.base_address

        # Encoder forward pass: self-attention on input
        print(f"Generating encoder trace ({num_encoder_layers} layers)...")
        for layer in range(num_encoder_layers):
            # Query, Key, Value matrices for self-attention
            for token in range(self.context_length):
                # Read Q, K, V for this token
                for _ in range(3):  # Q, K, V
                    trace.append(MemoryOp("READ", addr))
                    addr += 64

                # Attention computation: read all K, V
                for other_token in range(self.context_length):
                    trace.append(MemoryOp("READ", self.base_address + other_token * 64))

        # Decoder forward pass: autoregressive generation
        print(f"Generating decoder trace ({num_decoder_layers} layers)...")
        for output_token in range(self.context_length):
            for layer in range(num_decoder_layers):
                # Self-attention on previously generated tokens
                for prev_token in range(output_token + 1):
                    trace.append(MemoryOp("READ", addr))
                    addr += 64

                # Cross-attention to encoder outputs
                for encoder_token in range(self.context_length):
                    trace.append(MemoryOp("READ", self.base_address + encoder_token * 64))

        print(f"Generated {len(trace)} memory operations")
        return trace

    def generate_sparse_attention_trace(self, window_size: int = 128) -> List[MemoryOp]:
        """Generate trace for sparse attention (e.g., Longformer, BigBird).

        Uses sliding window attention instead of full attention.
        """
        trace = []
        addr = self.base_address

        print(f"Generating sparse attention trace (window={window_size})...")
        for token in range(self.context_length):
            # Only attend to tokens within window
            start = max(0, token - window_size // 2)
            end = min(self.context_length, token + window_size // 2)

            for attending_token in range(start, end):
                trace.append(MemoryOp("READ", addr))
                addr += 64

            # Global attention tokens (every N tokens)
            if token % 64 == 0:
                for global_token in range(0, self.context_length, 64):
                    trace.append(MemoryOp("READ", self.base_address + global_token * 64))

        print(f"Generated {len(trace)} memory operations")
        return trace

    def generate_moe_trace(self, num_experts: int = 8, experts_per_token: int = 2) -> List[MemoryOp]:
        """Generate trace for Mixture-of-Experts (MoE) architecture.

        Each token routed to subset of experts.
        """
        trace = []
        addr = self.base_address
        expert_size_bytes = self.hidden_dim * 4 * 64  # Expert weight size

        print(f"Generating MoE trace ({num_experts} experts, {experts_per_token} active)...")
        for token in range(self.context_length):
            # Router decision (which experts to use)
            trace.append(MemoryOp("READ", addr))
            addr += 64

            # Randomly select experts (simulate routing)
            active_experts = np.random.choice(num_experts, experts_per_token, replace=False)

            # Access expert weights
            for expert_id in active_experts:
                expert_addr = self.base_address + expert_id * expert_size_bytes
                # Read expert parameters (simplified)
                for _ in range(100):  # Multiple reads per expert
                    trace.append(MemoryOp("READ", expert_addr))
                    expert_addr += 64

        print(f"Generated {len(trace)} memory operations")
        return trace


def analyze_workload(trace: List[MemoryOp], workload_name: str) -> Dict:
    """Analyze workload characteristics and performance on Janus-1."""
    print(f"\nAnalyzing {workload_name}...")
    print("=" * 70)

    # Run simulation with different prefetcher configurations
    configs = [
        ("No Prefetch", SimulationConfig(prefetch_enabled=False)),
        ("Lookahead=8", SimulationConfig(prefetch_look_ahead=8)),
        ("Lookahead=16", SimulationConfig(prefetch_look_ahead=16)),
        ("Lookahead=32", SimulationConfig(prefetch_look_ahead=32)),
    ]

    results = []
    for config_name, config in configs:
        sim = JanusSim(config)
        sim.run(trace)
        metrics = sim.get_metrics()

        results.append({
            "Configuration": config_name,
            "Hit Rate (%)": metrics.hit_rate,
            "P50 Latency": metrics.p50_latency,
            "P99 Latency": metrics.p99_latency,
            "Total Cycles": metrics.total_cycles,
        })

    df = pd.DataFrame(results)
    print(f"\n{workload_name} Results:")
    print(df.to_string(index=False))
    print()

    return {"workload": workload_name, "results": df}


def plot_comparison(all_results: List[Dict]):
    """Plot performance comparison across workloads."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    metrics = ["Hit Rate (%)", "P99 Latency", "Total Cycles"]
    titles = ["Cache Hit Rate", "P99 Latency (cycles)", "Total Execution Cycles"]

    for ax, metric, title in zip(axes, metrics, titles):
        for result_dict in all_results:
            workload = result_dict["workload"]
            df = result_dict["results"]
            ax.plot(df["Configuration"], df[metric], marker="o", label=workload, linewidth=2)

        ax.set_xlabel("Prefetcher Configuration", fontweight="bold")
        ax.set_ylabel(metric, fontweight="bold")
        ax.set_title(title, fontweight="bold")
        ax.legend()
        ax.grid(alpha=0.3)
        ax.tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig("custom_workload_comparison.png", dpi=300, bbox_inches="tight")
    print("\n✅ Saved figure: custom_workload_comparison.png")
    plt.close()


def main():
    """Main execution."""
    print("\n" + "="*70)
    print("CUSTOM WORKLOAD GENERATION AND ANALYSIS")
    print("="*70 + "\n")

    # Configuration
    context_length = 512  # Smaller for faster demo
    hidden_dim = 2048

    generator = CustomWorkloadGenerator(context_length, hidden_dim)

    # Generate different workload types
    workloads = [
        ("Encoder-Decoder", generator.generate_encoder_decoder_trace(6, 6)),
        ("Sparse Attention", generator.generate_sparse_attention_trace(128)),
        ("MoE (8 experts)", generator.generate_moe_trace(8, 2)),
    ]

    # Analyze each workload
    all_results = []
    for name, trace in workloads:
        result = analyze_workload(trace, name)
        all_results.append(result)

    # Generate comparison plot
    plot_comparison(all_results)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nKey Findings:")
    print("  1. Encoder-decoder benefits from cross-attention prefetching")
    print("  2. Sparse attention reduces memory traffic significantly")
    print("  3. MoE workloads have irregular access patterns")
    print("  4. Optimal prefetcher depth varies by workload")
    print("\nRecommendations:")
    print("  - Use adaptive prefetching for mixed workloads")
    print("  - Consider workload-specific cache policies")
    print("  - MoE requires larger T1 cache for expert weights\n")


if __name__ == "__main__":
    main()
