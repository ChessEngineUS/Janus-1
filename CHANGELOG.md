# Changelog

All notable changes to the Janus-1 project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CONTRIBUTING.md with comprehensive contribution guidelines
- CHANGELOG.md for tracking project changes
- Enhanced README badges (codecov, code style, DOI, stars)
- Improved README formatting and organization

### Changed
- Updated README with performance metrics table
- Enhanced comparative analysis section with clearer advantages
- Improved CI/CD documentation

### Fixed
- Test assertion in `test_memory_power_model_sram` to expect 'HD_SRAM' instead of 'HD SRAM'

## [1.0.0] - 2026-01-10

### Added
- Initial public release of Janus-1
- Complete cycle-accurate memory hierarchy simulator (`JanusSim`)
- Janus-Prefetch-1 FSM-based stream prefetcher implementation
- KV-cache sizing models for FP16/INT8/INT4 quantization
- Memory technology power/area models (SRAM, eDRAM, MRAM)
- SRAM area estimation tools
- Thermal analysis with junction temperature modeling
- Comprehensive test suite with 15 unit tests
- CI/CD pipeline with multi-platform testing (Ubuntu, macOS, Windows)
- Multi-version Python support (3.9, 3.10, 3.11, 3.12)
- Publication-ready Google Colab notebook with complete analysis
- Automated code quality checks (flake8, black, mypy)
- Memory hierarchy parameter sweep experiments
- Prefetcher look-ahead optimization experiments
- Full system evaluation scripts

### Documentation
- Comprehensive README with architecture overview
- Quick start guide for local and Colab execution
- Design methodology documentation (4-step co-design process)
- API documentation for all modules
- Reproducibility instructions

### Results
- **8.2 TOPS** INT4/INT8 compute performance
- **~4.05 W** total power consumption
- **~79 mm²** die area at 3nm process
- **99.99%** T1 cache hit rate
- **63 MB/W** memory efficiency (15.8× better than Google Edge TPU)
- **1.0 cycle** P99 read latency
- INT4 quantization validation on Llama-2 7B (6.04 perplexity)

### Architecture Highlights
- **Heterogeneous memory**: 32 MB SRAM (T1) + 224 MB eDRAM (T2)
- **Compute fabric**: 16 tiles, 16×16 MAC units per tile
- **Prefetcher**: <2K gate FSM with 16-line look-ahead
- **Process technology**: 3nm Gate-All-Around (GAA)

---

## Release Notes Template

### [Version Number] - YYYY-MM-DD

#### Added
- New features added to the project

#### Changed
- Changes to existing functionality

#### Deprecated
- Features that will be removed in future versions

#### Removed
- Features that have been removed

#### Fixed
- Bug fixes

#### Security
- Security vulnerability fixes

---

## Version History

- **v1.0.0** (2026-01-10): Initial public release with complete system implementation
- **v0.x.x** (Pre-release): Internal development and validation

---

## Future Releases

### Planned for v1.1.0
- FPGA emulation support
- Extended workload traces (encoder-decoder models)
- Enhanced visualization tools
- Docker containerization
- Additional memory technology models

### Planned for v2.0.0
- RTL implementation of compute tiles
- Hardware validation results
- Extended quantization support (INT2, FP8)
- Dynamic voltage/frequency scaling
- Advanced prefetching policies

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this changelog.

When submitting a pull request, please add your changes to the "Unreleased" section.

---

## Links

- [GitHub Repository](https://github.com/ChessEngineUS/Janus-1)
- [Google Colab Notebook](https://colab.research.google.com/github/ChessEngineUS/Janus-1/blob/main/Janus_1_Complete_Analysis.ipynb)
- [Issues](https://github.com/ChessEngineUS/Janus-1/issues)
- [Discussions](https://github.com/ChessEngineUS/Janus-1/discussions)

---

**Note**: Versions prior to 1.0.0 were internal development releases and are not documented here.
