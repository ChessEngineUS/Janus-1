# Janus-1 Quick Reference Guide

> **TL;DR**: Real-time LLM inference at the edge with 4W power and 15.8× better memory efficiency than existing solutions.

## 🚀 One-Minute Quickstart

### Option 1: Google Colab (Fastest)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ChessEngineUS/Janus-1/blob/main/Janus_1_Complete_Analysis.ipynb)

Click the badge above → Run all cells → Get complete results in ~5 minutes

### Option 2: Local Installation

```bash
git clone https://github.com/ChessEngineUS/Janus-1.git
cd Janus-1
pip install -r requirements.txt
pytest tests/ -v  # Verify installation
```

### Option 3: Python Package (Coming Soon)

```bash
pip install janus-1
```

---

## 📊 Key Numbers

| Metric | Value | Meaning |
|--------|-------|--------|
| **8.2 TOPS** | Compute | INT4/INT8 MAC operations |
| **4.05 W** | Power | Total system (compute + memory) |
| **79 mm²** | Area | 3nm GAA silicon die |
| **256 MB** | Memory | On-chip KV-cache for LLMs |
| **99.99%** | Hit Rate | Cache efficiency |
| **15.8×** | Efficiency | Better than Google Edge TPU |
| **1.0 cycle** | Latency | P99 read latency |

---

## 💡 Core Concepts

### What Problem Does Janus-1 Solve?

**Problem**: Running 7B-parameter LLMs on edge devices requires:
- Massive memory bandwidth (bottleneck)
- High power consumption (>20W)
- Large die area (expensive)

**Solution**: Janus-1 co-design approach:
1. **Algorithm**: INT4 quantization (8× memory reduction)
2. **Architecture**: 2-tier SRAM+eDRAM hierarchy
3. **Technology**: eDRAM for optimal power-latency-area
4. **Prefetcher**: FSM-based stream detection

**Result**: Real-time inference in <5W power envelope

### Architecture Overview

```
┌─────────────────────────────────────────┐
│           Janus-1 Processor             │
├─────────────────┬───────────────────────┤
│  Compute Fabric │   Memory Hierarchy    │
│                 │                       │
│  16 Tiles       │  T1: 32 MB SRAM      │
│  (4096 MACs)    │  - 4 quadrants       │
│  INT4/INT8      │  - 4 banks each      │
│  8.2 TOPS       │  - 1 cycle latency   │
│                 │                       │
│  0.327 W        │  T2: 224 MB eDRAM    │
│                 │  - 14 banks          │
│                 │  - 3 cycle latency   │
│                 │                       │
│                 │  Janus-Prefetch-1    │
│                 │  - Stream detector   │
│                 │  - 16-line lookahead │
│                 │  - <2K gates         │
└─────────────────┴───────────────────────┘
```

---

## 🎯 Common Use Cases

### 1. Run Full System Simulation

```python
from src.simulator.janus_sim import JanusSim
from src.benchmarks.trace_generator import generate_llm_trace

# Generate LLM workload
trace = generate_llm_trace(context_length=2048)

# Run simulation
sim = JanusSim()
sim.run(trace)

# Get results
metrics = sim.get_metrics()
print(f"Hit Rate: {metrics.hit_rate:.2f}%")
print(f"P99 Latency: {metrics.p99_latency} cycles")
```

### 2. Calculate KV-Cache Size

```python
from src.models.kv_cache_sizing import KVCacheSizer, ModelConfig

# Configure model
config = ModelConfig(
    num_layers=32,
    hidden_dim=4096,
    context_length=4096
)

# Calculate for INT4
sizer = KVCacheSizer(config)
result = sizer.calculate('INT4')

print(f"KV-Cache: {result['size_mb']} MB")
print(f"On-chip feasible: {result['size_mb'] < 256}")
```

### 3. Compare Memory Technologies

```python
from src.models.memory_power_model import MemoryPowerModel

for tech in ['HD_SRAM', 'eDRAM', 'STT_MRAM']:
    model = MemoryPowerModel(
        cache_size_mb=224,
        bandwidth_gb_s=20,
        technology=tech
    )
    power = model.estimate_power()
    print(f"{tech}: {power['total_w']:.2f} W")
```

### 4. Optimize Prefetcher

```python
from src.simulator.janus_sim import SimulationConfig

# Sweep lookahead depths
for lookahead in [4, 8, 16, 32, 64]:
    config = SimulationConfig(prefetch_look_ahead=lookahead)
    sim = JanusSim(config)
    sim.run(trace)
    metrics = sim.get_metrics()
    print(f"LA={lookahead}: Hit={metrics.hit_rate:.2f}%")
```

---

## 📚 Repository Structure

```
Janus-1/
├── src/                         # Source code
│   ├── simulator/              # Memory hierarchy simulator
│   │   ├── janus_sim.py       # Main simulator (★ start here)
│   │   └── prefetcher.py      # Prefetcher FSM
│   ├── models/                 # Power/area models
│   │   ├── kv_cache_sizing.py # Memory calculations
│   │   ├── memory_power_model.py
│   │   └── thermal_analysis.py
│   └── benchmarks/             # Trace generation
│       └── trace_generator.py
├── tests/                       # Test suite (15 tests)
├── experiments/                 # Evaluation scripts
├── docs/                        # Documentation
│   ├── EXAMPLES.md             # Code examples (★ read this)
│   └── architecture.md
├── Janus_1_Complete_Analysis.ipynb  # Colab notebook (★ try this first)
├── README.md                    # Project overview
├── CONTRIBUTING.md              # How to contribute
├── CHANGELOG.md                 # Version history
└── PROJECT_SUMMARY.md           # Executive summary
```

