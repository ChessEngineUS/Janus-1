"""Memory Trace Generation for LLM Inference Workloads.

This module generates synthetic memory access traces that mimic the behavior
of large language model inference, particularly the attention mechanism's
KV-cache access patterns.

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
        context_length: Number of tokens in context.
        hidden_dim: Hidden dimension size.
        cache_line_size: Cache line size in bytes.
        precision: Data precision ('FP32', 'FP16', 'INT8', 'INT4').
        base_addr: Starting memory address.
        num_layers: Number of transformer layers.
    """
    context_length: int = 2048
    hidden_dim: int = 4096
    cache_line_size: int = 128
    precision: str = "INT4"
    base_addr: int = 0x1000000
    num_layers: int = 32


class TraceGenerator:
    """Generate memory access traces for LLM inference.
    
    This class creates synthetic traces that model the sequential access
    pattern of transformer attention over KV-cache during inference.
    
    Example:
        >>> generator = TraceGenerator()
        >>> trace = generator.generate_attention_trace()
        >>> print(f"Generated {len(trace)} memory operations")
        Generated 2048 memory operations
    """
    
    PRECISION_BYTES = {
        'FP32': 4,
        'FP16': 2,
        'INT8': 1,
        'INT4': 0.5
    }
    
    def __init__(self, config: Optional[TraceConfig] = None):
        """Initialize trace generator.
        
        Args:
            config: Trace configuration. Uses defaults if None.
        """
        self.config = config or TraceConfig()
        self.bytes_per_element = self.PRECISION_BYTES[self.config.precision]
    
    def generate_attention_trace(
        self, 
        layer_id: int = 0,
        read_only: bool = True
    ) -> List[Tuple[str, int]]:
        """Generate trace for attention phase over KV-cache.
        
        This creates a sequential scan pattern typical of transformer
        attention, where each new token attends to all previous tokens
        in the context.
        
        Args:
            layer_id: Which transformer layer (affects base address).
            read_only: If True, only generate READ operations.
        
        Returns:
            List of (operation, address) tuples.
            Operations are "READ" or "WRITE".
        
        Example:
            >>> gen = TraceGenerator()
            >>> trace = gen.generate_attention_trace(layer_id=0)
            >>> trace[0]
            ('READ', 16777216)
        """
        trace = []
        
        # Calculate layer offset
        layer_offset = layer_id * self.config.hidden_dim * 2  # K and V
        
        # Sequential scan through context
        for token_idx in range(self.config.context_length):
            # Calculate address for this token's KV pair
            token_offset = token_idx * self.config.hidden_dim * 2
            byte_offset = (layer_offset + token_offset) * self.bytes_per_element
            
            # Align to cache line boundary
            cache_line_id = int(byte_offset // self.config.cache_line_size)
            addr = self.config.base_addr + (cache_line_id * self.config.cache_line_size)
            
            trace.append(("READ", addr))
        
        return trace
    
    def generate_prefill_trace(
        self,
        layer_id: int = 0
    ) -> List[Tuple[str, int]]:
        """Generate trace for prefill phase (initial context loading).
        
        During prefill, the KV-cache is populated with all context tokens.
        This creates a mix of WRITE operations followed by READ operations.
        
        Args:
            layer_id: Which transformer layer.
        
        Returns:
            List of (operation, address) tuples.
        """
        trace = []
        layer_offset = layer_id * self.config.hidden_dim * 2
        
        # Write phase: populate KV-cache
        for token_idx in range(self.config.context_length):
            token_offset = token_idx * self.config.hidden_dim * 2
            byte_offset = (layer_offset + token_offset) * self.bytes_per_element
            cache_line_id = int(byte_offset // self.config.cache_line_size)
            addr = self.config.base_addr + (cache_line_id * self.config.cache_line_size)
            
            trace.append(("WRITE", addr))
        
        # Read phase: attention over written tokens
        for token_idx in range(self.config.context_length):
            token_offset = token_idx * self.config.hidden_dim * 2
            byte_offset = (layer_offset + token_offset) * self.bytes_per_element
            cache_line_id = int(byte_offset // self.config.cache_line_size)
            addr = self.config.base_addr + (cache_line_id * self.config.cache_line_size)
            
            trace.append(("READ", addr))
        
        return trace
    
    def generate_random_trace(
        self,
        num_ops: int = 10000,
        read_prob: float = 0.7
    ) -> List[Tuple[str, int]]:
        """Generate random memory access trace.
        
        Useful for stress-testing and adversarial workloads.
        
        Args:
            num_ops: Number of memory operations.
            read_prob: Probability of READ vs WRITE (0.0 to 1.0).
        
        Returns:
            List of (operation, address) tuples.
        """
        trace = []
        max_addr = self.config.context_length * self.config.hidden_dim * 2
        max_cache_lines = int(max_addr * self.bytes_per_element / self.config.cache_line_size)
        
        for _ in range(num_ops):
            # Random operation type
            op = "READ" if np.random.random() < read_prob else "WRITE"
            
            # Random cache line
            cache_line_id = np.random.randint(0, max_cache_lines)
            addr = self.config.base_addr + (cache_line_id * self.config.cache_line_size)
            
            trace.append((op, addr))
        
        return trace
    
    def generate_strided_trace(
        self,
        stride: int = 1,
        num_passes: int = 1
    ) -> List[Tuple[str, int]]:
        """Generate strided access pattern.
        
        Tests prefetcher with non-sequential patterns.
        
        Args:
            stride: Stride in cache lines.
            num_passes: Number of passes through memory.
        
        Returns:
            List of (operation, address) tuples.
        """
        trace = []
        max_addr = self.config.context_length * self.config.hidden_dim * 2
        max_cache_lines = int(max_addr * self.bytes_per_element / self.config.cache_line_size)
        
        for _ in range(num_passes):
            for line_id in range(0, max_cache_lines, stride):
                addr = self.config.base_addr + (line_id * self.config.cache_line_size)
                trace.append(("READ", addr))
        
        return trace


def generate_llm_trace(
    context_length: int = 2048,
    hidden_dim: int = 4096,
    precision: str = "INT4"
) -> List[Tuple[str, int]]:
    """Convenience function to generate standard LLM inference trace.
    
    This is a simple wrapper around TraceGenerator for quick usage.
    
    Args:
        context_length: Number of tokens in context.
        hidden_dim: Hidden dimension size.
        precision: Data precision ('FP32', 'FP16', 'INT8', 'INT4').
    
    Returns:
        List of (operation, address) tuples representing attention trace.
    
    Example:
        >>> trace = generate_llm_trace(context_length=2048)
        >>> len(trace)
        2048
    """
    config = TraceConfig(
        context_length=context_length,
        hidden_dim=hidden_dim,
        precision=precision
    )
    generator = TraceGenerator(config)
    return generator.generate_attention_trace()


if __name__ == "__main__":
    # Example usage
    print("Generating LLM inference trace...")
    
    # Standard attention trace
    trace = generate_llm_trace(context_length=2048, hidden_dim=4096)
    print(f"Generated {len(trace)} operations")
    print(f"First 5 operations: {trace[:5]}")
    
    # Advanced usage with custom configuration
    config = TraceConfig(
        context_length=4096,
        hidden_dim=8192,
        precision="INT8"
    )
    generator = TraceGenerator(config)
    
    # Different trace types
    attention_trace = generator.generate_attention_trace()
    prefill_trace = generator.generate_prefill_trace()
    random_trace = generator.generate_random_trace(num_ops=5000)
    strided_trace = generator.generate_strided_trace(stride=4)
    
    print(f"\nAttention trace: {len(attention_trace)} ops")
    print(f"Prefill trace: {len(prefill_trace)} ops")
    print(f"Random trace: {len(random_trace)} ops")
    print(f"Strided trace: {len(strided_trace)} ops")
