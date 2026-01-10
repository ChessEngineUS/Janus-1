# Janus-1 Documentation

Welcome to the comprehensive documentation for the Janus-1 processor architecture project.

## 📚 Documentation Index

### Getting Started

1. **[Main README](../README.md)** - Start here! Project overview and quick start
2. **[Quick Reference Guide](../QUICK_REFERENCE.md)** - TL;DR version with key info
3. **[Project Summary](../PROJECT_SUMMARY.md)** - Executive summary and detailed results

### User Guides

4. **[Code Examples](EXAMPLES.md)** - Comprehensive code examples and tutorials
5. **[Colab Notebook](../Janus_1_Complete_Analysis.ipynb)** - Interactive analysis (click to open)

### Technical Documentation

6. **Architecture Documentation** (this folder)
   - System architecture overview
   - Memory hierarchy design
   - Prefetcher FSM specification
   - Compute fabric organization

7. **API Reference** - Auto-generated from docstrings
   - Simulator APIs
   - Model APIs
   - Benchmark APIs

### Development

8. **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute
9. **[Code of Conduct](../CODE_OF_CONDUCT.md)** - Community guidelines
10. **[Changelog](../CHANGELOG.md)** - Version history

### Research

11. **Design Methodology** - Co-design process walkthrough
12. **Experimental Setup** - Reproducibility details
13. **Results Analysis** - Performance evaluation

---

## 🎯 Quick Navigation by Role

### 👨‍💻 For Users

Want to use Janus-1 in your project?

1. Start with [Main README](../README.md)
2. Run the [Colab Notebook](../Janus_1_Complete_Analysis.ipynb)
3. Check [Code Examples](EXAMPLES.md) for your use case
4. Explore the API documentation below

### 🔬 For Researchers

Want to understand the research?

1. Read [Project Summary](../PROJECT_SUMMARY.md)
2. Review design methodology
3. Examine experimental results
4. Check [CITATION.cff](../CITATION.cff) for citing

### 🛠️ For Contributors

Want to contribute to the project?

