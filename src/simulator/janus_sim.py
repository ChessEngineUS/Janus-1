"""Janus-Sim: Cycle-Accurate Memory Hierarchy Simulator

This module implements the core simulation engine for the Janus-1 memory hierarchy.
It models the two-tier SRAM+eDRAM system with the Janus-Prefetch-1 engine.

Author: The Janus-1 Design Team
License: MIT
"""

import collections
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """Configuration parameters for Janus-Sim."""
    t1_sram_size_mb: int = 32
    t1_sram_banks: int = 4
    t2_edram_banks: int = 14
    cache_line_size_bytes: int = 128
    t1_latency_cycles: int = 1
    t2_latency_cycles: int = 3
    bank_conflict_penalty_cycles: int = 5
    prefetch_issue_width: int = 4
    prefetch_look_ahead: int = 16


@dataclass
class SimulationMetrics:
    """Performance metrics from simulation run."""
    t1_hits: int
    t1_misses: int
    total_cycles: int
    read_latencies: List[int]
    prefetch_bandwidth: int
    compute_bandwidth: int
    
    @property
    def hit_rate(self) -> float:
        """Calculate T1 cache hit rate."""
        total = self.t1_hits + self.t1_misses
        return (self.t1_hits / total * 100) if total > 0 else 0.0
    
    @property
    def p50_latency(self) -> float:
        """Calculate P50 (median) latency."""
        return np.percentile(self.read_latencies, 50) if self.read_latencies else 0.0
    
    @property
    def p90_latency(self) -> float:
        """Calculate P90 latency."""
        return np.percentile(self.read_latencies, 90) if self.read_latencies else 0.0
    
    @property
    def p99_latency(self) -> float:
        """Calculate P99 latency."""
        return np.percentile(self.read_latencies, 99) if self.read_latencies else 0.0


