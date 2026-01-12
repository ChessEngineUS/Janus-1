# Janus-1 Development Roadmap

This document outlines the development timeline, milestones, and future plans for the Janus-1 project.

## Current Status: v1.0 (Research Prototype)

✅ **Completed**:
- Cycle-accurate memory hierarchy simulator
- KV-cache sizing and memory technology models
- INT4 quantization validation on Llama-2 7B
- Janus-Prefetch-1 FSM design and evaluation
- Power, performance, and area (PPA) analysis
- Publication-ready Jupyter notebook
- Comprehensive documentation

---

## Phase 1: Software Refinement (Q1 2026)

### v1.1 - Enhanced Simulator (January 2026)
**Status**: 🔄 In Progress

- [ ] Add support for variable batch sizes
- [ ] Implement encoder-decoder model traces
- [ ] Add visualization dashboard for real-time simulation
- [ ] Optimize simulator performance (10× speedup target)
- [ ] Add profiling hooks for external model integration

**Deliverables**:
- Simulator v1.1 release
- Performance benchmarking report
- Updated API documentation

### v1.2 - Extended Workloads (February 2026)
**Status**: 📋 Planned

- [ ] Integrate with Hugging Face Transformers
- [ ] Real trace collection from vLLM inference
- [ ] Support for vision transformers (ViT)
- [ ] Multi-modal model traces (CLIP, Flamingo)
- [ ] Benchmark suite with 10+ model architectures

**Deliverables**:
- Workload trace library
- Comparative analysis report
- Integration guide for custom models

### v1.3 - Advanced Prefetching (March 2026)
**Status**: 📋 Planned

- [ ] Neural prefetcher (learned patterns)
- [ ] Hybrid stream + stride prefetcher
- [ ] Context-aware prefetching (prefill vs. generation)
- [ ] Comparative study: FSM vs. ML-based prefetchers
- [ ] Gate-level synthesis of prefetcher variants

**Deliverables**:
- Prefetcher design space exploration
- Hardware cost comparison (area, power)
- Publication: "Neural Prefetching for LLM Inference"

---

## Phase 2: Hardware Prototyping (Q2-Q3 2026)

### v2.0 - RTL Implementation (April-June 2026)
**Status**: 📋 Planned

**Goals**:
- Complete Verilog/SystemVerilog RTL for Janus-1 core
- Functional verification with UVM testbenches
- Gate-level synthesis targeting 3nm library

**Tasks**:
- [ ] RTL design of compute tile (systolic array)
- [ ] Memory controller for T1 SRAM
- [ ] eDRAM controller with refresh logic
- [ ] Janus-Prefetch-1 RTL implementation
- [ ] 2D mesh NoC (network-on-chip)
- [ ] Top-level SoC integration
- [ ] UVM testbench for full-chip verification
- [ ] Synthesis with commercial EDA tools (Synopsys, Cadence)
- [ ] Static timing analysis (STA)
- [ ] Power analysis (PrimeTime PX)

**Deliverables**:
- Synthesizable RTL (open-source)
- Verification report (code coverage >95%)
- PPA estimates from synthesis
- Technical report: "Janus-1 RTL Design"

**Challenges**:
- eDRAM modeling (may require foundry partnership)
- Timing closure at 2 GHz target frequency
- Power optimization under 4W constraint

### v2.1 - FPGA Emulation (July-September 2026)
**Status**: 📋 Planned

**Goals**:
- Validate Janus-1 functionality on FPGA before tape-out
- Measure real-world performance with live LLM inference

**Platform**: Xilinx Versal ACAP or Intel Stratix 10

**Tasks**:
- [ ] Port RTL to FPGA (replace eDRAM with BRAM + latency delay)
- [ ] Integrate with RISC-V host processor
- [ ] Implement PCIe interface for host communication
- [ ] Run Llama-2 7B INT4 inference on FPGA
- [ ] Measure achieved throughput (tokens/sec)
- [ ] Validate hit rate on real workloads
- [ ] Power measurement with onboard sensors

**Deliverables**:
- FPGA bitstream (open-source)
- Integration guide for FPGA platforms
- Performance validation report
- Demo: Live LLM chatbot on FPGA