1. Read [Contributing Guide](../CONTRIBUTING.md)
2. Review [Code of Conduct](../CODE_OF_CONDUCT.md)
3. Check [open issues](https://github.com/ChessEngineUS/Janus-1/issues)
4. See development setup instructions

### 🏫 For Students

Want to learn about processor design?

1. Start with [Quick Reference](../QUICK_REFERENCE.md)
2. Read the architecture documentation
3. Work through [Code Examples](EXAMPLES.md)
4. Experiment with the simulator

---

## 💻 API Documentation

### Core Modules

#### Simulator

**`src.simulator.janus_sim`**

```python
from src.simulator.janus_sim import JanusSim, SimulationConfig, SimulationMetrics

# Main simulator class
class JanusSim:
    """Cycle-accurate memory hierarchy simulator."""
    
    def __init__(self, config: SimulationConfig = None)
    def run(self, trace: List[Tuple[str, int]]) -> None
    def get_metrics(self) -> SimulationMetrics
    def report(self) -> None
```

**Key Classes:**
- `JanusSim` - Main simulator
- `SimulationConfig` - Configuration parameters
- `SimulationMetrics` - Performance metrics

**See also:** [Simulator Examples](EXAMPLES.md#memory-hierarchy-simulation)

#### Models

**`src.models.kv_cache_sizing`**

```python
from src.models.kv_cache_sizing import KVCacheSizer, ModelConfig

class KVCacheSizer:
    """Calculate KV-cache memory requirements."""
    
    def __init__(self, config: ModelConfig)
    def calculate(self, precision: str) -> dict
    def calculate_all_precisions(self) -> dict
```

**See also:** [KV-Cache Examples](EXAMPLES.md#kv-cache-analysis)

**`src.models.memory_power_model`**

```python
from src.models.memory_power_model import MemoryPowerModel

class MemoryPowerModel:
    """Estimate power for memory technologies."""
    
    def __init__(self, cache_size_mb, bandwidth_gb_s, technology)
    def estimate_power(self) -> dict
```

**See also:** [Power Model Examples](EXAMPLES.md#memory-technology-comparison)

**`src.models.thermal_analysis`**

```python
from src.models.thermal_analysis import ThermalAnalyzer

class ThermalAnalyzer:
    """Calculate junction temperature."""
    
    def __init__(self, power_w, ambient_c, theta_ja_c_per_w)
    def calculate_junction_temp(self, package) -> dict
```

**See also:** [Thermal Examples](EXAMPLES.md#thermal-analysis)

#### Benchmarks

**`src.benchmarks.trace_generator`**

```python
from src.benchmarks.trace_generator import (
    generate_llm_trace,
    generate_random_trace,
    generate_strided_trace,
    analyze_trace
)

# Generate various trace patterns
trace = generate_llm_trace(context_length=2048)
trace = generate_random_trace(num_accesses=10000)
trace = generate_strided_trace(stride=4)

# Analyze trace characteristics
stats = analyze_trace(trace)
```

**See also:** [Trace Generator Source](../src/benchmarks/trace_generator.py)

---

## 📖 Architecture Documentation

### System Overview

Janus-1 is a domain-specific processor optimized for LLM inference at the edge.

**Key Components:**

1. **Compute Fabric** (8.2 TOPS)
   - 16 tiles across 4 quadrants
   - 4,096 MACs total (INT4/INT8)
   - Systolic dataflow architecture
   - 0.327W power consumption

2. **Memory Hierarchy** (256 MB total)
   - **Tier 1**: 32 MB HD SRAM
     - 4 quadrants × 8 MB each
     - 4 banks per quadrant
     - 1 cycle read latency
     - 2.56W power (mostly static)
   
   - **Tier 2**: 224 MB eDRAM
     - 14 banks
     - 3 cycle read latency
     - 1.15W power (dynamic + refresh)

3. **Janus-Prefetch-1 Engine**
   - FSM-based stream prefetcher
   - 16-line lookahead depth
   - 4-way issue width
   - <2K logic gates
   - Achieves 99.99% hit rate

### Memory Hierarchy Diagram

```
                    CPU Core
                       |
                       v
        ┌─────────────────────┐
        │  Janus-Prefetch-1   │
        │   Stream Detector   │
        └─────────┬──────────┘
                 |
                 v
        ┌─────────────────────┐
        │   Tier 1: SRAM     │  1 cycle
        │      32 MB         │  99.99% hit
        │    16 banks        │  2.56W
        └─────────┬──────────┘
                 | (on miss)
                 v
        ┌─────────────────────┐
        │   Tier 2: eDRAM    │  3 cycles
        │     224 MB         │  0.01% miss
        │    14 banks        │  1.15W
        └─────────────────────┘
```

### Prefetcher FSM States

```
     ┌────────────┐
     │    IDLE     │
     └─────┬──────┘
          | Stream
          | Detected
          v
     ┌────────────┐
     │  STREAMING  │ <---+
     └─────┬──────┘     |
          |              |
          | Pattern      | Continue
          | Break        | Stream
          v              |
     ┌────────────┐     |
     │  TRAINING   │ ----+
     └────────────┘
```

---

## 🧪 Testing & Validation

### Test Coverage

```
Module                          Tests    Coverage
────────────────────────────────────────────────────
src/simulator/janus_sim.py      7        82%
src/models/memory_power_model.py 3       58%
src/models/kv_cache_sizing.py   3        54%
src/models/thermal_analysis.py  2        45%
────────────────────────────────────────────────────
TOTAL                           15       65%
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_simulator.py -v

# Run only fast tests
pytest tests/ -v -m "not slow"
```

---

## 📊 Performance Benchmarks

### Key Results

| Metric | Value | Context |
|--------|-------|--------|
| **Cache Hit Rate** | 99.99% | T1 cache with prefetcher |
| **P99 Latency** | 1.0 cycle | Read operations |
| **Memory Efficiency** | 63 MB/W | 15.8× vs Edge TPU |
| **Power** | 4.05 W | Total system |
| **Area** | 79 mm² | 3nm GAA process |

### Comparison vs. Baselines

**Memory Efficiency (MB/W)**

```
Janus-1:        ████████████████ 63 MB/W
Edge TPU:       █ 4 MB/W
Jetson Orin:    < 0.2 MB/W
```

---

## 🔗 External Resources

### Research Papers

- [Transformer Architecture](https://arxiv.org/abs/1706.03762) - Vaswani et al.
- [LLM Quantization](https://arxiv.org/abs/2103.13630) - Dettmers et al.
- [eDRAM Technology](https://ieeexplore.ieee.org/) - ISSCC/IEDM papers

### Related Projects

- [PyTorch](https://pytorch.org/) - Deep learning framework
- [Transformers](https://huggingface.co/transformers/) - HuggingFace library
- [TinyML](https://www.tinyml.org/) - ML on edge devices

### Tools & Frameworks

- [Qiskit](https://qiskit.org/) - Quantum computing (if extending)
- [Cocotb](https://www.cocotb.org/) - Hardware verification
- [Verilator](https://verilator.org/) - Verilog simulation

---

## ❓ FAQ

### General Questions

**Q: What is Janus-1?**

A: A processor architecture for real-time LLM inference at the edge with <5W power.

**Q: Is this production-ready?**

A: This is a research prototype. The simulator and models are ready for academic use. Silicon implementation is planned for 2026.

**Q: Can I use this in my project?**

A: Yes! The code is MIT licensed. See [LICENSE](../LICENSE).

### Technical Questions

**Q: Why eDRAM instead of SRAM?**

A: eDRAM provides 15× better energy efficiency than SRAM for large caches (>32MB) while maintaining acceptable latency (3 cycles).

**Q: Why INT4 quantization?**

A: INT4 reduces memory footprint by 8× vs FP16 with acceptable accuracy loss (6.04 vs 5.79 perplexity on WikiText-103).

**Q: How does prefetcher achieve 99.99% hit rate?**

A: LLM inference has sequential access patterns. FSM-based stream detection with 16-line lookahead captures this pattern effectively.

### Usage Questions

**Q: How do I get started?**

A: Easiest way is the [Colab notebook](../Janus_1_Complete_Analysis.ipynb). For local use, see [README](../README.md).

**Q: Can I modify the architecture?**

A: Yes! Modify `SimulationConfig` parameters and re-run simulations. See [examples](EXAMPLES.md).

**Q: How do I cite this work?**

A: See [CITATION.cff](../CITATION.cff) for BibTeX format.

---

## 📞 Contact & Support

### Community Channels

- **GitHub Issues**: [Report bugs or request features](https://github.com/ChessEngineUS/Janus-1/issues)
- **GitHub Discussions**: [Ask questions or share ideas](https://github.com/ChessEngineUS/Janus-1/discussions)
- **Pull Requests**: [Contribute code](https://github.com/ChessEngineUS/Janus-1/pulls)

### Maintainer

- **Tommaso Marena** ([@ChessEngineUS](https://github.com/ChessEngineUS))
- Email: 112788717+ChessEngineUS@users.noreply.github.com

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](../LICENSE) for details.

---

**Last Updated**: January 10, 2026 | **Version**: 1.0.0

**⭐ Star the repo** | **🐛 Report issues** | **💬 Join discussions**
