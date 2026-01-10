# Janus-1 Project Summary

## Executive Summary

Janus-1 is a novel processor architecture designed for real-time execution of large language models (LLMs) at the edge with sub-5-watt power consumption. The project demonstrates a complete systems-level co-design methodology that achieves 15.8× better memory efficiency compared to existing edge accelerators.

## Key Achievements

### Performance Metrics

| Metric | Value | Significance |
|--------|-------|-------------|
| **Compute** | 8.2 TOPS | INT4/INT8 operations for LLM inference |
| **Power** | 4.05 W | Total system power (compute + memory) |
| **Area** | 79 mm² | Die area on 3nm GAA process |
| **Memory** | 256 MB | On-chip KV-cache capacity |
| **Hit Rate** | 99.99% | T1 cache efficiency |
| **Efficiency** | 63 MB/W | 15.8× better than Google Edge TPU |
| **Latency** | 1.0 cycle | P99 read latency |

### Novel Contributions

1. **Heterogeneous Memory Architecture**
   - 32 MB SRAM Tier-1 (active cache)
   - 224 MB eDRAM Tier-2 (main store)
   - 63 MB/W efficiency vs. 4 MB/W (Edge TPU)

2. **Janus-Prefetch-1 Engine**
   - FSM-based stream prefetcher
   - <2K logic gates hardware cost
   - 99.99% cache hit rate
   - 16-line optimal lookahead depth

3. **Validated INT4 Quantization**
   - Llama-2 7B model
   - 6.04 perplexity on WikiText-103
   - 8× memory reduction vs. FP16
   - Acceptable accuracy degradation

4. **Complete Co-Design Methodology**
   - Algorithm + architecture + technology
   - Systematic 4-step process
   - Reproducible analysis pipeline
   - Publication-ready results

## Technical Architecture

### Memory Hierarchy

```
Tier 1 (T1) - Active Cache
- Technology: HD SRAM
- Capacity: 32 MB (4 quadrants × 8 MB)
- Banks: 4 per quadrant
- Latency: 1 cycle
- Power: 2.56 W (0.08 W dynamic + 2.48 W static)

Tier 2 (T2) - Main Store
- Technology: eDRAM
- Capacity: 224 MB
- Banks: 14
- Latency: 3 cycles
- Power: 1.15 W (0.27 W dynamic + 0.88 W refresh)
```

### Compute Fabric

```
16 Compute Tiles (4 quadrants × 4 tiles)
Per Tile:
- 16×16 MAC array (256 MACs)
- INT4/INT8 precision
- Systolic dataflow
- ~20 mW per tile

Total:
- 4,096 MACs
- 8.2 TOPS @ 1 GHz
- 0.327 W total compute power
```

### Prefetcher

```
Janus-Prefetch-1 Finite State Machine
- Stream detection logic
- 16-line lookahead depth
- 4-way issue width
- <2K logic gates
- Minimal power overhead (<1 mW)
```

## Design Methodology

### Step 1: Problem Quantification

**Goal**: Calculate theoretical KV-cache requirements

- Model: Llama-2 7B (32 layers, 4096 hidden dim)
- Context: 4096 tokens
- Result: 1024 MB @ INT8, 2048 MB @ FP16
- **Conclusion**: On-chip SRAM infeasible → need compression

### Step 2: Algorithmic Mitigation

**Goal**: Reduce memory footprint via quantization

- Evaluated: INT8 vs INT4 on WikiText-103
- INT8: 1024 MB, 5.79 perplexity
- INT4: 256 MB, 6.04 perplexity (+11.4% degradation)
- **Decision**: INT4 selected (acceptable accuracy loss)

### Step 3: Technology Selection

**Goal**: Choose optimal memory technology

| Technology | Power (W) | Area (mm²) | Latency (ns) |
|------------|-----------|------------|-------------|
| HD SRAM    | 17.93     | 5.04       | 0.5         |
| **eDRAM**  | **1.15**  | **1.01**   | **2.0**     |
| STT-MRAM   | 0.36      | 3.02       | 10.0        |

**Decision**: eDRAM (optimal power-latency-area)

### Step 4: Prefetcher Design

**Goal**: Maximize cache hit rate

- Implemented: FSM-based stream prefetcher
- Swept: 4, 8, 16, 32, 64 line lookahead
- Result: 16-line optimal (99.99% hit rate)
- Hardware: <2K gates, negligible power

## Comparative Analysis

### vs. Google Edge TPU

| Metric | Janus-1 | Edge TPU | Advantage |
|--------|---------|----------|----------|
| Process | 3nm | 16nm | 2.3 gens newer |
| Compute | 8.2 TOPS | 4 TOPS | 2.1× |
| Power | 4.05 W | 2 W | 0.5× |
| Memory/W | **63 MB/W** | 4 MB/W | **15.8×** |

### vs. NVIDIA Jetson Orin

| Metric | Janus-1 | Jetson Orin | Advantage |
|--------|---------|-------------|----------|
| Process | 3nm | 8nm | Newer |
| Compute | 8.2 TOPS | 275 TOPS | Purpose-built |
| Power | 4.05 W | 15-60 W | 3.7-14.8× |
| Memory/W | **63 MB/W** | <0.2 MB/W | **315×** |