**Metrics**:
- Target: >10 tokens/sec @ 4W (Llama-2 7B)
- Memory hit rate: >99%
- End-to-end latency: <100ms per token

---

## Phase 3: Silicon Validation (Q4 2026 - Q2 2027)

### v3.0 - Tape-Out Preparation (October-December 2026)
**Status**: 📋 Planned

**Goals**:
- Prepare design for multi-project wafer (MPW) tape-out
- Complete physical design and verification

**Tasks**:
- [ ] Floorplanning (32 MB SRAM + 224 MB eDRAM layout)
- [ ] Place & Route (P&R) with commercial tools
- [ ] Design Rule Check (DRC)
- [ ] Layout Versus Schematic (LVS)
- [ ] IR drop analysis
- [ ] Electromigration (EM) analysis
- [ ] Sign-off timing analysis
- [ ] Parasitic extraction (post-layout simulation)
- [ ] Generate GDSII for foundry submission

**Deliverables**:
- GDSII tape-out ready layout
- Signoff reports (DRC, LVS, STA)
- Final PPA numbers
- Tape-out application to foundry MPW program

**Challenges**:
- Securing eDRAM process access (may require foundry partnership or alternative)
- Meeting area constraint (~79 mm²)
- Multi-Vt cell library optimization

**Budget**: ~$50K-$100K (academic MPW program)

### v3.1 - Silicon Bring-Up (Q1 2027)
**Status**: 📋 Planned

**Goals**:
- Receive fabricated chips from foundry
- Validate functionality and performance on silicon

**Tasks**:
- [ ] PCB design for chip testing
- [ ] Chip bring-up (power-on, clock, reset)
- [ ] JTAG boundary scan testing
- [ ] Memory BIST (built-in self-test)
- [ ] Functional validation with test patterns
- [ ] Run Llama-2 7B inference on chip
- [ ] Measure power (active, idle)
- [ ] Measure performance (tokens/sec, latency)
- [ ] Thermal imaging under load

**Deliverables**:
- Silicon validation report
- Measured vs. simulated PPA comparison
- Demo: Live inference on Janus-1 chip
- Publication: "Janus-1: A 3nm Edge AI Processor" (ISSCC/ISCA submission)

**Success Criteria**:
- Functional chip: >90% of compute tiles operational
- Performance: >5 tokens/sec (Llama-2 7B INT4)
- Power: <5W measured
- Temperature: <90°C @ 25°C ambient

### v3.2 - Production Refinement (Q2 2027)
**Status**: 📋 Planned

**Goals**:
- Iterate on design based on silicon learnings
- Optimize for commercial viability

**Tasks**:
- [ ] Analyze silicon bugs and design flaws
- [ ] Re-spin design with fixes (optional)
- [ ] Yield analysis
- [ ] Cost modeling for commercial production
- [ ] Explore licensing opportunities

---

## Phase 4: Ecosystem Development (2027+)

### Software Stack
**Status**: 📋 Future Work

- [ ] Custom compiler for INT4 code generation
- [ ] Runtime scheduler for multi-model inference
- [ ] Integration with ONNX, TensorFlow Lite
- [ ] Device drivers for Linux/Android
- [ ] SDK and developer documentation

### Extended Architectures
**Status**: 📋 Future Work

- [ ] Janus-2: Multi-chip design for 70B+ models
- [ ] Chiplet-based architecture (UCIe interconnect)
- [ ] Heterogeneous 3-tier memory (SRAM + eDRAM + MRAM)
- [ ] Janus-Vision: Optimized for vision transformers
- [ ] Janus-Multi: Multi-modal AI accelerator

### Applications
**Status**: 📋 Future Work

- [ ] Edge chatbot device (consumer product)
- [ ] On-device translation (speech + text)
- [ ] Real-time video understanding
- [ ] Robotics (vision + language grounding)
- [ ] Wearable AI assistant

---

## Research Publications

### Submitted/In Preparation

1. **Janus-1: A Systems-Level Design Methodology for Real-Time Generative AI at the Edge**
   - Status: arXiv preprint (January 2026)
   - Target: ISCA 2026 or MICRO 2026

2. **Janus-Prefetch-1: FSM-Based Prefetching for Transformer Inference**
   - Status: In preparation
   - Target: HPCA 2027

