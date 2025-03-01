# Testing cc_autoignore

This directory contains tests for the cc_autoignore tool.

## Test Structure

The tests are organized into several categories:

1. **Unit Tests**: 
   - `test_core.py`: Tests for core.py functionality
   - `test_scanner.py`: Tests for scanner.py functionality
   - Additional unit tests for other modules (to be added)

2. **Integration Tests**:
   - `test_integration.py`: Tests interactions between components

3. **Functional Tests**:
   - `test_functional.py`: Tests command-line interface

## Test Environment

The test environment uses fixtures to create temporary file structures and mock the Claude Code CLI commands. Fixtures include:

- `temp_dir`: Creates a temporary directory for tests
- `temp_config_file`: Creates a temporary config file
- `mock_config`: Provides a sample configuration for testing
- `mock_git_repo`: Sets up a mock git repository with multiple .gitignore files
- `mock_subprocess_run`: Mocks the subprocess.run function to simulate Claude Code CLI

## Running Tests

Run the tests using pytest:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_core.py

# Run a specific test function
pytest tests/test_core.py::TestConfigFunctions::test_get_config_new
```

## Code Coverage

To measure code coverage:

```bash
# Install coverage tools
pip install pytest-cov

# Run tests with coverage
pytest --cov=.

# Generate HTML coverage report
pytest --cov=. --cov-report=html
```