class JanusSim:
    """Cycle-accurate simulator for Janus-1 memory hierarchy.
    
    This simulator models:
    - 32 MB SRAM Tier-1 active cache (4 banks)
    - 224 MB eDRAM Tier-2 main store (14 banks)
    - Janus-Prefetch-1 FSM-based stream prefetcher
    - Bank conflicts and queuing delays
    
    Example:
        >>> sim = JanusSim()
        >>> trace = [("READ", 0x1000), ("READ", 0x1080), ...]
        >>> sim.run(trace)
        >>> sim.report()
        T1 Hit Rate: 99.99% (65520 hits / 65536 reads)
        Latencies (cycles): P50=1.0, P90=1.0, P99=1.0
    """
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        """Initialize simulator with configuration.
        
        Args:
            config: Simulation configuration. Uses defaults if None.
        """
        self.config = config or SimulationConfig()
        self._init_memory_hierarchy()
        self._init_prefetcher()
        self._init_metrics()
    
    def _init_memory_hierarchy(self):
        """Initialize memory hierarchy state."""
        # T1 SRAM cache (LRU replacement)
        self.t1_sram_size_bytes = self.config.t1_sram_size_mb * 1024 * 1024
        self.t1_max_lines = self.t1_sram_size_bytes // self.config.cache_line_size_bytes
        self.t1_cache = collections.OrderedDict()
        
        # Bank busy tracking
        self.t1_bank_busy_until = [0] * self.config.t1_sram_banks
        self.t2_bank_busy_until = [0] * self.config.t2_edram_banks
        
        # Event queue for T2 responses
        self.pending_events = []
        self.pending_cpu_read = None
        self.pending_cpu_read_start_cycle = None
        
        # Prefetch tracking
        self.inflight_prefetches = set()
    
    def _init_prefetcher(self):
        """Initialize prefetcher FSM state."""
        self.prefetch_stream_addr = -1
        self.prefetch_stream_detected = False
    
    def _init_metrics(self):
        """Initialize performance metrics."""
        self.cycle = 0
        self.t1_hits = 0
        self.t1_misses = 0
        self.read_latencies = []
        self.prefetch_bw_count = 0
        self.compute_bw_count = 0
    
    def get_t1_bank(self, addr: int) -> int:
        """Calculate T1 SRAM bank ID for address."""
        line_num = addr // self.config.cache_line_size_bytes
        return line_num % self.config.t1_sram_banks
    
    def get_t2_bank(self, addr: int) -> int:
        """Calculate T2 eDRAM bank ID for address."""
        line_num = addr // self.config.cache_line_size_bytes
        return line_num % self.config.t2_edram_banks
    
    def run(self, trace: List[Tuple[str, int]]):
        """Run simulation on memory access trace.
        
        Args:
            trace: List of (operation, address) tuples.
                  Operations: "READ" or "WRITE"
        """
        trace_iterator = iter(trace)
        current_trace_entry = next(trace_iterator, None)
        
        while current_trace_entry or self.pending_cpu_read or self.pending_events:
            self._process_pending_events()
            self._process_pending_read(trace_iterator)
            
            if not self.pending_cpu_read and current_trace_entry:
                current_trace_entry = self._process_trace_entry(
                    current_trace_entry, trace_iterator
                )
            
            if self.prefetch_stream_detected:
                self._issue_prefetches()
            
            self.cycle += 1
    
    def _process_pending_events(self):
        """Process T2 responses arriving this cycle."""
        arrivals = []
        for addr, arrival_time, is_prefetch in self.pending_events:
            if self.cycle >= arrival_time:
                arrivals.append((addr, is_prefetch))
        
        for addr, is_prefetch in arrivals:
            self.inflight_prefetches.discard(addr)
            
            # Insert into T1 cache with LRU eviction
            if len(self.t1_cache) >= self.t1_max_lines:
                self.t1_cache.popitem(last=False)
            self.t1_cache[addr] = True
            
            # Remove from event queue
            self.pending_events = [
                ev for ev in self.pending_events if ev[0] != addr
            ]
    
    def _process_pending_read(self, trace_iterator):
        """Complete pending CPU read if data now in T1."""
        if not self.pending_cpu_read:
            return
        
        addr = self.pending_cpu_read
        if addr in self.t1_cache:
            bank_id = self.get_t1_bank(addr)
            service_time = max(
                self.cycle, 
                self.t1_bank_busy_until[bank_id]
            ) + self.config.t1_latency_cycles
            
            latency = service_time - self.pending_cpu_read_start_cycle
            self.read_latencies.append(latency)
            
            self.t1_bank_busy_until[bank_id] = service_time
            self.t1_cache.move_to_end(addr)
            self.pending_cpu_read = None
    
    def _process_trace_entry(
        self, 
        entry: Tuple[str, int], 
        trace_iterator
    ) -> Optional[Tuple[str, int]]:
        """Process a single trace entry.
        
        Returns:
            Next trace entry to process, or None if entry is pending.
        """
        op, addr = entry
        
        if op == "READ":
            self.compute_bw_count += 1
            
            if addr in self.t1_cache:
                # T1 hit
                self.t1_hits += 1
                bank_id = self.get_t1_bank(addr)
                service_time = max(
                    self.cycle, 
                    self.t1_bank_busy_until[bank_id]
                ) + self.config.t1_latency_cycles
                
                self.read_latencies.append(service_time - self.cycle)
                self.t1_bank_busy_until[bank_id] = service_time
                self.t1_cache.move_to_end(addr)
                
                next_entry = next(trace_iterator, None)
            else:
                # T1 miss - fetch from T2
                self.t1_misses += 1
                self.pending_cpu_read = addr
                self.pending_cpu_read_start_cycle = self.cycle
                self.issue_to_t2(addr, is_prefetch=False)
                next_entry = entry  # Keep current entry
            
            # Update prefetcher state
            if self.prefetch_stream_addr + self.config.cache_line_size_bytes == addr:
                self.prefetch_stream_detected = True
            else:
                self.prefetch_stream_detected = False
            self.prefetch_stream_addr = addr
        
        elif op == "WRITE":
            # Write allocates in T1
            if addr not in self.t1_cache:
                if len(self.t1_cache) >= self.t1_max_lines:
                    self.t1_cache.popitem(last=False)
                self.t1_cache[addr] = True
            next_entry = next(trace_iterator, None)
        
        else:
            raise ValueError(f"Unknown operation: {op}")
        
        return next_entry
    
    def _issue_prefetches(self):
        """Issue prefetches based on detected stream."""
        issued = 0
        for i in range(1, self.config.prefetch_look_ahead + 1):
            if issued >= self.config.prefetch_issue_width:
                break
            
            pf_addr = (
                self.prefetch_stream_addr + 
                i * self.config.cache_line_size_bytes
            )
            
            if (pf_addr not in self.t1_cache and 
                pf_addr not in self.inflight_prefetches):
                self.issue_to_t2(pf_addr, is_prefetch=True)
                self.inflight_prefetches.add(pf_addr)
                issued += 1
    
    def issue_to_t2(self, addr: int, is_prefetch: bool):
        """Issue request to T2 eDRAM.
        
        Args:
            addr: Address to fetch
            is_prefetch: True if this is a prefetch, False if demand
        """
        if is_prefetch:
            self.prefetch_bw_count += 1
        else:
            self.compute_bw_count += 1
        
        bank_id = self.get_t2_bank(addr)
        
        # Calculate arrival time accounting for bank conflicts
        base_arrival = max(
            self.cycle, 
            self.t2_bank_busy_until[bank_id]
        ) + self.config.t2_latency_cycles
        
        # Add conflict penalty if bank is busy
        if base_arrival > self.cycle + self.config.t2_latency_cycles:
            base_arrival += self.config.bank_conflict_penalty_cycles
        
        self.t2_bank_busy_until[bank_id] = base_arrival
        self.pending_events.append((addr, base_arrival, is_prefetch))
    
    def get_metrics(self) -> SimulationMetrics:
        """Return simulation metrics."""
        return SimulationMetrics(
            t1_hits=self.t1_hits,
            t1_misses=self.t1_misses,
            total_cycles=self.cycle,
            read_latencies=self.read_latencies,
            prefetch_bandwidth=self.prefetch_bw_count,
            compute_bandwidth=self.compute_bw_count
        )
    
    def report(self):
        """Print formatted simulation results."""
        metrics = self.get_metrics()
        total_reads = metrics.t1_hits + metrics.t1_misses
        
        print(f"\n{'='*60}")
        print("Janus-1 Memory Hierarchy Simulation Results")
        print(f"{'='*60}")
        print(f"\nCache Performance:")
        print(f"  T1 Hit Rate: {metrics.hit_rate:.2f}% "
              f"({metrics.t1_hits} hits / {total_reads} reads)")
        print(f"\nLatency Distribution (cycles):")
        print(f"  P50: {metrics.p50_latency:.1f}")
        print(f"  P90: {metrics.p90_latency:.1f}")
        print(f"  P99: {metrics.p99_latency:.1f}")
        print(f"\nBandwidth Utilization:")
        print(f"  Compute BW: {metrics.compute_bandwidth} accesses")
        print(f"  Prefetch BW: {metrics.prefetch_bandwidth} accesses")
        print(f"  Total Cycles: {metrics.total_cycles}")
        print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # Example usage
    from src.benchmarks.trace_generator import generate_llm_trace
    
    print("Generating LLM inference trace...")
    trace = generate_llm_trace(context_length=2048, hidden_dim=4096)
    
    print(f"Running simulation on {len(trace)} memory operations...")
    sim = JanusSim()
    sim.run(trace)
    sim.report()
