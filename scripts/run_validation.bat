@echo off
REM Run complete Janus-1 validation suite (Windows)
REM Executes all tests with coverage reporting

echo ========================================
echo Janus-1 Comprehensive Validation Suite
echo ========================================
echo.

REM Check if pytest is installed
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo Error: pytest not installed
    echo Install with: pip install pytest pytest-cov
    exit /b 1
)

echo [1/6] Running Memory Hierarchy Tests...
python -m pytest tests/test_memory_hierarchy.py -v --tb=short
if errorlevel 1 (
    echo Memory Hierarchy Tests FAILED
    exit /b 1
)
echo Memory Hierarchy Tests PASSED
echo.

echo [2/6] Running Trace Generator Tests...
python -m pytest tests/test_trace_generator.py -v --tb=short
if errorlevel 1 (
    echo Trace Generator Tests FAILED
    exit /b 1
)
echo Trace Generator Tests PASSED
echo.

echo [3/6] Running Integration Tests...
python -m pytest tests/test_integration.py -v --tb=short
if errorlevel 1 (
    echo Integration Tests FAILED
    exit /b 1
)
echo Integration Tests PASSED
echo.

echo [4/6] Running Benchmark Tests...
python -m pytest tests/test_benchmarks.py -v --tb=short
if errorlevel 1 (
    echo Benchmark Tests FAILED
    exit /b 1
)
echo Benchmark Tests PASSED
echo.

echo [5/6] Running Model Tests...
python -m pytest tests/test_models.py -v --tb=short
echo.

echo [6/6] Generating Coverage Report...
python -m pytest tests/ --cov=src --cov-report=term --cov-report=html --tb=short
echo Coverage Report Generated
echo View detailed report: htmlcov/index.html
echo.

echo ========================================
echo All Validation Tests Completed!
echo ========================================
echo.
echo Summary:
echo   - Memory hierarchy tests: PASSED
echo   - Trace generator tests: PASSED
echo   - Integration tests: PASSED
echo   - Benchmark tests: PASSED
echo   - Coverage report: Generated
echo.