# Janus-1 Utility Scripts

This directory contains utility scripts for development, testing, and reproduction of results.

## Scripts Overview

### Development Setup

#### `setup_dev_env.sh`

Sets up a complete development environment with all dependencies.

**Usage:**
```bash
bash scripts/setup_dev_env.sh
```

**What it does:**
- Checks Python version (3.9+ required)
- Creates virtual environment
- Installs production dependencies
- Installs development dependencies
- Sets up pre-commit hooks
- Runs verification tests
- Creates necessary directories

**Requirements:**
- Python 3.9+
- pip
- git

---

### Testing

#### `run_quick_test.sh`

Runs a fast validation suite for quick checks during development.

**Usage:**
```bash
bash scripts/run_quick_test.sh
```

**What it includes:**
1. Unit tests (fast tests only)
2. Code formatting check (Black)
3. Linting (flake8)
4. Quick simulation validation

**Duration:** ~30 seconds

**Use case:** Run before committing code

---

### Paper Reproduction

#### `reproduce_paper.sh`

Reproduces all results from the Janus-1 paper.

**Usage:**
```bash
bash scripts/reproduce_paper.sh
```

**What it does:**
1. Verifies dependencies
2. Runs all experiments:
   - KV-cache analysis
   - Memory technology comparison
   - Memory hierarchy simulation
   - Prefetcher optimization
   - Thermal analysis
   - Full system evaluation
3. Generates all figures
4. Creates summary report

**Duration:** ~5-10 minutes

**Output:**
- `results/paper_reproduction_YYYYMMDD_HHMMSS/`
  - `data/` - CSV/JSON data files
  - `figures/` - Publication-quality figures
  - `REPRODUCTION_REPORT.txt` - Summary

**Use case:** Verify reproducibility, generate paper figures

---

## Cross-Platform Usage

### Linux / macOS

```bash
# Make scripts executable (first time only)
chmod +x scripts/*.sh

# Run scripts
bash scripts/setup_dev_env.sh
bash scripts/run_quick_test.sh
bash scripts/reproduce_paper.sh
```

### Windows (Git Bash)

```bash
bash scripts/setup_dev_env.sh
bash scripts/run_quick_test.sh
bash scripts/reproduce_paper.sh
```

### Windows (PowerShell)

Use the Python launcher scripts:

```powershell
python scripts/setup_dev.py
python scripts/quick_test.py
python scripts/reproduce_paper.py
```

---

## Python Launcher Scripts

For better cross-platform compatibility, Python versions of the scripts are available:

- `setup_dev.py` - Development setup
- `quick_test.py` - Quick validation
- `reproduce_paper.py` - Paper reproduction

These work identically to the shell scripts but use Python instead of Bash.

---

## Continuous Integration

These scripts are also used in CI/CD:

- **GitHub Actions**: Uses `reproduce_paper.sh` for validation
- **Pre-commit**: Uses `run_quick_test.sh` hooks

---

## Troubleshooting

### "Permission denied" error

```bash
chmod +x scripts/*.sh
```

### "python3: command not found"

Make sure Python 3.9+ is installed and in your PATH.

### Virtual environment issues

Delete and recreate:
```bash
rm -rf venv
bash scripts/setup_dev_env.sh
```

### Tests failing

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

## Adding New Scripts

When adding new scripts:

1. **Shell scripts** (`.sh`):
   - Add shebang: `#!/bin/bash`
   - Use `set -e` for error handling
   - Add descriptive comments
   - Make executable: `chmod +x script.sh`

2. **Python scripts** (`.py`):
   - Add shebang: `#!/usr/bin/env python3`
   - Use argparse for CLI arguments
   - Add docstrings
   - Handle cross-platform paths

3. **Documentation**:
   - Add section to this README
   - Include usage examples
   - Document expected output

---

## Examples

### Complete Development Workflow

```bash
# 1. Setup (first time only)
bash scripts/setup_dev_env.sh

# 2. Activate environment
source venv/bin/activate

# 3. Make changes to code
vim src/simulator/janus_sim.py

# 4. Quick validation
bash scripts/run_quick_test.sh

# 5. Full reproduction (before submitting PR)
bash scripts/reproduce_paper.sh

# 6. Commit and push
git add -A
git commit -m "Your changes"
git push
```

### Quick Iteration Cycle

```bash
# Edit code
vim src/models/memory_power_model.py

# Format
black src/models/memory_power_model.py

# Test
pytest tests/test_models.py -v

# Quick check
bash scripts/run_quick_test.sh
```

### Paper Submission Workflow

```bash
# Generate all results
bash scripts/reproduce_paper.sh

# Review outputs
ls -lh results/paper_reproduction_*/figures/

# Create archive for submission
zip -r paper_results.zip results/paper_reproduction_*/

# Verify archive
unzip -l paper_results.zip
```

---

## Script Dependencies

### Required

- Python 3.9+
- pip
- git

### Optional

- GNU Make (for Makefile targets)
- Docker (for containerized reproduction)
- pre-commit (installed by setup script)

---

## Related Documentation

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines
- [README.md](../README.md) - Project overview
- [docs/](../docs/) - Technical documentation

---

## Questions?

If you have questions about these scripts:

- Check [CONTRIBUTING.md](../CONTRIBUTING.md)
- Open an issue: https://github.com/ChessEngineUS/Janus-1/issues
- Start a discussion: https://github.com/ChessEngineUS/Janus-1/discussions

---

**Last Updated:** January 10, 2026  
**Maintainer:** Tommaso Marena (@ChessEngineUS)
