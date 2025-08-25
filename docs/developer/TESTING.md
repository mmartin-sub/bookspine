# Testing Guide

This guide explains how to run tests for the BookSpine project, both locally and in CI/CD environments.

## Quick Start

### Option 1: Python Script (Recommended)

```bash
# Run all tests with coverage
python run_tests.py

# Run specific test categories
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --resources
python run_tests.py --kte
python run_tests.py --spine
python run_tests.py --performance

# Run in CI mode (all checks)
python run_tests.py --ci

# Generate HTML coverage report
python run_tests.py --html
```

### Option 2: Shell Script

```bash
# Run all tests
./tests/test.sh

# Run specific test categories
./tests/test.sh unit
./tests/test.sh integration
./tests/test.sh resources
./tests/test.sh kte
./tests/test.sh spine
./tests/test.sh quick

# Run CI mode
./tests/test.sh ci

# Install dependencies
./tests/test.sh install
```

### Option 3: Direct pytest

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=bookspine --cov-report=term-missing tests/

# Run specific test modules
pytest tests/spine/
pytest tests/kte/

# Run specific test files
pytest tests/spine/unit/
pytest tests/kte/unit/
pytest tests/spine/unit/test_calculator.py
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=bookspine

# Run specific test file
pytest tests/spine/unit/test_calculator.py

# Run tests with verbose output
pytest -v
```

### Important: Pre-downloading Models for KTE Tests

The Keyword Theme Extraction (KTE) tests require a machine learning model from Hugging Face. To ensure the tests run correctly and reliably, you **must** pre-download and cache this model before running the test suite.

This prevents two common issues:
1.  **Hugging Face Rate Limiting:** Repeatedly downloading the model can lead to `HTTP 429` errors.
2.  **Performance Test Failures:** The time taken to download the model can cause performance tests to time out.

**To download the model, run the following command from the root of the repository:**

```bash
python scripts/download_models.py
```

This only needs to be done once.

For CI/CD environments or to get higher rate limits, you can also set an API token as an environment variable:

```bash
export HF_TOKEN="your_token_here"
```

## Test Structure

The tests are organized into two main modules:

### 📏 Spine Calculator Module (`tests/spine/`)

- **Unit Tests** (`tests/spine/unit/`): Core spine calculation functionality
- **Integration Tests** (`tests/spine/integration/`): End-to-end workflows and CLI

### 🔍 Keyword Theme Extraction Module (`tests/kte/`)

- **Unit Tests** (`tests/kte/unit/`): KTE functionality and file processing
- **Integration Tests** (`tests/kte/integration/`): KTE workflows and performance

## Test Categories

### 1. Unit Tests

- **Purpose**: Test individual components in isolation
- **Coverage**: Core functionality, data models, utilities
- **Speed**: Fast execution
- **Location**: `tests/spine/unit/` and `tests/kte/unit/`

**Run with**: `python run_tests.py --unit`

### 2. Integration Tests

- **Purpose**: Test complete workflows and system interactions
- **Coverage**: End-to-end scenarios, CLI, performance
- **Speed**: Medium execution time
- **Location**: `tests/spine/integration/` and `tests/kte/integration/`

**Run with**: `python run_tests.py --integration`

### 3. Module-Specific Tests

#### Spine Tests (`tests/spine/`)

- **Purpose**: Test spine calculation functionality
- **Coverage**: Calculator, PDF processor, unit converter, CLI
- **Files**: 9 unit tests + 3 integration tests

**Run with**: `python run_tests.py --spine`

#### KTE Tests (`tests/kte/`)

- **Purpose**: Test Keyword Theme Extraction functionality
- **Coverage**: KeyBERT integration, text processing, file handling
- **Files**: 1 unit test (resource-based) + integration tests

**Run with**: `python run_tests.py --kte`

### 4. Resource-Based Tests

- **Purpose**: Test all files in `tests/resources/` folder
- **Coverage**: PDF, Markdown, and text file processing
- **Speed**: Fast execution
- **Files**: 2 test files that test all resource files

**Run with**: `python run_tests.py --resources`

### 5. Performance Tests

- **Purpose**: Test performance characteristics and scalability
- **Coverage**: Memory usage, processing speed, parallel execution
- **Speed**: Slow execution (intentionally)
- **Files**: 1 test file for performance benchmarks

**Run with**: `python run_tests.py --performance`

## Test Options

### Verbose Output

Add `--verbose` or `-v` for detailed test output:

```bash
python run_tests.py --unit --verbose
```

### Quick Tests

Exclude performance tests for faster execution:

```bash
python run_tests.py --quick
```

### CI Mode

Run all checks (linting, type checking, tests) with minimal output:

```bash
python run_tests.py --ci
```

### HTML Coverage Report

Generate detailed HTML coverage report:

```bash
python run_tests.py --html
# Open tests/htmlcov/index.html in your browser
```

## Quality Checks

### Linting

```bash
# Run linting only
python run_tests.py --lint

# Or directly
ruff check .
black --check --diff .
```

### Type Checking

```bash
# Run type checking only
python run_tests.py --types

