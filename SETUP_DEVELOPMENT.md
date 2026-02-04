# Development Setup Guide

This guide will help you set up your development environment for the AMBEO Soundbar Home Assistant integration.

## Quick Start

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
make install

# 3. Install pre-commit hooks
make pre-commit

# 4. You're ready to code!
```

## Code Quality Commands

### Daily Workflow

```bash
# Before making changes
make clean              # Clean cache files

# While coding (auto-fixes issues)
make fix                # Auto-fix linting issues + format

# Before committing
make check              # Run all checks (what CI will run)
```

### Individual Commands

```bash
make lint               # Run Ruff linter only
make format             # Format code only
make type-check         # Run mypy type checking
make pre-commit-run     # Run all pre-commit hooks
```

### Quick Quality Assurance

```bash
make qa                 # Runs: clean + fix + check
```

## What Gets Checked?

### Ruff Linter (Fast & Comprehensive)
- Code style (PEP 8)
- Import sorting
- Code complexity
- Security issues
- Best practices
- And 50+ other rule categories

### Pre-commit Hooks
- Ruff linting & formatting
- YAML/JSON validation
- Security scanning (bandit)
- Spell checking (codespell)
- Trailing whitespace removal
- End-of-file fixing

### GitHub Actions CI
Every push and PR automatically runs:
- Ruff linting
- Ruff formatting check
- All pre-commit hooks
- Type checking (mypy)

## Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Ruff configuration, project metadata |
| `.pre-commit-config.yaml` | Pre-commit hooks setup |
| `.vscode/settings.json` | VS Code auto-formatting |
| `Makefile` | Convenient commands |
| `requirements-dev.txt` | Development dependencies |

## Editor Setup

### VS Code (Recommended)

1. Install recommended extensions when prompted
2. Settings are pre-configured in `.vscode/settings.json`
3. Code will auto-format on save
4. Linting runs as you type

### Other Editors

Install the Ruff extension/plugin for your editor:
- PyCharm: [Ruff Plugin](https://plugins.jetbrains.com/plugin/20574-ruff)
- Vim/Neovim: [ruff.nvim](https://github.com/mfussenegger/nvim-lint)
- Sublime Text: [LSP-ruff](https://github.com/sublimelsp/LSP-ruff)

## Understanding Errors

### Common Ruff Errors

| Code | Meaning | Fix |
|------|---------|-----|
| `E501` | Line too long | Run `make format` |
| `F401` | Unused import | Remove the import or use it |
| `I001` | Imports unsorted | Run `make fix` |
| `N802` | Function name should be lowercase | Rename function (or ignore for HA patterns) |

### Ignored Rules

Some rules are intentionally disabled in `pyproject.toml` because they conflict with Home Assistant conventions:

- `TRY401` - Verbose logging (HA prefers explicit error messages)
- `TID252` - Relative imports (HA custom components use relative imports)
- `ARG002` - Unused method arguments (needed for interface compatibility)

## Pre-commit Hooks

Pre-commit hooks run automatically before each commit.

### First Time Setup

```bash
make pre-commit
```

### Manual Run

```bash
# Run on all files
make pre-commit-run

# Run on staged files only
git commit -m "your message"  # Hooks run automatically
```

### Bypassing Hooks (Not Recommended)

```bash
git commit --no-verify -m "emergency fix"
```

## CI/CD Pipeline

Our GitHub Actions workflow (`.github/workflows/lint.yaml`) runs on:
- Every push to `master`, `main`, or `dev`
- Every pull request
- Manual trigger

### What CI Checks

1. **Ruff Check** - All linting rules
2. **Ruff Format Check** - Code formatting
3. **Pre-commit** - All hooks
4. **Type Check** - mypy (non-blocking)

## Troubleshooting

### "Command not found: make"

**Linux/Mac:** Install `make` via your package manager
```bash
# Ubuntu/Debian
sudo apt install make

# macOS
xcode-select --install
```

**Windows:** Use Git Bash or WSL, or run commands directly:
```bash
.venv\Scripts\ruff check .
```

### Pre-commit hooks fail

```bash
# Update hooks to latest version
pre-commit autoupdate

# Run hooks manually to see detailed output
pre-commit run --all-files --verbose
```

### Ruff finds too many errors

Don't panic! Many are auto-fixable:

```bash
# Auto-fix everything possible
make fix

# Then check what's left
make check
```

### Virtual environment issues

```bash
# Remove and recreate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
make install
```

## Best Practices

### Before Starting Work

```bash
git checkout -b feature/my-feature
make clean
make install
```

### During Development

- Run `make fix` frequently
- Commit small, logical changes
- Write descriptive commit messages

### Before Committing

```bash
make qa                 # Quick quality check
git add .
git commit -m "feat: add new feature"
```

### Before Pull Request

```bash
make check              # Ensure CI will pass
git push origin feature/my-feature
```

## Performance Tips

- **Ruff is fast** - Written in Rust, 10-100x faster than alternatives
- **Pre-commit uses caching** - Subsequent runs are much faster
- **VS Code integration** - Real-time feedback while coding

## Getting Help

- Check `CONTRIBUTING.md` for detailed contribution guidelines
- Run `make help` for available commands
- Open an issue for bugs or questions

## Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Home Assistant Development](https://developers.home-assistant.io/)

---

Happy coding! 🚀
