#!/bin/bash
# Setup development environment for Janus-1
# Run with: bash scripts/setup_dev.sh

set -e

echo "======================================"
echo "Janus-1 Development Setup"
echo "======================================"
echo ""

echo "[1/5] Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

if ! python -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "Error: Python 3.9 or higher is required"
    exit 1
fi
echo "✓ Python version OK"
echo ""

echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping..."
else
    python -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

echo "[3/5] Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "✓ Virtual environment activated"
echo ""

echo "[4/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo "✓ Dependencies installed"
echo ""

echo "[5/5] Installing pre-commit hooks..."
pip install pre-commit
pre-commit install
echo "✓ Pre-commit hooks installed"
echo ""

echo "======================================"
echo "✓ Development environment ready!"
echo "======================================"
echo ""
echo "To activate the virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "  source venv/Scripts/activate"
else
    echo "  source venv/bin/activate"
fi
echo ""
echo "To run tests:"
echo "  bash scripts/run_tests.sh"
echo ""
echo "To reproduce paper results:"
echo "  bash scripts/reproduce_paper.sh"
echo ""