3. **Co-Designing Memory Hierarchies for Edge LLM Inference**
   - Status: Planned (Q2 2026)
   - Target: IEEE Micro or ACM TACO

### Future Publications

4. **Silicon Validation of Janus-1: A 3nm Edge AI Processor** (2027)
5. **Janus-2: Scaling to 70B Parameters with Chiplets" (2027)
6. **Neural Prefetching for Large Language Models" (2027)

---

## Community Engagement

### Open-Source Contributions
**Current**:
- ✅ Simulator code (MIT license)
- ✅ Jupyter notebook for analysis
- ✅ Documentation and examples

**Planned**:
- [ ] RTL code (v2.0, Apache 2.0 license)
- [ ] FPGA reference design (v2.1)
- [ ] Workload trace library (v1.2)
- [ ] Compiler and runtime (v4.0)

### Collaboration Opportunities

**Academic Partnerships**:
- Looking for: FPGA emulation expertise (Xilinx/Intel)
- Looking for: Foundry connections for eDRAM access
- Looking for: LLM optimization researchers

**Industry Partnerships**:
- Looking for: Potential licensing/commercialization
- Looking for: Edge device manufacturers
- Looking for: AI software framework developers

**How to Contribute**:
- See [CONTRIBUTING.md](CONTRIBUTING.md)
- Join discussions on GitHub Discussions
- Submit issues for bugs or feature requests
- Propose pull requests for improvements

---

## Milestones Summary

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| v1.0 Research Prototype | ✅ January 2026 | Complete |
| v1.1 Enhanced Simulator | February 2026 | In Progress |
| v1.2 Extended Workloads | March 2026 | Planned |
| v1.3 Advanced Prefetching | April 2026 | Planned |
| v2.0 RTL Implementation | June 2026 | Planned |
| v2.1 FPGA Emulation | September 2026 | Planned |
| v3.0 Tape-Out | December 2026 | Planned |
| v3.1 Silicon Validation | March 2027 | Planned |
| v3.2 Production Refinement | June 2027 | Planned |

---

## Risks and Mitigation

### Technical Risks

1. **eDRAM process availability**
   - Risk: 3nm GAA may not support eDRAM
   - Mitigation: Explore MRAM alternative or foundry partnership
   - Contingency: Use 5nm/7nm FinFET with proven eDRAM

2. **Timing closure at 2 GHz**
   - Risk: Complex design may not meet frequency target
   - Mitigation: Early synthesis iterations, physical-aware RTL
   - Contingency: Reduce frequency to 1.5 GHz (still meets perf target)

3. **Quantization accuracy for new models**
   - Risk: INT4 may degrade accuracy for future models
   - Mitigation: Hybrid INT4/INT8 support, adaptive quantization
   - Contingency: Increase eDRAM to 448 MB for INT8 fallback

### Resource Risks

4. **Funding for tape-out**
   - Risk: MPW programs competitive, may not secure slot
   - Mitigation: Apply to multiple foundries (TSMC, Samsung, Intel)
   - Contingency: Industry partnership or crowdfunding

5. **EDA tool access**
   - Risk: Commercial tools expensive for academic/independent research
   - Mitigation: University partnerships, open-source EDA (OpenROAD)
   - Contingency: Focus on FPGA validation only

---

## Long-Term Vision (2028+)

### Janus Processor Family

- **Janus-1**: 7B models, <5W (2026)
- **Janus-2**: 13-70B models, <15W, multi-chip (2027)
- **Janus-Vision**: Vision transformers, video understanding (2028)
- **Janus-Multi**: Multi-modal (vision + language + audio) (2028)
- **Janus-Cloud**: Scaled-up version for edge servers (2029)

### Impact Goals

1. **Enable billion-parameter models on battery-powered devices**
2. **Democratize edge AI hardware research** (open-source tools)
3. **Establish new co-design methodologies** (algorithm + architecture + technology)
4. **Publish in top-tier venues** (ISCA, MICRO, ISSCC)
5. **Commercial deployment** (license to industry or startup)

---

*This roadmap is a living document and subject to change based on research progress and community feedback.*

**Last Updated**: January 12, 2026

**Maintainer**: Janus-1 Research Team (@ChessEngineUS)
