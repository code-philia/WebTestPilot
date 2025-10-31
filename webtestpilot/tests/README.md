# Test Infrastructure

This directory contains the unit testing infrastructure for the WebTestPilot project.

## Structure

- `conftest.py` - Shared pytest fixtures and configuration
- `test_execute_assertion.py` - Unit tests for the `execute_assertion` function
- `pytest.ini` - Pytest configuration

## Running Tests

To run the tests, first install the development dependencies:

```bash
uv sync --group dev
```

Then run the tests:

```bash
uv run pytest
```

Or run with verbose output:

```bash
uv run pytest -v
```

## Test Coverage

The current test suite covers:

- `execute_assertion` function with various scenarios:
  - Successful precondition/postcondition assertions
  - Failed assertions with error messages
  - Missing code blocks or assertion functions
  - Multiple code blocks
  - Session access within assertions
  - Pydantic and typing imports
  - Syntax and runtime error handling

## Adding New Tests

When adding new tests:

1. Create test files following the `test_*.py` naming convention
2. Use the existing fixtures from `conftest.py` where appropriate
3. Follow the existing test class structure
4. Add descriptive test method names that explain what is being tested