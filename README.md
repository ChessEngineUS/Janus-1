# Janus-1: Real-Time Generative AI Acceleration at the Edge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/ChessEngineUS/Janus-1/actions/workflows/ci.yml/badge.svg)](https://github.com/ChessEngineUS/Janus-1/actions/workflows/ci.yml)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ChessEngineUS/Janus-1/blob/main/Janus_1_Complete_Analysis.ipynb)
[![arXiv](https://img.shields.io/badge/arXiv-2026.xxxxx-b31b1b.svg)](https://arxiv.org)

> A novel processor architecture enabling real-time execution of 7-billion-parameter language models within a sub-5-watt power envelope on edge devices.

## 🎯 Overview

Janus-1 is a specialized processor architecture designed to overcome the "memory wall" challenge in deploying large language models at the edge. Through a holistic co-design methodology combining algorithmic optimization, heterogeneous memory architecture, and intelligent prefetching, Janus-1 achieves:

- **8.2 TOPS** of INT4/INT8 performance
- **~4.05W** total power consumption
- **~79 mm²** estimated die area (3nm process)
- **256 MB** on-chip KV-cache capacity
- **99.99%** T1 cache hit rate
- **1.0 cycle** P99 read latency

### Key Innovations

1. **Heterogeneous Memory Hierarchy**: 32 MB SRAM + 224 MB eDRAM with 63 MB/W efficiency
2. **Janus-Prefetch-1 Engine**: FSM-based stream prefetcher achieving near-perfect hit rates
3. **Systolic Compute Fabric**: 16-tile array with 16×16 MAC units per tile
4. **End-to-End Co-Design**: Integrated quantization, memory tech selection, and prefetching

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────┐
│                  JANUS-1 SoC                       │
│ ┌──────────────────┐  ┌──────────────────┐        │
│ │ Compute Quadrant │  │ Compute Quadrant │        │
│ │  ┌────┐  ┌────┐  │  │  ┌────┐  ┌────┐  │        │
│ │  │ CT │..│ CT │  │  │  │ CT │..│ CT │  │  T2    │
│ │  └────┘  └────┘  │  │  └────┘  └────┘  │ eDRAM  │
│ │      (4 tiles)   │  │      (4 tiles)   │ 224 MB │
│ │  T1 SRAM (8MB)   │  │  T1 SRAM (8MB)   │        │
│ └──────────────────┘  └──────────────────┘        │
│           ↕                     ↕                  │
│           └─────── 2D MESH ─────┘                  │
│                                                    │
│ ┌──────────────────┐  ┌──────────────────┐        │
│ │ Compute Quadrant │  │ Compute Quadrant │        │
│ │  (4 tiles each)  │  │  (4 tiles each)  │        │
│ │  T1 SRAM (8MB)   │  │  T1 SRAM (8MB)   │        │
│ └──────────────────┘  └──────────────────┘        │
└────────────────────────────────────────────────────┘
```

## 📓 Interactive Notebook

### 🚀 Run Complete Analysis in Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ChessEngineUS/Janus-1/blob/main/Janus_1_Complete_Analysis.ipynb)

**One-click reproducible analysis** - Run the entire Janus-1 evaluation pipeline in your browser:

- ✅ **Zero setup required** - All dependencies auto-installed
- ✅ **5-10 minute runtime** - Complete analysis on free Colab tier
- ✅ **Publication-ready outputs** - 300 DPI figures + data exports
- ✅ **Fully reproducible** - Timestamped results with version control

#### What's Included:

1. **KV-Cache Theoretical Analysis** - Memory requirements for FP16/INT8/INT4
2. **Memory Technology Comparison** - SRAM vs. eDRAM vs. MRAM power/area models
3. **Quantization Validation** - Accuracy trade-offs on Llama-2 7B
4. **Cycle-Accurate Simulation** - Memory hierarchy with 99.99% hit rate
5. **Prefetcher Optimization** - Parameter sweeps for look-ahead depth
6. **Thermal Analysis** - Junction temperature and thermal margin
7. **PPA Summary** - Comprehensive Power-Performance-Area metrics
8. **9-Panel Visualization Suite** - Publication-quality figures
9. **Data Exports** - CSV/JSON for external analysis
10. **Summary Report** - Complete methodology and results

#### Quick Start:

```python
# The notebook automatically:
# 1. Clones the repository
# 2. Installs all dependencies
# 3. Runs complete analysis pipeline
# 4. Generates all figures and data
# 5. Creates downloadable results package

# Just click "Runtime → Run all" in Colab!
```

#### Generated Outputs:

- **Figures**: PNG (300 DPI) + PDF (vector) formats
- **Data**: 8+ CSV/JSON files with all experimental results
- **Report**: Comprehensive summary with methodology and findings
- **Package**: Downloadable ZIP with all outputs

## 📦 Repository Structure

```
Janus-1/
├── Janus_1_Complete_Analysis.ipynb  # 🆕 Publication-ready Colab notebook
├── .github/workflows/
│   └── ci.yml                       # 🆕 CI/CD pipeline configuration
├── src/
│   ├── simulator/
│   │   ├── janus_sim.py              # Cycle-accurate memory hierarchy simulator
│   │   ├── prefetcher.py             # Janus-Prefetch-1 FSM implementation
│   │   └── compute_tile.py           # Compute tile model
│   ├── models/
│   │   ├── kv_cache_sizing.py        # KV-cache size calculations
│   │   ├── memory_power_model.py     # Technology power/area modeling
│   │   ├── sram_area_model.py        # SRAM area estimation
│   │   └── thermal_analysis.py       # Junction temperature modeling
│   └── benchmarks/
│       ├── trace_generator.py        # Workload trace generation
│       └── validation.py             # Accuracy validation on WikiText-103
├── experiments/
│   ├── run_memory_sweep.py           # Memory hierarchy parameter sweeps
│   ├── run_prefetch_sweep.py         # Prefetcher look-ahead optimization
│   └── run_full_system.py            # End-to-end system evaluation
├── results/
│   ├── figures/                      # Generated plots and visualizations
│   └── data/                         # Raw experimental data
├── docs/
│   ├── architecture.md               # Detailed architecture documentation
│   ├── methodology.md                # Design methodology walkthrough
│   ├── api_reference.md              # Code API documentation
│   └── paper.pdf                     # Full research paper
├── tests/
│   └── test_*.py                     # Unit tests for all modules
├── requirements.txt
├── setup.py
├── LICENSE
└── README.md
```

## 🚀 Quick Start

### Option 1: Google Colab (Recommended)

**Fastest way to reproduce all results:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ChessEngineUS/Janus-1/blob/main/Janus_1_Complete_Analysis.ipynb)

Click the badge above, then select **Runtime → Run all**. Results will be generated in ~5-10 minutes.

### Option 2: Local Installation

```bash
git clone https://github.com/ChessEngineUS/Janus-1.git
cd Janus-1
pip install -r requirements.txt
```

### Run the Memory Hierarchy Simulator

```python
from src.simulator.janus_sim import JanusSim
from src.benchmarks.trace_generator import generate_llm_trace

# Generate synthetic LLM inference trace
trace = generate_llm_trace(context_length=2048, hidden_dim=4096)

# Initialize and run simulator
sim = JanusSim()
sim.run(trace)
sim.report()
```

**Expected Output:**
```
T1 Hit Rate: 99.99% (65520 hits / 65536 reads)
Latencies (cycles): P50=1.0, P90=1.0, P99=1.0
```

### Run Complete System Analysis

```bash
python experiments/run_full_system.py
```

This will:
1. Calculate KV-cache requirements
2. Compare memory technologies (SRAM, eDRAM, MRAM)
3. Optimize prefetcher parameters
4. Validate end-to-end PPA metrics
5. Generate all figures from the paper

## 📊 Key Results

### Memory Technology Comparison (224 MB Tier-2 Cache)

| Technology | Dynamic Power (W) | Static Power (W) | Total Power (W) |
|------------|-------------------|------------------|------------------|
| HD SRAM    | 0.24              | 17.69            | **17.93**        |
| eDRAM      | 0.27              | 0.88             | **1.15**         |
| STT-MRAM   | 0.34              | 0.02             | **0.36**         |

*eDRAM selected for optimal power-latency trade-off.*

### Comparative Analysis

| Metric            | Janus-1   | Google Edge TPU | NVIDIA Jetson Orin |
|-------------------|-----------|-----------------|--------------------||
| Process           | 3nm       | 16nm            | 8nm                |
| Performance       | 8.2 TOPS  | 4 TOPS          | 275 TOPS (sparse)  |
| Power             | ~4.05 W   | ~2 W            | 15-60 W            |
| **Mem per Watt**  | **63 MB/W** | 4 MB/W        | <0.2 MB/W          |

### Quantization Trade-offs

| Precision | Memory Footprint | Perplexity (WikiText-103) |
|-----------|------------------|---------------------------|
| FP16      | 2048 MB          | 5.42                      |
| INT8      | 1024 MB          | 5.79                      |
| **INT4**  | **256 MB**       | **6.04**                  |

## 🔬 Design Methodology

The Janus-1 design follows a systematic four-step co-design loop:

### Step 1: Problem Quantification
- Calculate theoretical KV-cache size for 7B parameter LLM
- Result: 1024 MB at INT8 for 4096-token context
- Conclusion: On-chip SRAM infeasible → algorithmic compression required

### Step 2: Algorithmic Mitigation
- Evaluate INT8 vs INT4 quantization on Llama-2 7B
- Benchmark on WikiText-103 validation set
- Selected INT4: 256 MB footprint, 6.04 perplexity (acceptable degradation)

### Step 3: Technology Selection
- Model power/area for SRAM, eDRAM, MRAM at 256 MB scale
- SRAM: 17.93W leakage (infeasible)
- eDRAM: 1.15W total (optimal)
- MRAM: 0.36W but higher latency

### Step 4: Prefetcher Design
- Designed FSM-based stream prefetcher
- Swept look-ahead depth: 4→32 lines
- Optimal: 16-line look-ahead
- Hardware cost: <2K logic gates
- Achieved: 99.99% hit rate

## 🧪 Experimental Setup

### Simulation Infrastructure
- **Tool**: Janus-Sim (custom cycle-accurate simulator)
- **Language**: Python 3.9+ with NumPy
- **Runtime**: ~10s per 65K-access trace (single 2.6 GHz core)
- **Validation**: Compared against open-source Transformer profiling tools

### Workload
- Synthetic memory access trace representing LLM attention phase
- Linear scan pattern validated against real Transformer profiles
- 65,536 memory operations per simulation run

### PPA Estimation
- **Process**: 3nm Gate-All-Around (GAA)
- **MAC Efficiency**: 0.5 pJ/MAC (INT4/INT8)
- **Basis**: Publicly available foundry data + academic literature

## 📈 Reproducibility

All results in the paper are fully reproducible:

### Method 1: Google Colab (Easiest)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ChessEngineUS/Janus-1/blob/main/Janus_1_Complete_Analysis.ipynb)

Run all cells → Download results package

### Method 2: Local Scripts

```bash
# Run all experiments and generate figures
bash scripts/reproduce_paper.sh

# Individual experiments
python experiments/run_memory_sweep.py
python experiments/run_prefetch_sweep.py
python experiments/run_thermal_analysis.py
```

Results will be saved to `results/` with timestamps.

## 🔧 CI/CD Pipeline

[![CI Status](https://github.com/ChessEngineUS/Janus-1/actions/workflows/ci.yml/badge.svg)](https://github.com/ChessEngineUS/Janus-1/actions/workflows/ci.yml)

Automated testing on every commit:

- ✅ **Multi-platform testing** - Ubuntu, macOS, Windows
- ✅ **Multi-version Python** - 3.9, 3.10, 3.11, 3.12
- ✅ **Code quality checks** - Linting (flake8), formatting (black), type checking (mypy)
- ✅ **Unit tests** - Pytest with coverage reporting
- ✅ **Simulation validation** - Memory hierarchy correctness
- ✅ **Model validation** - KV-cache sizing, power models
- ✅ **Notebook validation** - Colab notebook integrity checks

### Running Tests Locally

```bash
# Install test dependencies
pip install pytest pytest-cov flake8 black mypy

# Run all tests
pytest tests/ -v --cov=src

# Run linting
flake8 src tests

# Check formatting
black --check src tests

# Type checking
mypy src
```

## 🧩 Code Examples

### Custom Memory Configuration

```python
from src.simulator.janus_sim import JanusSim

sim = JanusSim(
    t1_sram_size_mb=32,
    t2_edram_size_mb=224,
    cache_line_size=128,
    prefetch_lookahead=16
)
```

### Power Analysis

```python
from src.models.memory_power_model import MemoryPowerModel

model = MemoryPowerModel(
    cache_size_mb=224,
    bandwidth_gb_s=20,
    technology='eDRAM'
)

power = model.estimate_power()
print(f"Total Power: {power.total_w:.2f} W")
```

### Area Estimation

```python
from src.models.sram_area_model import estimate_sram_area

area_mm2 = estimate_sram_area(
    cache_size_mb=32,
    process_node_nm=3,
    efficiency=0.65
)
```

## 🔧 Advanced Usage

### Custom Prefetcher Policies

Implement your own prefetcher by subclassing `BasePrefetcher`:

```python
from src.simulator.prefetcher import BasePrefetcher

class MyPrefetcher(BasePrefetcher):
    def on_access(self, addr, is_hit):
        # Your custom prefetch logic
        if self.detect_stride(addr):
            return self.generate_prefetches(addr)
        return []
```

### Multi-Configuration Sweeps

```python
from src.experiments.parameter_sweep import run_sweep

results = run_sweep(
    param_name='prefetch_lookahead',
    values=[4, 8, 16, 32, 64],
    trace=my_trace
)
```

## 📚 Documentation

- **[Architecture Guide](docs/architecture.md)**: Detailed component specifications
- **[Methodology](docs/methodology.md)**: Step-by-step design process
- **[API Reference](docs/api_reference.md)**: Complete code documentation
- **[Paper](docs/paper.pdf)**: Full research paper with appendices
- **[Colab Notebook](Janus_1_Complete_Analysis.ipynb)**: Interactive analysis

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test suite
pytest tests/test_simulator.py -v
```

## 🤝 Contributing

We welcome contributions! Areas of interest:

- FPGA emulation implementations (Verilog/SystemVerilog)
- Extended workload traces (encoder-decoder models)
- Alternative memory technologies (HBM, ReRAM)
- Power/thermal optimization algorithms
- RTL implementations of compute tiles

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 Citation

If you use Janus-1 in your research, please cite:

```bibtex
@article{janus1_2026,
  title={Janus-1: A Systems-Level Design Methodology for Real-Time Generative AI Acceleration at the Edge},
  author={Marena, Tommaso and The Janus-1 Design Team},
  journal={arXiv preprint arXiv:2026.xxxxx},
  year={2026},
  url={https://github.com/ChessEngineUS/Janus-1}
}
```

## 🗺️ Future Work

1. **FPGA Emulation**: Hardware validation of memory hierarchy and prefetcher
2. **RTL Implementation**: Full Verilog/SystemVerilog design of compute quadrant
3. **Tape-out**: Multi-project wafer (MPW) run for silicon validation
4. **Extended Workloads**: Encoder-decoder models, vision transformers
5. **Compiler Support**: INT4 code generation and optimization

## 📞 Contact

- **Lead Researcher**: Tommaso Marena
- **GitHub Issues**: [Report bugs or request features](https://github.com/ChessEngineUS/Janus-1/issues)
- **Discussions**: [Join the community](https://github.com/ChessEngineUS/Janus-1/discussions)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Foundry process technology data based on public IEDM/ISSCC publications
- Benchmarking infrastructure inspired by open-source Transformer profiling tools
- Memory modeling validated against academic literature from MICRO/ISCA conferences

---

**Made with ❤️ for edge AI | [Documentation](https://github.com/ChessEngineUS/Janus-1/wiki) | [Paper](docs/paper.pdf) | [Colab Notebook](Janus_1_Complete_Analysis.ipynb) | [arXiv](https://arxiv.org)**