# Makefile for Kubli encryption/decryption project
.PHONY: help install test test-unit test-integration test-samples clean coverage lint format

# Default target
help:
	@echo "Kubli Project Makefile"
	@echo "Available targets:"
	@echo "  help           - Show this help message"
	@echo "  install        - Install dependencies"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-samples   - Run sample file tests only"
	@echo "  coverage       - Run tests with coverage report"
	@echo "  clean          - Clean up generated files"
	@echo "  lint           - Run linting (if flake8 is available)"
	@echo "  format         - Format code (if black is available)"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Run all tests
test:
	@echo "Running all tests..."
	python run_tests.py

# Run unit tests only
test-unit:
	@echo "Running unit tests..."
	python run_tests.py --unit

# Run integration tests only
test-integration:
	@echo "Running integration tests..."
	python run_tests.py --integration

# Run sample file tests only
test-samples:
	@echo "Running sample file tests..."
	python run_tests.py --file test_sample_files

# Run tests with coverage
coverage:
	@echo "Running tests with coverage..."
	python run_tests.py
	@echo "Coverage report generated in coverage_html/index.html"

# Clean up generated files
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	rm -rf utils/__pycache__/
	rm -rf .pytest_cache/
	rm -rf coverage_html/
	rm -rf .coverage
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "Cleanup complete!"

# Run linting (optional)
lint:
	@echo "Running linting..."
	@command -v flake8 >/dev/null 2>&1 && flake8 kubli.py utils/ tests/ || echo "flake8 not found, skipping linting"

# Format code (optional)
format:
	@echo "Formatting code..."
	@command -v black >/dev/null 2>&1 && black kubli.py utils/ tests/ || echo "black not found, skipping formatting"
