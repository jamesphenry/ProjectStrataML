# Test Suite

This directory contains pytest tests for ProjectStrataML tools and utilities.

Tests follow the naming convention `test_*.py` and aim for >90% coverage.

Run tests with:
```bash
pytest -xvs                # Run single test, stop on first failure
pytest -k "test_name"      # Run specific test
pytest --cov=.             # Run with coverage
```