# Makefile for Janus-1
# Provides convenient shortcuts for common development tasks

.PHONY: help install install-dev test test-fast test-cov clean format lint type-check pre-commit reproduce docs docker-build docker-run

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Janus-1 Development Makefile"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Example usage:"
	@echo "  make install-dev    # Install development dependencies"
	@echo "  make test          # Run all tests"
	@echo "  make format        # Format code with Black"
	@echo ""

install: ## Install production dependencies
	pip install -r requirements.txt
	pip install -e .

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install
	@echo "✓ Development environment ready"

test: ## Run all tests
	pytest tests/ -v

test-fast: ## Run fast tests only (skip slow/integration tests)
	pytest tests/ -v -m "not slow"

test-cov: ## Run tests with coverage report
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo ""
	@echo "Coverage report: htmlcov/index.html"

clean: ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned up generated files"

format: ## Format code with Black and isort
	black src tests experiments
	isort src tests experiments
	@echo "✓ Code formatted"

lint: ## Run linting checks
	flake8 src tests --max-line-length=88 --extend-ignore=E203,W503
	@echo "✓ Linting passed"

type-check: ## Run type checking with mypy
	mypy src --ignore-missing-imports
	@echo "✓ Type checking passed"

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

reproduce: ## Reproduce paper results
	bash scripts/reproduce_paper.sh

quick-test: ## Run quick validation
	bash scripts/run_quick_test.sh

docs: ## Generate documentation
	@echo "Documentation generation not yet implemented"
	@echo "See docs/ directory for existing documentation"

check: format lint type-check test-fast ## Run all code quality checks
	@echo ""
	@echo "====================================================================="
	@echo "All checks passed! ✓"
	@echo "====================================================================="

ci: ## Run CI pipeline locally
	@echo "Running CI checks..."
	@make format
	@make lint
	@make type-check
	@make test
	@echo ""
	@echo "====================================================================="
	@echo "CI checks complete! ✓"
	@echo "====================================================================="

docker-build: ## Build Docker image (if Dockerfile exists)
	@if [ -f Dockerfile ]; then \
		docker build -t janus-1:latest .; \
	else \
		echo "Dockerfile not found"; \
	fi

docker-run: ## Run in Docker container
	@if [ -f Dockerfile ]; then \
		docker run -it --rm -v $(PWD):/workspace janus-1:latest; \
	else \
		echo "Dockerfile not found"; \
	fi

setup: install-dev ## Alias for install-dev
	@echo "✓ Setup complete"

all: clean install-dev test ## Clean, install, and test everything
	@echo ""
	@echo "====================================================================="
	@echo "Complete build finished! ✓"
	@echo "====================================================================="
