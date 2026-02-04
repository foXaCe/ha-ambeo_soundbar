.PHONY: help install lint format check test clean pre-commit pre-commit-update security

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install development dependencies"
	@echo "  make pre-commit       - Install pre-commit hooks"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             - Run Ruff linter"
	@echo "  make format           - Format code with Ruff"
	@echo "  make fix              - Auto-fix all linting issues"
	@echo "  make check            - Run linter + formatter check (CI mode)"
	@echo "  make qa               - Quick QA (clean + fix + check)"
	@echo ""
	@echo "Pre-commit:"
	@echo "  make pre-commit-run   - Run all pre-commit hooks (17 hooks)"
	@echo "  make pre-commit-update - Update pre-commit hook versions"
	@echo ""
	@echo "Type Checking:"
	@echo "  make type-check       - Run mypy type checker"
	@echo ""
	@echo "Security:"
	@echo "  make security         - Run security scans (Bandit)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove cache and build files"
	@echo "  make test             - Run tests (if available)"

# Install development dependencies
install:
	@echo "Installing development dependencies..."
	pip install --upgrade pip
	pip install -r requirements-dev.txt
	@echo "✓ Dependencies installed"

# Run Ruff linter
lint:
	@echo "Running Ruff linter..."
	ruff check .

# Format code with Ruff
format:
	@echo "Formatting code with Ruff..."
	ruff format .
	@echo "✓ Code formatted"

# Check code (lint + format check) - CI mode
check:
	@echo "Running code quality checks..."
	ruff check .
	ruff format --check .
	@echo "✓ All checks passed"

# Auto-fix linting issues
fix:
	@echo "Auto-fixing linting issues..."
	ruff check --fix .
	ruff format .
	@echo "✓ Auto-fixes applied"

# Install pre-commit hooks
pre-commit:
	@echo "Installing pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	@echo "✓ Pre-commit hooks installed"

# Run all pre-commit hooks
pre-commit-run:
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files

# Update pre-commit hook versions
pre-commit-update:
	@echo "Updating pre-commit hook versions..."
	pre-commit autoupdate
	@echo "✓ Pre-commit hooks updated"

# Run security scans
security:
	@echo "Running security scans..."
	bandit -c pyproject.toml -r custom_components/ambeo_soundbar
	@echo "✓ Security scan complete"

# Type checking with mypy
type-check:
	@echo "Running type checks..."
	mypy custom_components/ambeo_soundbar --ignore-missing-imports --no-strict-optional || true

# Run tests (placeholder for future tests)
test:
	@echo "No tests configured yet"
	@echo "Consider adding pytest for unit tests"

# Clean cache and build files
clean:
	@echo "Cleaning cache and build files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"

# Quick quality check before commit
qa: clean fix check
	@echo "✓ Quality assurance complete"
