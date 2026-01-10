# Janus-1 Code Examples

This document provides comprehensive code examples for using Janus-1 components.

## Table of Contents

- [Quick Start](#quick-start)
- [Memory Hierarchy Simulation](#memory-hierarchy-simulation)
- [KV-Cache Analysis](#kv-cache-analysis)
- [Memory Technology Comparison](#memory-technology-comparison)
- [Prefetcher Optimization](#prefetcher-optimization)
- [Thermal Analysis](#thermal-analysis)
- [Custom Configurations](#custom-configurations)
- [Advanced Usage](#advanced-usage)

---

## Quick Start

### Minimal Example

```python
from src.simulator.janus_sim import JanusSim
from src.benchmarks.trace_generator import generate_llm_trace

# Generate trace and run simulation
trace = generate_llm_trace(context_length=2048)
sim = JanusSim()
sim.run(trace)
sim.report()
```

**Output**:
```
T1 Hit Rate: 99.99% (65520 hits / 65536 reads)
Latencies (cycles): P50=1.0, P90=1.0, P99=1.0
```

---

## Memory Hierarchy Simulation

### Basic Simulation

```python
from src.simulator.janus_sim import JanusSim, SimulationConfig
from src.benchmarks.trace_generator import generate_llm_trace

# Configure simulator
config = SimulationConfig(
    t1_sram_size_mb=32,
    t2_edram_banks=14,
    cache_line_size_bytes=128,
    prefetch_look_ahead=16
)

# Generate workload
trace = generate_llm_trace(
    context_length=4096,
    hidden_dim=4096,
    num_layers=32
)

# Run simulation
sim = JanusSim(config)
sim.run(trace)

# Get metrics
metrics = sim.get_metrics()

print(f"Hit Rate: {metrics.hit_rate:.4f}%")
print(f"P99 Latency: {metrics.p99_latency:.2f} cycles")
print(f"Total Cycles: {metrics.total_cycles}")
print(f"Prefetch BW: {metrics.prefetch_bandwidth}")
```

### Custom Memory Trace

```python
import numpy as np
from src.simulator.janus_sim import JanusSim

# Create custom access pattern
def generate_custom_trace(num_accesses=10000):
    """Generate trace with specific access pattern."""
    trace = []
    base_addr = 0x1000000
    cache_line = 128
    
    # Phase 1: Sequential access (streaming)
    for i in range(num_accesses // 2):
        addr = base_addr + i * cache_line
        trace.append(("READ", addr))
    
    # Phase 2: Random access (scattered)
    for i in range(num_accesses // 2):
        offset = np.random.randint(0, 1000) * cache_line
        addr = base_addr + offset
        trace.append(("READ", addr))
    
    return trace

# Run with custom trace
trace = generate_custom_trace()
sim = JanusSim()
sim.run(trace)
sim.report()
```

### Analyzing Latency Distribution

```python
import matplotlib.pyplot as plt
import numpy as np
from src.simulator.janus_sim import JanusSim
from src.benchmarks.trace_generator import generate_llm_trace

# Run simulation
trace = generate_llm_trace(context_length=2048)
sim = JanusSim()
sim.run(trace)
metrics = sim.get_metrics()

# Plot latency distribution
latencies = metrics.read_latencies

plt.figure(figsize=(10, 6))
plt.hist(latencies, bins=50, edgecolor='black', alpha=0.7)
plt.xlabel('Latency (cycles)')
plt.ylabel('Frequency')
plt.title('Read Latency Distribution')
plt.axvline(np.percentile(latencies, 99), 
            color='r', linestyle='--', 
            label=f'P99: {np.percentile(latencies, 99):.1f}')
plt.legend()
plt.grid(alpha=0.3)
plt.show()

print(f"Mean: {np.mean(latencies):.2f} cycles")
print(f"Std Dev: {np.std(latencies):.2f} cycles")
print(f"Min: {np.min(latencies)} cycles")
print(f"Max: {np.max(latencies)} cycles")
```

---

## KV-Cache Analysis

### Calculate Cache Requirements

```python
from src.models.kv_cache_sizing import KVCacheSizer, ModelConfig
import pandas as pd

# Configure model
config = ModelConfig(
    num_layers=32,
    hidden_dim=4096,
    num_heads=32,
    head_dim=128,
    context_length=4096
)

# Calculate for all precisions
sizer = KVCacheSizer(config)
results = sizer.calculate_all_precisions()

# Convert to DataFrame for analysis
df = pd.DataFrame([
    {
        'Precision': k,
        'Size (MB)': v['size_mb'],
        'Size (GB)': v['size_gb'],
        'Bytes/Token': v['bytes_per_token']
    }
    for k, v in results.items()
])

print(df.to_string(index=False))

# Calculate reduction
fp16_size = results['FP16']['size_mb']
int4_size = results['INT4']['size_mb']
reduction = fp16_size / int4_size
print(f"\nINT4 reduction: {reduction:.1f}x ({fp16_size - int4_size:.0f} MB saved)")
```

### Custom Model Analysis

```python
from src.models.kv_cache_sizing import KVCacheSizer, ModelConfig

# Analyze different model sizes
models = {
    'Llama-2 7B': ModelConfig(num_layers=32, hidden_dim=4096),
    'Llama-2 13B': ModelConfig(num_layers=40, hidden_dim=5120),
    'Llama-2 70B': ModelConfig(num_layers=80, hidden_dim=8192),
}

for name, config in models.items():
    sizer = KVCacheSizer(config)
    int4_result = sizer.calculate('INT4')
    int8_result = sizer.calculate('INT8')
    
    print(f"\n{name}:")
    print(f"  INT8: {int8_result['size_mb']:.0f} MB")
    print(f"  INT4: {int4_result['size_mb']:.0f} MB")
    print(f"  On-chip feasible: {int4_result['size_mb'] < 256}")
```

---

## Memory Technology Comparison

### Basic Power/Area Analysis

```python
from src.models.memory_power_model import MemoryPowerModel

# Compare technologies for T2 cache
cache_size = 224  # MB
bandwidth = 20    # GB/s

technologies = ['HD_SRAM', 'eDRAM', 'STT_MRAM']
results = []

for tech in technologies:
    model = MemoryPowerModel(
        cache_size_mb=cache_size,
        bandwidth_gb_s=bandwidth,
        technology=tech
    )
    power = model.estimate_power()
    results.append(power)
    
    print(f"\n{tech}:")
    print(f"  Dynamic: {power['dynamic_w']:.3f} W")
    print(f"  Static: {power['static_w']:.3f} W")
    print(f"  Total: {power['total_w']:.3f} W")
    print(f"  Efficiency: {cache_size / power['total_w']:.1f} MB/W")

# Find optimal
best = min(results, key=lambda x: x['total_w'])
print(f"\n✓ Optimal: {best['technology']} ({best['total_w']:.2f} W)")
```

### Parameter Sweep

```python
import matplotlib.pyplot as plt
import numpy as np
from src.models.memory_power_model import MemoryPowerModel

# Sweep cache sizes
sizes = np.array([32, 64, 128, 224, 256, 512])
technologies = ['HD_SRAM', 'eDRAM', 'STT_MRAM']

plt.figure(figsize=(12, 5))

# Plot total power vs size
plt.subplot(1, 2, 1)
for tech in technologies:
    powers = []
    for size in sizes:
        model = MemoryPowerModel(size, 20, tech)
        power = model.estimate_power()
        powers.append(power['total_w'])
    plt.plot(sizes, powers, marker='o', label=tech, linewidth=2)

plt.xlabel('Cache Size (MB)')
plt.ylabel('Total Power (W)')
plt.title('Power Scaling by Technology')
plt.legend()
plt.grid(alpha=0.3)
plt.yscale('log')

# Plot efficiency
plt.subplot(1, 2, 2)
for tech in technologies:
    efficiencies = []
    for size in sizes:
        model = MemoryPowerModel(size, 20, tech)
        power = model.estimate_power()
        efficiencies.append(size / power['total_w'])
    plt.plot(sizes, efficiencies, marker='s', label=tech, linewidth=2)

plt.xlabel('Cache Size (MB)')
plt.ylabel('Efficiency (MB/W)')
plt.title('Memory Efficiency by Technology')
plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()
```

---

## Prefetcher Optimization

### Lookahead Depth Sweep

```python
import matplotlib.pyplot as plt
from src.simulator.janus_sim import JanusSim, SimulationConfig
from src.benchmarks.trace_generator import generate_llm_trace

# Generate test trace
trace = generate_llm_trace(context_length=2048)

# Sweep lookahead values
lookahead_values = [2, 4, 8, 16, 32, 64, 128]
results = []

for lookahead in lookahead_values:
    config = SimulationConfig(prefetch_look_ahead=lookahead)
    sim = JanusSim(config)
    sim.run(trace)
    metrics = sim.get_metrics()
    
    results.append({
        'lookahead': lookahead,
        'hit_rate': metrics.hit_rate,
        'p99_latency': metrics.p99_latency,
        'prefetch_bw': metrics.prefetch_bandwidth
    })
    
    print(f"Lookahead={lookahead:3d}: "
          f"Hit={metrics.hit_rate:6.2f}%, "
          f"P99={metrics.p99_latency:4.1f} cyc, "
          f"PF_BW={metrics.prefetch_bandwidth}")

# Plot results
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot([r['lookahead'] for r in results],
         [r['hit_rate'] for r in results],
         'o-', linewidth=2, markersize=8)
ax1.set_xlabel('Prefetch Lookahead Depth')
ax1.set_ylabel('Hit Rate (%)')
ax1.set_title('Cache Hit Rate vs Lookahead')
ax1.grid(alpha=0.3)
ax1.set_xscale('log', base=2)

ax2.plot([r['lookahead'] for r in results],
         [r['prefetch_bw'] for r in results],
         's-', linewidth=2, markersize=8, color='orange')
ax2.set_xlabel('Prefetch Lookahead Depth')
ax2.set_ylabel('Prefetch Bandwidth (accesses)')
ax2.set_title('Prefetch Overhead vs Lookahead')
ax2.grid(alpha=0.3)
ax2.set_xscale('log', base=2)

plt.tight_layout()
plt.show()

# Find optimal
optimal = max(results, key=lambda x: x['hit_rate'])
print(f"\n✓ Optimal lookahead: {optimal['lookahead']}")
print(f"  Hit rate: {optimal['hit_rate']:.2f}%")
print(f"  P99 latency: {optimal['p99_latency']:.1f} cycles")
```

---

## Thermal Analysis

### Junction Temperature Calculation

```python
from src.models.thermal_analysis import ThermalAnalyzer
import numpy as np
import matplotlib.pyplot as plt

# Create thermal model
thermal = ThermalAnalyzer(
    power_w=4.05,
    ambient_c=25.0,
    theta_ja_c_per_w=15.0  # Junction-to-ambient thermal resistance
)

# Calculate junction temperature
result = thermal.calculate_junction_temp(package='enhanced')

print(f"Thermal Analysis:")
print(f"  Power: {result['power_w']:.2f} W")
print(f"  Ambient: {result['ambient_temp_c']:.1f} °C")
print(f"  Junction: {result['junction_temp_c']:.1f} °C")
print(f"  Margin: {result['thermal_margin_c']:.1f} °C")
print(f"  Within Spec: {result['within_spec']}")

# Thermal sweep
power_range = np.linspace(1, 10, 50)
ambients = [25, 45, 65]  # Room, warm, hot

plt.figure(figsize=(10, 6))

for amb in ambients:
    temps = []
    for power in power_range:
        t = ThermalAnalyzer(power, amb)
        result = t.calculate_junction_temp()
        temps.append(result['junction_temp_c'])
    
    plt.plot(power_range, temps, linewidth=2, 
             label=f'Ambient={amb}°C')

plt.axhline(y=85, color='orange', linestyle='--', 
            linewidth=2, label='Industrial Limit (85°C)')
plt.axhline(y=125, color='red', linestyle='--', 
            linewidth=2, label='Max Spec (125°C)')
plt.xlabel('Power Dissipation (W)')
plt.ylabel('Junction Temperature (°C)')
plt.title('Thermal Operating Range')
plt.legend()
plt.grid(alpha=0.3)
plt.xlim(1, 10)
plt.ylim(20, 130)
plt.show()
```

---

## Custom Configurations

### Multi-Configuration Comparison

```python
from src.simulator.janus_sim import JanusSim, SimulationConfig
from src.benchmarks.trace_generator import generate_llm_trace
import pandas as pd

# Define configurations to compare
configs = {
    'Baseline': SimulationConfig(),
    'Large T1': SimulationConfig(t1_sram_size_mb=64),
    'More Banks': SimulationConfig(t1_sram_banks=8),
    'Aggressive PF': SimulationConfig(prefetch_look_ahead=32),
    'Conservative PF': SimulationConfig(prefetch_look_ahead=8),
}

# Run all configurations
trace = generate_llm_trace(context_length=2048)
results = []

for name, config in configs.items():
    sim = JanusSim(config)
    sim.run(trace)
    metrics = sim.get_metrics()
    
    results.append({
        'Configuration': name,
        'Hit Rate (%)': metrics.hit_rate,
        'P50 Latency': metrics.p50_latency,
        'P99 Latency': metrics.p99_latency,
        'Total Cycles': metrics.total_cycles,
        'Prefetch BW': metrics.prefetch_bandwidth
    })

df = pd.DataFrame(results)
print(df.to_string(index=False))

# Find best configuration
best_hit_rate = df.loc[df['Hit Rate (%)'].idxmax()]
print(f"\n✓ Best hit rate: {best_hit_rate['Configuration']}")
print(f"  {best_hit_rate['Hit Rate (%)']:.2f}%")
```

---

## Advanced Usage

### Custom Prefetcher Algorithm

```python
from src.simulator.janus_sim import JanusSim
import collections

class CustomPrefetcher(JanusSim):
    """Custom prefetcher with stride detection."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stride_history = collections.deque(maxlen=4)
        self.detected_stride = 0
    
    def _process_trace_entry(self, entry, trace_iterator):
        """Override to add stride detection."""
        op, addr = entry
        
        if op == "READ" and self.prefetch_stream_addr >= 0:
            stride = addr - self.prefetch_stream_addr
            self.stride_history.append(stride)
            
            # Detect consistent stride
            if len(self.stride_history) == 4:
                if len(set(self.stride_history)) == 1:
                    self.detected_stride = stride
                    self.prefetch_stream_detected = True
                else:
                    self.prefetch_stream_detected = False
        
        return super()._process_trace_entry(entry, trace_iterator)
    
    def _issue_prefetches(self):
        """Issue prefetches using detected stride."""
        if self.detected_stride == 0:
            return super()._issue_prefetches()
        
        issued = 0
        for i in range(1, self.config.prefetch_look_ahead + 1):
            if issued >= self.config.prefetch_issue_width:
                break
            
            pf_addr = self.prefetch_stream_addr + i * self.detected_stride
            
            if (pf_addr not in self.t1_cache and 
                pf_addr not in self.inflight_prefetches):
                self.issue_to_t2(pf_addr, is_prefetch=True)
                self.inflight_prefetches.add(pf_addr)
                issued += 1

# Use custom prefetcher
from src.benchmarks.trace_generator import generate_llm_trace

trace = generate_llm_trace()
sim = CustomPrefetcher()
sim.run(trace)
sim.report()
```

### Batch Simulation with Parallel Processing

```python
from concurrent.futures import ProcessPoolExecutor
from src.simulator.janus_sim import JanusSim, SimulationConfig
from src.benchmarks.trace_generator import generate_llm_trace
import pandas as pd

def run_simulation(config_dict):
    """Run single simulation (for parallel execution)."""
    config = SimulationConfig(**config_dict['params'])
    trace = generate_llm_trace(context_length=2048)
    
    sim = JanusSim(config)
    sim.run(trace)
    metrics = sim.get_metrics()
    
    return {
        'name': config_dict['name'],
        'hit_rate': metrics.hit_rate,
        'p99_latency': metrics.p99_latency,
        'total_cycles': metrics.total_cycles
    }

# Define parameter sweep
configurations = [
    {'name': f'LA={la}', 'params': {'prefetch_look_ahead': la}}
    for la in [4, 8, 16, 32, 64]
]

# Run in parallel
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(run_simulation, configurations))

# Analyze results
df = pd.DataFrame(results)
print(df.to_string(index=False))
```

---

## More Examples

For more examples, see:

- [Colab Notebook](../Janus_1_Complete_Analysis.ipynb) - Complete analysis pipeline
- [experiments/](../experiments/) - Full system evaluations
- [tests/](../tests/) - Unit test examples

---

**Questions?** Open an issue on [GitHub](https://github.com/ChessEngineUS/Janus-1/issues)!