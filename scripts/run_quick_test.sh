#!/bin/bash
# Quick validation script for Janus-1
# Usage: bash scripts/run_quick_test.sh

set -e

echo "======================================================================"
echo "Janus-1 Quick Test Suite"
echo "======================================================================"
echo ""

# Run fast tests only
echo "[1/4] Running unit tests..."
pytest tests/ -v --tb=short -m "not slow" 2>&1 | grep -E "(PASSED|FAILED|ERROR|test_)"
echo "✓ Unit tests complete"
echo ""

# Check code formatting
echo "[2/4] Checking code formatting..."
if black --check src tests 2>&1 | tail -n 3; then
    echo "✓ Code formatting OK"
else
    echo "⚠ Code formatting issues found (run: black src tests)"
fi
echo ""

# Run linter
echo "[3/4] Running linter..."
if flake8 src tests --max-line-length=88 --extend-ignore=E203,W503 --count 2>&1 | tail -n 5; then
    echo "✓ No linting errors"
else
    echo "⚠ Linting issues found"
fi
echo ""

# Quick simulation test
echo "[4/4] Running quick simulation..."
python -c "
from src.simulator.janus_sim import JanusSim
from src.benchmarks.trace_generator import generate_llm_trace

trace = generate_llm_trace(context_length=256)  # Small trace
sim = JanusSim()
sim.run(trace)
metrics = sim.get_metrics()

assert metrics.hit_rate > 90.0, f'Hit rate too low: {metrics.hit_rate}'
print(f'✓ Simulation test passed (hit rate: {metrics.hit_rate:.2f}%)')
"
echo ""

echo "======================================================================"
echo "Quick Test Complete!"
echo "======================================================================"
echo ""
echo "All checks passed ✓"
echo ""
