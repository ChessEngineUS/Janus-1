#!/bin/bash
# Run comprehensive test suite with coverage
# Run with: bash scripts/run_tests.sh

set -e

echo "======================================"
echo "Janus-1 Test Suite"
echo "======================================"
echo ""

echo "[1/5] Running unit tests..."
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
echo "✓ Unit tests complete"
echo ""

echo "[2/5] Checking code formatting (black)..."
black --check src tests || {
    echo "⚠ Code formatting issues found. Run 'black src tests' to fix."
}
echo "✓ Code formatting check complete"
echo ""

echo "[3/5] Running linter (flake8)..."
flake8 src tests --max-line-length=88 --extend-ignore=E203,W503 --statistics || {
    echo "⚠ Linting issues found. Review the output above."
}
echo "✓ Linting complete"
echo ""

echo "[4/5] Running type checker (mypy)..."
mypy src --ignore-missing-imports || {
    echo "⚠ Type checking issues found. Review the output above."
}
echo "✓ Type checking complete"
echo ""

echo "[5/5] Checking import sorting (isort)..."
isort --check-only src tests || {
    echo "⚠ Import sorting issues found. Run 'isort src tests' to fix."
}
echo "✓ Import sorting check complete"
echo ""

echo "======================================"
echo "✓ All checks complete!"
echo "======================================"
echo ""
echo "Coverage report: htmlcov/index.html"
echo ""
