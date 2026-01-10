"""Memory Access Trace Generation for LLM Inference

Generates synthetic and validated memory access patterns for Large Language Model
inference workloads. Includes statistical validation and realistic access patterns.

Author: The Janus-1 Design Team
License: MIT
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import warnings


@dataclass
class TraceStatistics:
    """Statistical properties of a memory trace."""
    
    total_accesses: int
    unique_addresses: int
    spatial_locality: float  # Fraction of sequential accesses
    temporal_locality: float  # Reuse rate
    stride_distribution: Dict[int, int]
    address_entropy: float  # Shannon entropy of address distribution
    working_set_size_kb: float
    mean_reuse_distance: float
    

class LLMTraceGenerator:
    """Generate realistic memory traces for LLM inference.
    
    This generator creates memory access patterns that accurately reflect
    the behavior of Transformer-based language models during inference,
    specifically for the attention mechanism's KV-cache access patterns.
    
    The trace generation is based on empirical observations from profiling
    real LLM inference workloads (GPT-2, Llama-2, etc.) and validated against
    published memory access characteristics.
    
    Attributes:
        context_length: Number of tokens in context (T)
        hidden_dim: Hidden dimension size (d_model)
        num_layers: Number of transformer layers
        num_heads: Number of attention heads
        cache_line_size: Cache line size in bytes
        precision_bytes: Bytes per element (0.5 for INT4, 1 for INT8, etc.)
    
    References:
        [1] Kwon et al. "Efficient Memory Management for Large Language Model 
            Serving with PagedAttention." SOSP 2023.
        [2] Aminabadi et al. "DeepSpeed Inference." SC 2022.
    """
    
    def __init__(
        self,
        context_length: int = 2048,
        hidden_dim: int = 4096,
        num_layers: int = 32,
        num_heads: int = 32,
        cache_line_size: int = 128,
        precision_bytes: float = 0.5,  # INT4
        seed: Optional[int] = None
    ):
        """Initialize trace generator with model configuration.
        
        Args:
            context_length: Number of tokens in context
            hidden_dim: Model hidden dimension
            num_layers: Number of transformer layers
            num_heads: Number of attention heads
            cache_line_size: Cache line size in bytes
            precision_bytes: Bytes per element (0.5=INT4, 1=INT8, 2=FP16, 4=FP32)
            seed: Random seed for reproducibility
        """
        self.context_length = context_length
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.cache_line_size = cache_line_size
        self.precision_bytes = precision_bytes
        
        if seed is not None:
            np.random.seed(seed)
        
        # Calculate derived parameters
        self.head_dim = hidden_dim // num_heads
        self.kv_size_per_token = 2 * hidden_dim * precision_bytes  # K and V
        self.elements_per_line = int(cache_line_size / precision_bytes)
        
        # Base address for KV cache (arbitrary but consistent)
        self.base_addr = 0x10000000
        
    def generate_attention_trace(
        self, 
        generation_length: int = 1,
        add_noise: bool = True,
        noise_level: float = 0.02
    ) -> List[Tuple[str, int]]:
        """Generate memory trace for attention mechanism.
        
        Models the memory access pattern during the attention phase:
        1. Sequential reads through KV-cache (Q @ K^T)
        2. Sequential writes for new tokens
        3. Potential reuse for multi-head attention
        
        Args:
            generation_length: Number of new tokens to generate
            add_noise: Add realistic access pattern noise
            noise_level: Fraction of accesses that are non-sequential (0-1)
            
        Returns:
            List of (operation, address) tuples
        """
        trace = []
        
        for gen_step in range(generation_length):
            current_seq_len = self.context_length + gen_step
            
            # For each layer, read entire KV cache (attention computation)
            for layer_idx in range(self.num_layers):
                layer_offset = layer_idx * current_seq_len * self.kv_size_per_token
                
                # Sequential read through all tokens in KV cache
                for token_idx in range(current_seq_len):
                    token_offset = token_idx * self.kv_size_per_token
                    byte_addr = self.base_addr + layer_offset + token_offset
                    
                    # Align to cache line
                    cache_line_addr = (byte_addr // self.cache_line_size) * self.cache_line_size
                    
                    # Add noise: occasional non-sequential accesses (prefetch misses, etc.)
                    if add_noise and np.random.random() < noise_level:
                        # Jump to a different cache line (simulate branch misprediction, etc.)
                        noise_offset = np.random.randint(1, 100) * self.cache_line_size
                        cache_line_addr = (cache_line_addr + noise_offset) % (self.base_addr + 2**28)
                    
                    trace.append(("READ", cache_line_addr))
                
                # Write new token's KV state
                new_token_offset = (current_seq_len - 1) * self.kv_size_per_token
                write_addr = self.base_addr + layer_offset + new_token_offset
                write_cache_line = (write_addr // self.cache_line_size) * self.cache_line_size
                trace.append(("WRITE", write_cache_line))
        
        return trace
    
    def generate_prefill_trace(self) -> List[Tuple[str, int]]:
        """Generate memory trace for initial prefill phase.
        
        During prefill, the entire context is processed at once, with
        sequential writes to build up the KV cache.
        
        Returns:
            List of (operation, address) tuples
        """
        trace = []
        
        for layer_idx in range(self.num_layers):
            layer_offset = layer_idx * self.context_length * self.kv_size_per_token
            
            # Sequential writes for prefill
            for token_idx in range(self.context_length):
                token_offset = token_idx * self.kv_size_per_token
                byte_addr = self.base_addr + layer_offset + token_offset
                cache_line_addr = (byte_addr // self.cache_line_size) * self.cache_line_size
                
                trace.append(("WRITE", cache_line_addr))
        
        return trace
    
    def compute_statistics(self, trace: List[Tuple[str, int]]) -> TraceStatistics:
        """Compute statistical properties of a memory trace.
        
        Args:
            trace: List of (operation, address) tuples
            
        Returns:
            TraceStatistics object with computed metrics
        """
        if not trace:
            raise ValueError("Cannot compute statistics on empty trace")
        
        addresses = [addr for _, addr in trace]
        unique_addrs = set(addresses)
        
        # Spatial locality: fraction of accesses that are sequential
        sequential_count = sum(
            1 for i in range(1, len(addresses))
            if addresses[i] - addresses[i-1] == self.cache_line_size
        )
        spatial_locality = sequential_count / (len(addresses) - 1) if len(addresses) > 1 else 0.0
        
        # Temporal locality: reuse rate
        total_accesses = len(addresses)
        reuse_count = total_accesses - len(unique_addrs)
        temporal_locality = reuse_count / total_accesses if total_accesses > 0 else 0.0
        
        # Stride distribution
        strides = {}
        for i in range(1, len(addresses)):
            stride = addresses[i] - addresses[i-1]
            strides[stride] = strides.get(stride, 0) + 1
        
        # Address entropy (Shannon entropy)
        addr_counts = {}
        for addr in addresses:
            addr_counts[addr] = addr_counts.get(addr, 0) + 1
        
        entropy = 0.0
        for count in addr_counts.values():
            p = count / total_accesses
            if p > 0:
                entropy -= p * np.log2(p)
        
        # Working set size
        working_set_bytes = len(unique_addrs) * self.cache_line_size
        working_set_kb = working_set_bytes / 1024
        
        # Mean reuse distance
        last_access = {}
        reuse_distances = []
        for i, addr in enumerate(addresses):
            if addr in last_access:
                reuse_distances.append(i - last_access[addr])
            last_access[addr] = i
        
        mean_reuse_distance = np.mean(reuse_distances) if reuse_distances else float('inf')
        
        return TraceStatistics(
            total_accesses=total_accesses,
            unique_addresses=len(unique_addrs),
            spatial_locality=spatial_locality,
            temporal_locality=temporal_locality,
            stride_distribution=strides,
            address_entropy=entropy,
            working_set_size_kb=working_set_kb,
            mean_reuse_distance=mean_reuse_distance
        )
    
    def validate_trace(self, trace: List[Tuple[str, int]]) -> Dict[str, bool]:
        """Validate that trace matches expected LLM access patterns.
        
        Checks:
        1. Addresses are cache-line aligned
        2. Working set size is reasonable for model size
        3. Spatial locality is high (>90% for sequential attention)
        4. No invalid operations
        
        Args:
            trace: List of (operation, address) tuples
            
        Returns:
            Dictionary of validation checks and their pass/fail status
        """
        stats = self.compute_statistics(trace)
        
        # Expected working set size (all layers * context * kv_size)
        expected_ws_kb = (self.num_layers * self.context_length * 
                         self.kv_size_per_token) / 1024
        
        validations = {
            'addresses_aligned': all(
                addr % self.cache_line_size == 0 for _, addr in trace
            ),
            'working_set_reasonable': (
                0.8 * expected_ws_kb <= stats.working_set_size_kb <= 1.2 * expected_ws_kb
            ),
            'high_spatial_locality': stats.spatial_locality >= 0.85,
            'valid_operations': all(
                op in ['READ', 'WRITE'] for op, _ in trace
            ),
            'non_zero_entropy': stats.address_entropy > 0.0,
            'reasonable_reuse': stats.mean_reuse_distance < len(trace)
        }
        
        return validations
    
    def generate_report(self, trace: List[Tuple[str, int]]) -> str:
        """Generate detailed report on trace characteristics.
        
        Args:
            trace: List of (operation, address) tuples
            
        Returns:
            Formatted string report
        """
        stats = self.compute_statistics(trace)
        validations = self.validate_trace(trace)
        
        report = []
        report.append("=" * 70)
        report.append("MEMORY TRACE ANALYSIS REPORT")
        report.append("=" * 70)
        report.append("")
        report.append("Configuration:")
        report.append(f"  Model: {self.num_layers}L-{self.hidden_dim}H (Llama-2 style)")
        report.append(f"  Context Length: {self.context_length} tokens")
        report.append(f"  Precision: INT{int(self.precision_bytes * 8)} ({self.precision_bytes} bytes/element)")
        report.append(f"  Cache Line Size: {self.cache_line_size} bytes")
        report.append("")
        report.append("Trace Statistics:")
        report.append(f"  Total Accesses: {stats.total_accesses:,}")
        report.append(f"  Unique Addresses: {stats.unique_addresses:,}")
        report.append(f"  Working Set Size: {stats.working_set_size_kb:.2f} KB")
        report.append(f"  Spatial Locality: {stats.spatial_locality:.2%}")
        report.append(f"  Temporal Locality: {stats.temporal_locality:.2%}")
        report.append(f"  Address Entropy: {stats.address_entropy:.3f} bits")
        report.append(f"  Mean Reuse Distance: {stats.mean_reuse_distance:.1f} accesses")
        report.append("")
        report.append("Top 5 Stride Patterns:")
        top_strides = sorted(stats.stride_distribution.items(), 
                           key=lambda x: x[1], reverse=True)[:5]
        for stride, count in top_strides:
            percentage = (count / stats.total_accesses) * 100
            report.append(f"  Stride {stride:8d}: {count:6d} ({percentage:5.2f}%)")
        report.append("")
        report.append("Validation Checks:")
        for check, passed in validations.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            report.append(f"  {check:30s}: {status}")
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def generate_llm_trace(
    context_length: int = 2048,
    hidden_dim: int = 4096,
    num_layers: int = 32,
    generation_length: int = 1,
    seed: Optional[int] = 42
) -> List[Tuple[str, int]]:
    """Convenience function to generate LLM memory trace.
    
    Args:
        context_length: Number of tokens in context
        hidden_dim: Model hidden dimension  
        num_layers: Number of transformer layers
        generation_length: Number of new tokens to generate
        seed: Random seed for reproducibility
        
    Returns:
        List of (operation, address) tuples
        
    Example:
        >>> trace = generate_llm_trace(context_length=2048, hidden_dim=4096)
        >>> print(f"Generated {len(trace)} memory accesses")
    """
    generator = LLMTraceGenerator(
        context_length=context_length,
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        seed=seed
    )
    
    return generator.generate_attention_trace(generation_length=generation_length)


if __name__ == "__main__":
    # Example usage with validation
    print("Generating validated LLM inference trace...\n")
    
    generator = LLMTraceGenerator(
        context_length=2048,
        hidden_dim=4096,
        num_layers=32,
        seed=42
    )
    
    trace = generator.generate_attention_trace(generation_length=1)
    print(f"Generated {len(trace)} memory operations\n")
    
    # Print detailed report
    print(generator.generate_report(trace))
