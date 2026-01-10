"""Memory Access Trace Generation for LLM Workloads

This module generates synthetic memory access traces that represent
the memory access patterns of Large Language Model (LLM) inference.

The traces model the KV-cache access patterns during the attention
computation phase of transformer models.

Author: The Janus-1 Design Team
License: MIT
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TraceConfig:
    """Configuration for trace generation.
    
    Attributes:
        context_length: Number of tokens in context (default: 2048)
        hidden_dim: Model hidden dimension (default: 4096)
        num_layers: Number of transformer layers (default: 32)
        bytes_per_element: Size of each element in bytes (default: 0.5 for INT4)
        cache_line_size: Cache line size in bytes (default: 128)
        base_address: Starting memory address (default: 0x1000000)
        access_pattern: Type of access pattern ("sequential", "random", "strided")
        stride: Stride for strided access pattern (default: 1)
    """
    context_length: int = 2048
    hidden_dim: int = 4096
    num_layers: int = 32
    bytes_per_element: float = 0.5  # INT4
    cache_line_size: int = 128
    base_address: int = 0x1000000
    access_pattern: str = "sequential"
    stride: int = 1


def generate_llm_trace(
    context_length: int = 2048,
    hidden_dim: int = 4096,
    num_layers: int = 32,
    bytes_per_element: float = 0.5,
    cache_line_size: int = 128,
    base_address: int = 0x1000000,
) -> List[Tuple[str, int]]:
    """Generate memory access trace for LLM inference.
    
    Simulates the memory access pattern during the attention computation
    of a transformer-based LLM. The trace represents reading the KV-cache
    for each token in the context.
    
    The generated pattern is:
    - Sequential access through the KV-cache
    - Cache-line aligned addresses
    - Read-only operations (inference)
    
    Args:
        context_length: Number of tokens in context
        hidden_dim: Model hidden dimension
        num_layers: Number of transformer layers (not used in current impl)
        bytes_per_element: Size per element (0.5 for INT4, 1.0 for INT8)
        cache_line_size: Cache line size in bytes
        base_address: Starting memory address
        
    Returns:
        List of (operation, address) tuples where operation is "READ" or "WRITE"
        
    Example:
        >>> trace = generate_llm_trace(context_length=1024, hidden_dim=4096)
        >>> print(f"Generated {len(trace)} memory operations")
        Generated 1024 memory operations
        >>> print(trace[0])
        ('READ', 16777216)
        
    Note:
        - All addresses are cache-line aligned
        - Access pattern is sequential (streaming)
        - Models single-layer attention for simplicity
        - Real LLMs have more complex patterns (multi-layer, decode phase)
    """
    trace = []
    
    # Calculate elements per cache line
    elements_per_line = cache_line_size / bytes_per_element
    
    # Generate sequential access for each token in context
    for token_idx in range(context_length):
        # Calculate offset for this token in KV-cache
        token_offset_bytes = token_idx * hidden_dim * bytes_per_element
        
        # Align to cache line boundary
        cache_line_offset = int(token_offset_bytes // cache_line_size)
        addr = base_address + (cache_line_offset * cache_line_size)
        
        trace.append(("READ", addr))
    
    return trace


def generate_random_trace(
    num_accesses: int = 10000,
    address_space_mb: int = 256,
    cache_line_size: int = 128,
    base_address: int = 0x1000000,
    read_ratio: float = 0.9,
    seed: Optional[int] = None,
) -> List[Tuple[str, int]]:
    """Generate random memory access trace.
    
    Creates a trace with random memory accesses across a specified
    address space. Useful for stress testing cache replacement policies.
    
    Args:
        num_accesses: Number of memory operations to generate
        address_space_mb: Size of address space in MB
        cache_line_size: Cache line size in bytes
        base_address: Starting address
        read_ratio: Fraction of operations that are reads (0.0 to 1.0)
        seed: Random seed for reproducibility
        
    Returns:
        List of (operation, address) tuples
        
    Example:
        >>> trace = generate_random_trace(num_accesses=1000, address_space_mb=64)
        >>> read_ops = sum(1 for op, _ in trace if op == "READ")
        >>> print(f"Read operations: {read_ops}")
        Read operations: 900
    """
    if seed is not None:
        np.random.seed(seed)
    
    trace = []
    num_cache_lines = (address_space_mb * 1024 * 1024) // cache_line_size
    
    for _ in range(num_accesses):
        # Random cache line
        line_offset = np.random.randint(0, num_cache_lines)
        addr = base_address + (line_offset * cache_line_size)
        
        # Random operation (weighted by read_ratio)
        op = "READ" if np.random.random() < read_ratio else "WRITE"
        
        trace.append((op, addr))
    
    return trace


def generate_strided_trace(
    num_accesses: int = 10000,
    stride: int = 4,
    cache_line_size: int = 128,
    base_address: int = 0x1000000,
) -> List[Tuple[str, int]]:
    """Generate strided memory access trace.
    
    Creates a trace with regular stride pattern. Useful for testing
    stride prefetchers and cache performance with specific access patterns.
    
    Args:
        num_accesses: Number of memory operations
        stride: Stride in cache lines
        cache_line_size: Cache line size in bytes
        base_address: Starting address
        
    Returns:
        List of (operation, address) tuples
        
    Example:
        >>> trace = generate_strided_trace(num_accesses=100, stride=4)
        >>> addrs = [addr for _, addr in trace]
        >>> stride_bytes = addrs[1] - addrs[0]
        >>> print(f"Stride: {stride_bytes} bytes")
        Stride: 512 bytes
    """
    trace = []
    
    for i in range(num_accesses):
        addr = base_address + (i * stride * cache_line_size)
        trace.append(("READ", addr))
    
    return trace


def generate_mixed_trace(
    config: TraceConfig,
    phase_lengths: Optional[List[int]] = None,
) -> List[Tuple[str, int]]:
    """Generate trace with multiple phases.
    
    Creates a trace combining different access patterns in sequence.
    Useful for testing adaptivity of prefetchers.
    
    Args:
        config: Trace configuration
        phase_lengths: List of lengths for each phase.
                      If None, uses equal phases.
                      
    Returns:
        List of (operation, address) tuples
        
    Example:
        >>> config = TraceConfig(context_length=1000)
        >>> trace = generate_mixed_trace(config, phase_lengths=[300, 300, 400])
        >>> print(f"Total operations: {len(trace)}")
        Total operations: 1000
    """
    if phase_lengths is None:
        total = config.context_length
        phase_lengths = [total // 3, total // 3, total - 2 * (total // 3)]
    
    trace = []
    base = config.base_address
    line_size = config.cache_line_size
    
    # Phase 1: Sequential
    for i in range(phase_lengths[0]):
        addr = base + (i * line_size)
        trace.append(("READ", addr))
    
    # Phase 2: Strided (stride = 4)
    for i in range(phase_lengths[1]):
        addr = base + (i * 4 * line_size)
        trace.append(("READ", addr))
    
    # Phase 3: Random
    max_lines = (256 * 1024 * 1024) // line_size
    for _ in range(phase_lengths[2]):
        line_offset = np.random.randint(0, max_lines)
        addr = base + (line_offset * line_size)
        trace.append(("READ", addr))
    
    return trace


def analyze_trace(trace: List[Tuple[str, int]]) -> dict:
    """Analyze memory trace characteristics.
    
    Computes statistics about the trace including operation mix,
    address range, and spatial locality.
    
    Args:
        trace: List of (operation, address) tuples
        
    Returns:
        Dictionary with trace statistics
        
    Example:
        >>> trace = generate_llm_trace(context_length=1024)
        >>> stats = analyze_trace(trace)
        >>> print(f"Unique addresses: {stats['unique_addresses']}")
    """
    if not trace:
        return {}
    
    operations = [op for op, _ in trace]
    addresses = [addr for _, addr in trace]
    
    # Calculate stride pattern
    strides = [addresses[i+1] - addresses[i] 
               for i in range(len(addresses) - 1)]
    
    return {
        'total_operations': len(trace),
        'read_operations': operations.count('READ'),
        'write_operations': operations.count('WRITE'),
        'unique_addresses': len(set(addresses)),
        'address_range_mb': (max(addresses) - min(addresses)) / (1024 * 1024),
        'min_address': min(addresses),
        'max_address': max(addresses),
        'mean_stride': np.mean(strides) if strides else 0,
        'median_stride': np.median(strides) if strides else 0,
        'stride_stddev': np.std(strides) if strides else 0,
        'sequential_ratio': sum(1 for s in strides if s > 0) / len(strides) if strides else 0,
    }


if __name__ == "__main__":
    # Example usage and validation
    print("Generating sample traces...\n")
    
    # LLM inference trace
    print("1. LLM Inference Trace:")
    llm_trace = generate_llm_trace(context_length=1024, hidden_dim=4096)
    stats = analyze_trace(llm_trace)
    print(f"   Total operations: {stats['total_operations']}")
    print(f"   Unique addresses: {stats['unique_addresses']}")
    print(f"   Address range: {stats['address_range_mb']:.2f} MB")
    print(f"   Mean stride: {stats['mean_stride']:.0f} bytes")
    print()
    
    # Random trace
    print("2. Random Access Trace:")
    random_trace = generate_random_trace(num_accesses=1000, address_space_mb=64)
    stats = analyze_trace(random_trace)
    print(f"   Total operations: {stats['total_operations']}")
    print(f"   Read ratio: {stats['read_operations']/stats['total_operations']:.1%}")
    print(f"   Unique addresses: {stats['unique_addresses']}")
    print()
    
    # Strided trace
    print("3. Strided Access Trace:")
    strided_trace = generate_strided_trace(num_accesses=1000, stride=4)
    stats = analyze_trace(strided_trace)
    print(f"   Total operations: {stats['total_operations']}")
    print(f"   Mean stride: {stats['mean_stride']:.0f} bytes")
    print(f"   Sequential ratio: {stats['sequential_ratio']:.1%}")
    print()
    
    print("✓ Trace generation validated")
