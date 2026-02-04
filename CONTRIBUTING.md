# Contributing to HA AMBEO Soundbar

Thank you for your interest in contributing to the AMBEO Soundbar Home Assistant integration!

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Home Assistant development environment (optional but recommended)

### Getting Started

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/ha-ambeo_soundbar.git
cd ha-ambeo_soundbar
```

2. **Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install development dependencies**

```bash
make install
# or manually:
pip install -r requirements-dev.txt
```

4. **Install pre-commit hooks**

```bash
make pre-commit
# or manually:
pre-commit install
```

## Code Quality Tools

This project uses several tools to maintain code quality:

### Ruff (Linter & Formatter)

Ruff is our primary linting and formatting tool. It's fast and comprehensive.

```bash
# Run linter
make lint
# or: ruff check .

# Auto-fix issues
make fix
# or: ruff check --fix .

# Format code
make format
# or: ruff format .

# Check everything (CI mode)
make check
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit to ensure code quality.

```bash
# Run all hooks manually
make pre-commit-run
# or: pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

The hooks include:
- Ruff linting and formatting
- YAML/JSON validation
- Trailing whitespace removal
- Security checks (bandit)
- Spell checking (codespell)

### Type Checking

We use mypy for optional type checking:

```bash
make type-check
# or: mypy custom_components/ambeo_soundbar --ignore-missing-imports
```

## Code Style Guidelines

### General Principles

1. **Follow Home Assistant conventions**
   - Use `async_*` prefix for async functions
   - Follow HA entity naming patterns
   - Use proper HA logging

2. **Python Style**
   - Line length: 88 characters (Black/Ruff default)
   - Use double quotes for strings
   - Use type hints where appropriate
   - Write docstrings for public functions

3. **Imports**
   - Organize imports with isort (handled by Ruff)
   - Group: standard library, third-party, local

### Example

```python
"""Example module docstring."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the media player platform.

    Args:
        hass: Home Assistant instance
        entry: Config entry
        async_add_entities: Callback to add entities
    """
    # Implementation
    pass
```

## Testing

### Manual Testing

1. Install the integration in a Home Assistant instance
2. Test with actual AMBEO soundbar hardware
3. Verify all entity states update correctly

### Future: Automated Testing

We plan to add pytest-based unit tests. Contributions welcome!

```bash
# Run tests (when available)
make test
```

## Workflow

### Making Changes

1. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
   - Write clean, documented code
   - Follow code style guidelines
   - Test your changes

3. **Commit your changes**

Pre-commit hooks will automatically run. Fix any issues before committing.

```bash
git add .
git commit -m "Add feature: description"
```

4. **Push and create a pull request**

```bash
git push origin feature/your-feature-name
```

### Commit Messages

Use clear, descriptive commit messages:

```
Add support for subwoofer volume control

- Implement number entity for dB level adjustment
- Add capability detection for Max models
- Update documentation
```

## Pull Request Process

1. Ensure all pre-commit hooks pass
2. Update documentation if needed
3. Describe your changes clearly in the PR
4. Link any related issues
5. Wait for review and address feedback

## CI/CD

Our GitHub Actions workflows will automatically:
- Run Ruff linting and formatting checks
- Run pre-commit hooks
- Validate YAML/JSON files
- Check for security issues

Make sure all checks pass before requesting review.

## Quick Reference

```bash
# Common commands
make help              # Show all available commands
make install           # Install dev dependencies
make lint              # Run linter
make format            # Format code
make fix               # Auto-fix issues
make check             # Run all checks (CI mode)
make clean             # Clean cache files
make qa                # Quick QA: clean + fix + check

# Pre-commit
make pre-commit        # Install hooks
make pre-commit-run    # Run all hooks

# Development
python -m venv .venv   # Create virtual env
source .venv/bin/activate  # Activate (Linux/Mac)
.venv\Scripts\activate     # Activate (Windows)
```

## VS Code Setup

If using VS Code, the repository includes configuration for:
- Automatic formatting on save
- Ruff integration
- Recommended extensions

Install recommended extensions when prompted.

## Questions?

- Open an issue for bugs or feature requests
- Check existing issues and PRs first
- Be respectful and constructive

Thank you for contributing!
