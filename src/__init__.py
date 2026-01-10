"""Janus-1: Real-Time Generative AI Acceleration at the Edge

A novel processor architecture enabling real-time execution of 7-billion-parameter
language models within a sub-5-watt power envelope on edge devices.

Modules:
    simulator: Cycle-accurate memory hierarchy simulator
    models: Power, area, and performance models
    benchmarks: Trace generation and validation tools

Example:
    >>> from src.simulator.janus_sim import JanusSim
    >>> from src.benchmarks.trace_generator import generate_llm_trace
    >>> 
    >>> trace = generate_llm_trace(context_length=2048)
    >>> sim = JanusSim()
    >>> sim.run(trace)
    >>> sim.report()

For more information:
    - Repository: https://github.com/ChessEngineUS/Janus-1
    - Colab Notebook: https://colab.research.google.com/github/ChessEngineUS/Janus-1/blob/main/Janus_1_Complete_Analysis.ipynb
    - Documentation: https://github.com/ChessEngineUS/Janus-1/tree/main/docs

Author: Tommaso Marena
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Tommaso Marena"
__email__ = "112788717+ChessEngineUS@users.noreply.github.com"
__license__ = "MIT"
__url__ = "https://github.com/ChessEngineUS/Janus-1"

# Key performance metrics
__metrics__ = {
    "compute_tops": 8.2,
    "power_watts": 4.05,
    "area_mm2": 79,
    "cache_hit_rate_percent": 99.99,
    "memory_efficiency_mb_per_watt": 63,
    "p99_latency_cycles": 1.0,
    "process_node_nm": 3,
}

# Import key classes for convenience
from src.simulator.janus_sim import JanusSim, SimulationConfig, SimulationMetrics
from src.models.kv_cache_sizing import KVCacheSizer, ModelConfig
from src.models.memory_power_model import MemoryPowerModel
from src.benchmarks.trace_generator import generate_llm_trace

__all__ = [
    "JanusSim",
    "SimulationConfig",
    "SimulationMetrics",
    "KVCacheSizer",
    "ModelConfig",
    "MemoryPowerModel",
    "generate_llm_trace",
]


def get_version() -> str:
    """Get Janus-1 version string.
    
    Returns:
        Version string in semantic versioning format
    """
    return __version__


def get_metrics() -> dict:
    """Get key performance metrics.
    
    Returns:
        Dictionary containing major performance metrics
    """
    return __metrics__.copy()


def print_info():
    """Print Janus-1 project information."""
    separator = '=' * 70
    print(f"\n{separator}")
    print("Janus-1: Real-Time Generative AI Acceleration at the Edge")
    print(separator)
    print(f"Version: {__version__}")
    print(f"Author: {__author__}")
    print(f"License: {__license__}")
    print("\nKey Performance Metrics:")
    print(f"  Compute: {__metrics__['compute_tops']} TOPS")
    print(f"  Power: {__metrics__['power_watts']} W")
    print(f"  Area: {__metrics__['area_mm2']} mm²")
    print(f"  Cache Hit Rate: {__metrics__['cache_hit_rate_percent']}%")
    print(f"  Memory Efficiency: {__metrics__['memory_efficiency_mb_per_watt']} MB/W")
    print(f"  P99 Latency: {__metrics__['p99_latency_cycles']} cycle")
    print(f"\nProcess: {__metrics__['process_node_nm']}nm GAA")
    print(f"\nRepository: {__url__}")
    print(f"{separator}\n")
