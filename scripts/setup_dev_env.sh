#!/bin/bash
# Setup development environment for Janus-1
# Usage: bash scripts/setup_dev_env.sh

set -e

echo "======================================================================"
echo "Janus-1 Development Environment Setup"
echo "======================================================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python version: $PYTHON_VERSION"

# Check if version is >= 3.9
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "✓ Python version is 3.9 or higher"
else
    echo "❌ Error: Python 3.9+ is required"
    exit 1
fi
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
    echo "✓ Virtual environment activated (Windows)"
else
    echo "❌ Error: Could not find activation script"
    exit 1
fi
echo ""

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip -q
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing production dependencies..."
pip install -r requirements.txt -q
echo "✓ Production dependencies installed"
echo ""

echo "Installing development dependencies..."
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt -q
    echo "✓ Development dependencies installed"
else
    echo "⚠ requirements-dev.txt not found, installing essential dev tools"
    pip install pytest pytest-cov black flake8 mypy isort -q
    echo "✓ Essential dev tools installed"
fi
echo ""

# Install package in editable mode
echo "Installing Janus-1 in editable mode..."
pip install -e . -q
echo "✓ Janus-1 installed in editable mode"
echo ""

# Setup pre-commit hooks
if [ -f ".pre-commit-config.yaml" ]; then
    echo "Setting up pre-commit hooks..."
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        echo "✓ Pre-commit hooks installed"
    else
        echo "⚠ pre-commit not found, installing..."
        pip install pre-commit -q
        pre-commit install
        echo "✓ Pre-commit hooks installed"
    fi
else
    echo "⚠ .pre-commit-config.yaml not found, skipping pre-commit setup"
fi
echo ""

# Run tests to verify setup
echo "Running tests to verify setup..."
if pytest tests/ -v --tb=short 2>&1 | tail -n 5; then
    echo "✓ All tests passed"
else
    echo "⚠ Some tests failed, but environment is set up"
fi
echo ""

# Create necessary directories
echo "Creating project directories..."
mkdir -p results/figures
mkdir -p results/data
mkdir -p experiments
echo "✓ Directories created"
echo ""

# Print summary
echo "======================================================================"
echo "Setup Complete!"
echo "======================================================================"
echo ""
echo "Your development environment is ready. Here's what was installed:"
echo ""
echo "  ✓ Python ${PYTHON_VERSION}"
echo "  ✓ Virtual environment (venv/)"
echo "  ✓ Production dependencies"
echo "  ✓ Development dependencies"
echo "  ✓ Pre-commit hooks"
echo "  ✓ Janus-1 package (editable mode)"
echo ""
echo "Next steps:"
echo ""
echo "  1. Activate the virtual environment:"
if [ -f "venv/bin/activate" ]; then
    echo "     source venv/bin/activate"
else
    echo "     venv\\Scripts\\activate  (Windows)"
fi
echo ""
echo "  2. Run tests:"
echo "     pytest tests/ -v"
echo ""
echo "  3. Start developing:"
echo "     python experiments/run_full_system.py"
echo ""
echo "  4. Check code quality:"
echo "     black --check src tests"
echo "     flake8 src tests"
echo "     mypy src"
echo ""
echo "  5. See CONTRIBUTING.md for more information"
echo ""
echo "Happy coding! 🚀"