# Or directly
mypy bookspine/
```

### Shell Script Validation

```bash
# Check shell scripts
bash scripts/check_shell_scripts.sh

# Or run as part of CI checks
python run_tests.py --ci
```

The shell script validation checks:

- Syntax validity
- Proper shebang (`#!/bin/bash`)
- Error handling (`set -e`)
- Variable quoting
- Executable permissions

## CI/CD Integration

### GitHub Actions

The project includes a comprehensive GitHub Actions workflow (`.github/workflows/tests.yml`) that:

1. **Runs on**: Push to main/develop, Pull Requests
2. **Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12
3. **Jobs**:
   - **test**: Main test suite with coverage
   - **test-spine**: Spine calculator tests
   - **test-kte**: KTE and resource-based tests
   - **performance**: Performance tests (main branch only)
   - **security**: Security checks with bandit and safety

### Local CI Simulation

To simulate CI locally:

```bash
python run_tests.py --ci
```

This runs:

1. Linting checks (ruff, black)
2. Type checking (mypy)
3. All tests with coverage

## Test Resources

### Resource Files (`tests/resources/`)

- `sample.pdf` - Original sample PDF
- `test1.pdf` - Additional test PDF (copy)
- `test2.pdf` - Additional test PDF (copy)
- `sample.txt` - Sample text file
- `sample.md` - Sample markdown file

### Resource-Based Testing

The resource-based tests automatically:

- Discover all files in `tests/resources/`
- Test each file with appropriate processors
- Validate file formats and content
- Ensure consistent results across identical files

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Coverage Configuration (pyproject.toml)

```toml
[tool.coverage.run]
source = ["bookspine"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    # ... other exclusions
]
```

## Troubleshooting

### Common Issues

1. **Import Errors**

   ```bash
   # Install dependencies
   uv sync --dev
   # or
   pip install -e .
   ```

2. **Missing Dependencies**

   ```bash
   # Install test dependencies
   uv pip install pytest pytest-cov ruff black mypy
   ```

3. **Performance Tests Timeout**

   ```bash
   # Run without performance tests
   python run_tests.py --quick
   ```

4. **Type Checking Errors**

   ```bash
   # Install type stubs
   uv pip install types-Markdown types-PyYAML
   ```

### Debug Mode

For debugging test issues:

```bash
# Run with maximum verbosity
pytest -vvv tests/

# Run specific test with debug output
pytest -vvv tests/spine/unit/test_calculator.py::TestSpineCalculator::test_calculate_spine_width_basic

# Run with print statements visible
pytest -s tests/
```

## Test Development

### Adding New Tests

1. **Spine Unit Tests**: Add to `tests/spine/unit/`
2. **Spine Integration Tests**: Add to `tests/spine/integration/`
3. **KTE Unit Tests**: Add to `tests/kte/unit/`
4. **KTE Integration Tests**: Add to `tests/kte/integration/`
5. **Resource Tests**: Add to `tests/resources/` and update resource tests

### Test Naming Convention

- Files: `test_*.py`
- Classes: `Test*`
- Methods: `test_*`

### Test Structure

```python
def test_something():
    """Test description."""
    # Arrange
    # Act
    # Assert
```

## Coverage Reports

### Terminal Coverage

```bash
python run_tests.py
# Shows coverage summary in terminal
```

### HTML Coverage Report

```bash
python run_tests.py --html
# Generates detailed HTML report in tests/htmlcov/
```

### Coverage Targets

- **Overall**: >80%
- **Core modules**: >90%
- **New features**: >95%

## Performance Benchmarks

### Running Performance Tests

```bash
python run_tests.py --performance
```

### Performance Targets

- **Test execution**: <60 seconds for full suite
- **Memory usage**: <500MB peak
- **Model loading**: <30 seconds for KeyBERT
- **File processing**: <10 seconds per file

## Security Testing

### Running Security Checks

```bash
# Bandit (security linter)
bandit -r bookspine/

# Safety (dependency vulnerability checker)
safety check
```

### Security Targets

- **Bandit score**: A (low risk)
- **Safety check**: No known vulnerabilities
- **Dependencies**: Up-to-date versions

## Continuous Integration

### Pre-commit Checklist

Before committing, ensure:

1. ✅ All tests pass: `python run_tests.py --ci`
2. ✅ Linting passes: `python run_tests.py --lint`
3. ✅ Type checking passes: `python run_tests.py --types`
4. ✅ Coverage is adequate: `python run_tests.py --html`

### Pull Request Requirements

- All CI checks must pass
- Coverage should not decrease
- New features should have tests
- Performance tests should pass

## Advanced Usage

### Parallel Testing

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto tests/
```

### Test Filtering

```bash
# Run tests matching pattern
pytest -k "calculator" tests/

# Exclude tests matching pattern
pytest -k "not performance" tests/
```

### Custom Test Configuration

```bash
# Run with custom pytest options
pytest --tb=short --maxfail=5 tests/
```

## Support

For test-related issues:

1. Check this guide first
2. Review test documentation in `tests/TEST_DOCUMENTATION.md`
3. Check GitHub Actions logs for CI issues
4. Run tests locally to reproduce issues
