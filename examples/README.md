# Janus-1 Examples

This directory contains practical examples and tutorials for using Janus-1.

## Quick Start Examples

### Basic Usage
- **[01_basic_simulation.py](01_basic_simulation.py)** - Run your first memory hierarchy simulation
- **[02_kv_cache_analysis.py](02_kv_cache_analysis.py)** - Calculate KV-cache requirements for different models
- **[03_power_analysis.py](03_power_analysis.py)** - Analyze power consumption across memory technologies

### Advanced Examples
- **[04_prefetcher_tuning.py](04_prefetcher_tuning.py)** - Optimize prefetcher parameters for your workload
- **[05_custom_workload.py](05_custom_workload.py)** - Create and simulate custom LLM inference patterns
- **[06_thermal_modeling.py](06_thermal_modeling.py)** - Model junction temperature and thermal management

### Integration Examples
- **[07_llama_integration.py](07_llama_integration.py)** - Integrate with Llama models
- **[08_batch_analysis.py](08_batch_analysis.py)** - Run parameter sweeps and batch experiments
- **[09_visualization.py](09_visualization.py)** - Generate publication-quality plots

## Running Examples

Each example is self-contained and can be run directly:

```bash
python examples/01_basic_simulation.py
```

Or explore interactively:

```bash
python -i examples/01_basic_simulation.py
```

## Expected Output

Each example includes expected output in comments. Results should match within ±2% due to floating-point precision.

## Dependencies

All examples use the main Janus-1 dependencies. Install with:

```bash
pip install -r requirements.txt
```

Some advanced examples may require additional packages listed in their docstrings.