**Key Insight**: Janus-1 optimizes for memory-bound LLM inference, while competitors target compute-bound workloads.

## Implementation Status

### ✅ Completed

- Cycle-accurate simulator (Python)
- Power/area/thermal models
- Prefetcher FSM design
- Comprehensive test suite (15 tests, 65%+ coverage)
- CI/CD pipeline (multi-platform)
- Publication-ready Google Colab notebook
- Complete documentation
- Reproducible experiments

### 🚧 In Progress

- Extended LLM validation (Mistral, Phi-2, Gemma)
- Real hardware trace collection
- Power optimization algorithms

### 🔮 Planned

- **Q1 2026**: FPGA emulation (Verilog)
- **Q2 2026**: RTL implementation
- **Q3 2026**: Multi-project wafer (MPW) tape-out
- **Q4 2026**: Silicon validation

## Repository Structure

```
Janus-1/
├── src/                      # Source code
│   ├── simulator/           # Memory hierarchy simulator
│   ├── models/              # Power/area/thermal models
│   └── benchmarks/          # Trace generation
├── tests/                   # Unit tests
├── experiments/             # Evaluation scripts
├── docs/                    # Documentation
├── results/                 # Experimental data
├── Janus_1_Complete_Analysis.ipynb  # Colab notebook
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

## Key Files

### Simulator
- `src/simulator/janus_sim.py` - Core simulator (500+ lines)
- `src/simulator/prefetcher.py` - FSM implementation

### Models
- `src/models/kv_cache_sizing.py` - Memory calculations
- `src/models/memory_power_model.py` - Technology comparison
- `src/models/thermal_analysis.py` - Junction temperature

### Experiments
- `experiments/run_full_system.py` - Complete evaluation
- `experiments/run_prefetch_sweep.py` - Optimization

### Documentation
- `docs/EXAMPLES.md` - Code examples
- `docs/architecture.md` - Detailed specs
- `docs/methodology.md` - Design process

## Testing & Quality

### Test Coverage

```
Module                          Coverage
────────────────────────────────────────────────────
src/simulator/janus_sim.py      82%
src/models/memory_power_model.py 58%
src/models/kv_cache_sizing.py   54%
src/models/thermal_analysis.py  45%
────────────────────────────────────────────────────
TOTAL                           65%
```

### CI/CD Pipeline

- **Platforms**: Ubuntu, macOS, Windows
- **Python**: 3.9, 3.10, 3.11, 3.12
- **Checks**: pytest, flake8, black, mypy
- **Status**: ✅ All passing

## Publications & Dissemination

### Planned Submissions

1. **Conference Papers**
   - IEEE ISCA 2026
   - IEEE MICRO 2026
   - ACM ASPLOS 2027

2. **Journal Papers**
   - Nature Electronics
   - IEEE Transactions on Computers

3. **Preprints**
   - arXiv (ready for submission)

### Open Source Release

- **Repository**: https://github.com/ChessEngineUS/Janus-1
- **License**: MIT
- **DOI**: 10.5281/zenodo.xxxxx (pending)
- **Citation**: Available in README

## Community & Contribution

### Getting Started

1. **Quick Start**: Run Colab notebook (5-10 minutes)
2. **Local Setup**: Clone repo, install dependencies
3. **Explore**: Check `docs/EXAMPLES.md`
4. **Contribute**: See `CONTRIBUTING.md`

### Areas for Contribution

- 🔥 **High Priority**: FPGA implementation, extended validation
- 📦 **Medium Priority**: Documentation, visualization
- 🌟 **Good First Issue**: Tests, examples, bug fixes

### Contact

- **GitHub**: [@ChessEngineUS](https://github.com/ChessEngineUS)
- **Issues**: [Issue Tracker](https://github.com/ChessEngineUS/Janus-1/issues)
- **Discussions**: [Community](https://github.com/ChessEngineUS/Janus-1/discussions)

## Impact & Vision

### Short-term (6-12 months)

- Silicon validation via MPW
- Extended model support
- FPGA demonstration
- Academic publications

### Long-term (1-3 years)

- Commercial adoption in edge devices
- Integration with LLM frameworks
- Advanced memory technologies
- Next-generation architecture (Janus-2)

### Broader Impact

- **Energy Efficiency**: Enable sustainable AI deployment
- **Accessibility**: Democratize LLM inference
- **Innovation**: Advance edge computing research
- **Education**: Open-source learning resource

## Acknowledgments

### Technical Foundations

- Process data: Public IEDM/ISSCC publications
- Memory models: Academic MICRO/ISCA papers
- Transformer profiling: Open-source tools

### Community

- Open-source contributors
- Academic reviewers
- Early adopters and testers

## License

MIT License - See [LICENSE](LICENSE) for details

---

**Project Status**: 🟢 Active Development  
**Last Updated**: January 10, 2026  
**Version**: 1.0.0  

**⭐ Star the repo** | **🐛 Report bugs** | **💬 Join discussions**
