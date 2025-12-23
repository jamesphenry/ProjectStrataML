# ProjectStrataML Agent Instructions

**This repository follows TFC standards for ML project development. AI agents must adhere to these conventions.**

## Build/Lint/Test Commands
```bash
# Environment validation (required before any work)
python3 tools/setup.py --validate

# Code formatting and quality (run before commits)
black .                    # Format code
isort .                    # Sort imports  
flake8 .                   # Lint code
mypy .                     # Type checking

# Testing (when tests exist)
pytest -xvs                # Run single test, stop on first failure
pytest -k "test_name"      # Run specific test
pytest --cov=.             # Run with coverage
```

## Code Style Guidelines

### Imports (strict order)
```python
# 1. Standard library
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# 2. Third-party (alphabetical)
import yaml
import click
from rich.console import Console

# 3. Local imports (relative)
from .utils import helper_func
```

### Types (mandatory)
- **All functions** require type hints for parameters and return values
- Use `typing` module: `List`, `Dict`, `Optional`, `Tuple`
- Classes: `PascalCase` (`EnvironmentValidator`)
- Functions/variables: `snake_case` (`validate_python_version`)
- Constants: `UPPER_SNAKE_CASE` (when used)

### Error Handling (consistent pattern)
```python
class CustomError(Exception):
    """Descriptive docstring"""
    pass

def validate_something() -> bool:
    errors = []
    warnings = []
    
    # Validation logic
    if condition_fails:
        errors.append("Specific error message")
    
    return len(errors) == 0
```

### CLI Tools (framework standard)
- Use Click for CLI interface (`@click.command()`, `@click.option()`)
- Use Rich for beautiful console output (`console.print("✅ Success")`)
- Provide comprehensive help via docstrings
- Support `--validate` pattern for consistency

### Configuration (YAML-driven)
- Store configuration in `environments/` directory
- Use `yaml.safe_load()` for parsing
- Provide validation rules in system configuration
- Follow existing patterns in `environments/system.yaml`

### Testing (pytest when available)
- Test files: `tests/test_*.py` naming convention
- Use descriptive test names: `test_python_version_validation()`
- Mock external dependencies with `pytest-mock`
- Aim for high coverage (>90%)

### Documentation
- Docstrings required for all classes and public methods
- Module-level docstring explaining purpose and usage
- Use `"""Triple quotes"""` format
- Include examples in CLI tool docstrings

## Critical Constraints
- **Linux-only development** (Windows/macOS explicitly unsupported)
- **Virtual environments mandatory** (use `.venv/` directory)
- **Python 3.11+ required** (enforced by setup.py validation)
- **TFC compliance required** (run `tools/doctor.py --strict` before commits)
- **Git LFS required** for large files (datasets, models, artifacts)
- **YAML configuration** (no JSON or other formats)

## Tool Integration
- All tools must pass `tools/setup.py --validate`
- CLI tools should integrate with existing doctor validation
- Follow established patterns in `tools/setup.py`
- Use Rich console for consistent user experience
- Store tool configuration in `environments/` where applicable

## Repository Structure
Follow TFC-0001 layout strictly. Never modify core directories or file names. All tools must live in `tools/`, configs in `environments/`, and docs in `docs/TFC/`.