**Legend**: ★ = Recommended starting points

---

## 🔧 Configuration Options

### SimulationConfig Parameters

```python
from src.simulator.janus_sim import SimulationConfig

config = SimulationConfig(
    # Tier-1 SRAM
    t1_sram_size_mb=32,           # Total T1 capacity
    t1_sram_banks=16,             # Number of banks (4 per quad)
    t1_read_latency_cycles=1,     # Read latency
    
    # Tier-2 eDRAM
    t2_edram_banks=14,            # Number of banks
    t2_read_latency_cycles=3,     # Read latency
    
    # Cache parameters
    cache_line_size_bytes=128,    # Cache line size
    
    # Prefetcher
    prefetch_look_ahead=16,       # Lookahead depth (optimal)
    prefetch_issue_width=4,       # Max prefetches/cycle
)
```

### ModelConfig Parameters

```python
from src.models.kv_cache_sizing import ModelConfig

config = ModelConfig(
    num_layers=32,                # Transformer layers
    hidden_dim=4096,              # Model dimension
    num_heads=32,                 # Attention heads
    head_dim=128,                 # Head dimension
    context_length=4096,          # Max context tokens
)
```

---

## 📈 Performance Comparison

### vs. Google Edge TPU

```
Janus-1:    63 MB/W   (3nm, 4.05W)
Edge TPU:    4 MB/W   (16nm, 2W)
Advantage:   15.8×    (memory efficiency)
```

### vs. NVIDIA Jetson Orin

```
Janus-1:     63 MB/W   (3nm, 4.05W)
Jetson:    <0.2 MB/W   (8nm, 15-60W)
Advantage:   315×      (memory efficiency)
```

### Why Janus-1 Wins on Efficiency

1. **Specialized for memory-bound LLM inference**
2. **eDRAM technology** (1.15W for 224MB)
3. **99.99% cache hit rate** (prefetcher)
4. **INT4 quantization** (8× reduction)
5. **Co-designed** (algorithm + arch + tech)

---

## 🎓 Learning Path

### Beginner (1-2 hours)

1. ✅ Read [README.md](README.md) - Overview
2. ✅ Run [Colab Notebook](https://colab.research.google.com/github/ChessEngineUS/Janus-1/blob/main/Janus_1_Complete_Analysis.ipynb) - See results
3. ✅ Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Deep dive

### Intermediate (1 day)

4. ✅ Read [docs/EXAMPLES.md](docs/EXAMPLES.md) - Code patterns
5. ✅ Clone repo and run tests
6. ✅ Modify `experiments/run_full_system.py`
7. ✅ Run your own simulations

### Advanced (1 week)

8. ✅ Read [CONTRIBUTING.md](CONTRIBUTING.md)
9. ✅ Study source code in `src/`
10. ✅ Extend simulator with new features
11. ✅ Submit a pull request

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Tests fail with import errors
```bash
# Solution: Install in development mode
pip install -e .
```

**Issue**: `ModuleNotFoundError: No module named 'src'`
```bash
# Solution: Run from repository root
cd Janus-1
python -m pytest tests/
```

**Issue**: Colab notebook fails to load
```bash
# Solution: Use the direct link
https://colab.research.google.com/github/ChessEngineUS/Janus-1/blob/main/Janus_1_Complete_Analysis.ipynb
```

**Issue**: Slow simulation
```python
# Solution: Reduce trace size
trace = generate_llm_trace(context_length=1024)  # Instead of 4096
```

---

## 📝 Citation

If you use Janus-1 in your research, please cite:

```bibtex
@software{marena2026janus1,
  author = {Marena, Tommaso},
  title = {Janus-1: Real-Time Generative AI Acceleration at the Edge},
  year = {2026},
  url = {https://github.com/ChessEngineUS/Janus-1},
  version = {1.0.0}
}
```

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| **Repository** | https://github.com/ChessEngineUS/Janus-1 |
| **Colab Notebook** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ChessEngineUS/Janus-1/blob/main/Janus_1_Complete_Analysis.ipynb) |
| **Issues** | https://github.com/ChessEngineUS/Janus-1/issues |
| **Discussions** | https://github.com/ChessEngineUS/Janus-1/discussions |
| **Documentation** | [docs/](docs/) |
| **Examples** | [docs/EXAMPLES.md](docs/EXAMPLES.md) |
| **Contributing** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **Changelog** | [CHANGELOG.md](CHANGELOG.md) |

---

## 💬 Getting Help

1. **Check documentation** - Most answers are in [docs/](docs/)
2. **Search issues** - Someone may have asked before
3. **Ask in discussions** - Community Q&A
4. **Open an issue** - For bugs or feature requests

---

## 🌟 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of conduct
- Development setup
- Coding standards
- Pull request process

**Good first issues**: Look for `good-first-issue` label

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Made with ❤️ by [@ChessEngineUS](https://github.com/ChessEngineUS)**

**Last Updated**: January 10, 2026 | **Version**: 1.0.0
