# Changelog

All notable changes to the Janus-1 project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CONTRIBUTING.md with comprehensive contribution guidelines
- CHANGELOG.md for tracking project changes
- Enhanced README.md with additional badges and improved formatting
- Code coverage badge support
- DOI/Zenodo badge for research citation

### Changed
- Improved documentation structure and clarity
- Enhanced CI/CD badge display in README

### Fixed
- Test assertion in `test_memory_power_model_sram` expecting 'HD_SRAM' instead of 'HD SRAM'

---

## [1.0.0] - 2026-01-10

### Added

#### Core Features
- **Janus-Sim**: Cycle-accurate memory hierarchy simulator
  - Two-tier SRAM+eDRAM memory system (32 MB + 224 MB)
  - Bank conflict modeling (4 SRAM banks, 14 eDRAM banks)
  - LRU cache replacement policy
  - Event-driven simulation engine

- **Janus-Prefetch-1**: FSM-based stream prefetcher
  - Configurable look-ahead depth (optimized at 16 lines)
  - 4-wide prefetch issue
  - 99.99% cache hit rate achievement
  - <2K gate hardware cost

- **Memory Technology Models**
  - Power modeling for HD SRAM, eDRAM, STT-MRAM
  - Area estimation at 3nm GAA process
  - Thermal analysis with junction temperature modeling
  - Technology comparison and selection methodology

- **KV-Cache Analysis**
  - Size calculation for FP32, FP16, INT8, INT4 precisions
  - Support for arbitrary model configurations
  - Llama-2 7B validation on WikiText-103

#### Analysis Tools
- **Google Colab Notebook**: Complete end-to-end analysis pipeline
  - Zero-setup reproducible research
  - 10 comprehensive analysis sections
  - Publication-quality 9-panel visualization suite
  - Automated data export (CSV/JSON)
  - Downloadable results package

- **Experiment Scripts**
  - Memory hierarchy parameter sweeps
  - Prefetcher optimization studies
  - Full system PPA evaluation
  - Thermal analysis tools

#### Testing Infrastructure
- **Comprehensive Test Suite**
  - 15+ unit tests covering all modules
  - Pytest-based testing framework
  - 65%+ code coverage
  - Model validation tests
  - Simulation correctness tests

- **CI/CD Pipeline**
  - Multi-platform testing (Ubuntu, macOS, Windows)
  - Multi-version Python support (3.9, 3.10, 3.11, 3.12)
  - Automated linting (flake8)
  - Code formatting checks (black)
  - Type checking (mypy)

#### Documentation
- **README.md**: Comprehensive project documentation
  - Architecture overview with ASCII diagram
  - Quick start guide
  - Installation instructions
  - Usage examples
  - Key results and comparative analysis
  - Design methodology walkthrough

- **Code Documentation**
  - Google-style docstrings for all public APIs
  - Type hints throughout codebase
  - Inline comments for complex algorithms
  - Example usage in docstrings

### Key Results

#### Performance Metrics
- **Compute**: 8.2 TOPS (INT4/INT8)
- **Power**: ~4.05 W total system power
- **Area**: ~79 mm² (3nm process)
- **Memory Efficiency**: 63 MB/W (15.8× better than Google Edge TPU)
- **Cache Hit Rate**: 99.99%
- **P99 Latency**: 1.0 cycle

#### Memory Technology Selection
- Evaluated HD SRAM, eDRAM, and STT-MRAM
- Selected eDRAM for T2 cache (224 MB)
  - Total power: 1.15 W
  - Memory efficiency: 194.8 MB/W
  - Optimal power-latency trade-off

#### Quantization Validation
- Llama-2 7B on WikiText-103
- INT4: 256 MB footprint, 6.04 perplexity (+11.4% vs FP16)
- 8× memory reduction vs FP16
- Acceptable accuracy degradation for edge deployment

#### Prefetcher Optimization
- Optimal look-ahead: 16 cache lines
- 99.99% T1 hit rate achieved
- Hardware cost: <2K logic gates (FSM implementation)
- Minimal area and power overhead

### Design Methodology

1. **Problem Quantification**: Calculated theoretical KV-cache requirements
2. **Algorithmic Mitigation**: Selected INT4 quantization (256 MB footprint)
3. **Technology Selection**: Chose eDRAM for power-latency optimization
4. **Prefetcher Design**: Optimized FSM-based stream prefetcher

### Repository Structure

```
Janus-1/
├── src/                          # Source code
│   ├── simulator/                # Memory hierarchy simulator
│   ├── models/                   # Power/area/thermal models
│   └── benchmarks/               # Workload generation and validation
├── experiments/                  # Analysis scripts
├── tests/                        # Test suite
├── results/                      # Generated outputs
├── docs/                         # Documentation
├── Janus_1_Complete_Analysis.ipynb  # Colab notebook
├── requirements.txt              # Dependencies
└── README.md                     # Project documentation
```

### Dependencies

- Python 3.9+
- NumPy
- Pandas
- Matplotlib
- Seaborn
- Pytest (testing)
- Flake8 (linting)
- Black (formatting)
- MyPy (type checking)

---

## Version History Summary

- **v1.0.0** (2026-01-10): Initial release with complete Janus-1 design, simulation, and analysis tools

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Citation

If you use this work, please cite:

```bibtex
@article{janus1_2026,
  title={Janus-1: A Systems-Level Design Methodology for Real-Time 
         Generative AI Acceleration at the Edge},
  author={Marena, Tommaso and The Janus-1 Design Team},
  journal={arXiv preprint arXiv:2026.xxxxx},
  year={2026},
  url={https://github.com/ChessEngineUS/Janus-1}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
