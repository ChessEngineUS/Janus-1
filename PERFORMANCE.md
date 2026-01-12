# Performance Benchmarking Guide

This guide provides comprehensive instructions for benchmarking Janus-1's performance across different quantum simulation backends and optimization strategies.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Benchmark Suite](#benchmark-suite)
- [Performance Metrics](#performance-metrics)
- [Hardware Requirements](#hardware-requirements)
- [Optimization Strategies](#optimization-strategies)
- [Results Interpretation](#results-interpretation)
- [Reproducibility](#reproducibility)

## Overview

Janus-1 is designed for efficient quantum-classical hybrid simulation of protein folding dynamics. Performance varies significantly based on:

- System size (number of qubits)
- Circuit depth and complexity
- Backend selection (statevector, MPS, GPU)
- Optimization algorithm
- Hardware specifications

## Quick Start

Run the complete benchmark suite:

```bash
python examples/02_kv_cache_analysis.py --benchmark
```

Run specific benchmarks:

```bash
# Circuit compilation performance
python -m pytest tests/test_performance.py::test_circuit_compilation_speed -v

# Variational optimization
python -m pytest tests/test_performance.py::test_vqe_convergence_speed -v

# Memory profiling
python scripts/profile_memory.py
```

## Benchmark Suite

### 1. Circuit Construction

**What it measures**: Time to construct quantum circuits of varying complexity

```python
from janus1.trace import TraceGenerator
import time

for n_qubits in [4, 8, 12, 16, 20]:
    start = time.perf_counter()
    generator = TraceGenerator(n_qubits=n_qubits)
    circuit = generator.generate_circuit()
    elapsed = time.perf_counter() - start
    print(f"{n_qubits} qubits: {elapsed:.4f}s")
```

**Expected results**:
- 4 qubits: ~0.01s
- 8 qubits: ~0.03s
- 12 qubits: ~0.08s
- 16 qubits: ~0.15s
- 20 qubits: ~0.30s

### 2. Circuit Execution

**What it measures**: Time to execute circuits on different backends

```python
from qiskit_aer import AerSimulator
from qiskit import transpile

backends = {
    'statevector': AerSimulator(method='statevector'),
    'density_matrix': AerSimulator(method='density_matrix'),
    'mps': AerSimulator(method='matrix_product_state'),
    'stabilizer': AerSimulator(method='stabilizer'),
}

for name, backend in backends.items():
    start = time.perf_counter()
    t_circuit = transpile(circuit, backend)
    job = backend.run(t_circuit, shots=1024)
    result = job.result()
    elapsed = time.perf_counter() - start
    print(f"{name}: {elapsed:.4f}s")
```

### 3. VQE Optimization

**What it measures**: Convergence speed and accuracy of variational optimization

```python
from janus1.optimization import VQEOptimizer

optimizer = VQEOptimizer(
    n_qubits=8,
    max_iterations=100,
    convergence_threshold=1e-6
)

result = optimizer.optimize()
print(f"Iterations: {result['iterations']}")
print(f"Final energy: {result['energy']:.6f}")
print(f"Time: {result['time']:.2f}s")
```

**Expected results** (8 qubits, COBYLA):
- Convergence: 40-60 iterations
- Time: 15-25 seconds
- Energy accuracy: ±1e-4

### 4. Memory Usage

**What it measures**: Peak memory consumption during simulation

```python
import tracemalloc

tracemalloc.start()
result = run_simulation(n_qubits=16)
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Peak memory: {peak / 1024**2:.2f} MB")
```

**Expected memory usage**:

| Qubits | Statevector | Density Matrix | MPS |
|--------|-------------|----------------|-----|
| 10 | 16 MB | 256 MB | 50 MB |
| 15 | 512 MB | 8 GB | 200 MB |
| 20 | 16 GB | 256 GB | 800 MB |
| 25 | 512 GB | OOM | 3 GB |

### 5. Parallel Scaling

**What it measures**: Speedup with multiple CPU cores/GPUs

```python
from joblib import Parallel, delayed

def run_trial(seed):
    return run_simulation(n_qubits=12, seed=seed)

for n_jobs in [1, 2, 4, 8]:
    start = time.perf_counter()
    results = Parallel(n_jobs=n_jobs)(delayed(run_trial)(i) for i in range(32))
    elapsed = time.perf_counter() - start
    speedup = (elapsed_1 / elapsed)
    print(f"{n_jobs} cores: {elapsed:.2f}s (speedup: {speedup:.2f}x)")
```

## Performance Metrics

### Primary Metrics

1. **Circuit Construction Time**: Time to build quantum circuits
2. **Execution Time**: Time to run circuits on simulator/hardware
3. **Optimization Convergence**: Iterations needed for VQE convergence
4. **Memory Usage**: Peak RAM consumption
5. **Fidelity**: Accuracy of simulated quantum states

### Derived Metrics

1. **Throughput**: Circuits executed per second
2. **Energy Efficiency**: Joules per circuit execution
3. **Scalability**: Performance vs. system size
4. **Cost Efficiency**: Compute cost per simulation

## Hardware Requirements

### Minimum Configuration

- **CPU**: 4 cores, 2.5 GHz
- **RAM**: 16 GB
- **Storage**: 10 GB free space
- **Python**: 3.9+

**Capabilities**: Up to 15 qubits with statevector, 20 qubits with MPS

### Recommended Configuration

- **CPU**: 16 cores, 3.5 GHz
- **RAM**: 64 GB
- **GPU**: NVIDIA A100 (40GB) or equivalent
- **Storage**: 50 GB SSD
- **Python**: 3.10+

**Capabilities**: Up to 20 qubits with statevector, 30 qubits with MPS, GPU acceleration

### High-Performance Configuration

- **CPU**: 64+ cores, 4.0 GHz
- **RAM**: 256 GB+
- **GPU**: 4× NVIDIA A100 (80GB)
- **Storage**: 1 TB NVMe SSD
- **Network**: InfiniBand for distributed computing

**Capabilities**: Up to 25 qubits with statevector, 35+ qubits with MPS, multi-GPU scaling

## Optimization Strategies

### 1. Backend Selection

**Statevector**: Fast for small systems (<15 qubits), exact results

```python
backend = AerSimulator(method='statevector', device='CPU')
```

**Matrix Product State**: Efficient for large systems with limited entanglement

```python
backend = AerSimulator(
    method='matrix_product_state',
    matrix_product_state_max_bond_dimension=128
)
```

**GPU Acceleration**: 5-10× speedup for large circuits

```python
backend = AerSimulator(method='statevector', device='GPU')
```

### 2. Circuit Optimization

**Transpilation**:

```python
from qiskit import transpile

# Aggressive optimization
t_circuit = transpile(
    circuit,
    backend,
    optimization_level=3,
    routing_method='sabre',
    layout_method='sabre'
)
```

**Gate Reduction**:

```python
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Optimize1qGatesDecomposition

pm = PassManager([Optimize1qGatesDecomposition(basis=['u3', 'cx'])])
optimized_circuit = pm.run(circuit)
```

### 3. Parallel Execution

**Multiple Shots**:

```python
job = backend.run(circuit, shots=1024, max_parallel_threads=8)
```

**Circuit Batching**:

```python
jobs = [backend.run(circ, shots=1024) for circ in circuits]
results = [job.result() for job in jobs]
```

### 4. Memory Management

**Lazy Evaluation**:

```python
generator = TraceGenerator(n_qubits=20, lazy=True)
for chunk in generator.generate_chunks(chunk_size=5):
    process(chunk)
```

**Checkpoint/Restart**:

```python
import pickle

# Save intermediate results
with open('checkpoint.pkl', 'wb') as f:
    pickle.dump({'iteration': i, 'params': params, 'energy': energy}, f)
```

## Results Interpretation

### Understanding Your Benchmarks

**Good performance indicators**:
- Circuit construction: <0.1s per qubit
- VQE convergence: <100 iterations for simple Hamiltonians
- Memory usage: <2^n MB for n qubits (statevector)
- Parallel efficiency: >70% at 8 cores

**Performance bottlenecks**:
- **Slow circuit construction**: Check for inefficient Python loops, consider vectorization
- **Slow execution**: Try different backend (MPS), enable GPU, reduce circuit depth
- **Poor VQE convergence**: Adjust ansatz, try different optimizer, initialize better
- **High memory usage**: Use MPS backend, reduce shots, implement checkpointing

### Comparing Results

When comparing to published benchmarks:

1. **Normalize for hardware**: Account for CPU/GPU differences
2. **Match problem size**: Same number of qubits, circuit depth
3. **Use same metrics**: Ensure identical measurement definitions
4. **Report confidence intervals**: Include error bars
5. **Document environment**: OS, Python version, dependency versions

## Reproducibility

### Environment Setup

```bash
# Create reproducible environment
python -m venv venv_benchmark
source venv_benchmark/bin/activate
pip install -r requirements.txt
pip freeze > requirements_frozen.txt
```

### System Information

```python
import platform
import psutil
import qiskit

print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {platform.python_version()}")
print(f"CPU: {platform.processor()}")
print(f"Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count()} logical")
print(f"RAM: {psutil.virtual_memory().total / 1024**3:.1f} GB")
print(f"Qiskit: {qiskit.__version__}")
```

### Benchmark Script Template

```python
import time
import json
from janus1.trace import TraceGenerator

def run_benchmark(n_qubits, n_trials=10):
    """Run standardized benchmark."""
    times = []
    for trial in range(n_trials):
        start = time.perf_counter()
        generator = TraceGenerator(n_qubits=n_qubits)
        circuit = generator.generate_circuit()
        result = run_simulation(circuit)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    return {
        'n_qubits': n_qubits,
        'mean_time': sum(times) / len(times),
        'std_time': (sum((t - sum(times)/len(times))**2 for t in times) / len(times))**0.5,
        'min_time': min(times),
        'max_time': max(times),
        'trials': n_trials
    }

if __name__ == '__main__':
    results = [run_benchmark(n) for n in [4, 8, 12, 16, 20]]
    with open('benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)
```

### Reporting Results

Include in your reports:

1. **Hardware specifications**: CPU, RAM, GPU
2. **Software versions**: OS, Python, Qiskit, Janus-1
3. **Benchmark parameters**: Problem size, shots, optimization level
4. **Statistical measures**: Mean, std dev, min, max
5. **Raw data**: Share full results for verification

## Advanced Topics

### Profiling with cProfile

```bash
python -m cProfile -o profile.stats examples/01_basic_simulation.py
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"
```

### Line-by-Line Profiling

```python
from line_profiler import LineProfiler

lp = LineProfiler()
lp_wrapper = lp(my_function)
lp_wrapper(args)
lp.print_stats()
```

### GPU Profiling

```bash
nvprof python examples/01_basic_simulation.py
# or with newer NVIDIA tools
nsys profile -t cuda,nvtx -o profile python examples/01_basic_simulation.py
```

## Contributing Benchmarks

We welcome benchmark contributions! Please:

1. Use the template above
2. Include full system specs
3. Run at least 10 trials
4. Document any optimizations
5. Share raw results
6. Open a PR with your results in `benchmarks/community/`

## Support

For performance questions:
- Open an issue with benchmark results
- Join discussions in Issues
- Check existing performance issues

## References

1. Qiskit Performance Guide: https://qiskit.org/documentation/
2. Quantum Computing Benchmarking: Various academic papers
3. HPC Best Practices: Community standards