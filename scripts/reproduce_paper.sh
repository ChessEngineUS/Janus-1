#!/bin/bash
# Reproduce all results from the Janus-1 paper
# Run with: bash scripts/reproduce_paper.sh

set -e  # Exit on error

echo "======================================"
echo "Janus-1 Paper Reproduction Script"
echo "======================================"
echo ""

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

if ! python -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "Error: Python 3.9 or higher is required"
    exit 1
fi

echo ""
echo "[1/6] Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "[2/6] Running memory technology comparison..."
python experiments/run_memory_sweep.py
echo "✓ Memory sweep complete"

echo ""
echo "[3/6] Running prefetcher optimization..."
python experiments/run_prefetch_sweep.py
echo "✓ Prefetcher sweep complete"

echo ""
echo "[4/6] Running thermal analysis..."
python experiments/run_thermal_analysis.py
echo "✓ Thermal analysis complete"

echo ""
echo "[5/6] Running full system evaluation..."
python experiments/run_full_system.py
echo "✓ Full system evaluation complete"

echo ""
echo "[6/6] Running tests to verify correctness..."
pytest tests/ -v --tb=short
echo "✓ All tests passed"

echo ""
echo "======================================"
echo "✓ Paper reproduction complete!"
echo "======================================"
echo ""
echo "Results saved to: results/"
echo "Figures saved to: results/figures/"
echo "Data saved to: results/data/"
echo ""
echo "To view results, check the results/ directory."
echo "To run individual experiments, see experiments/ folder."
echo ""
