# Contributing to BookSpine & KTE

Thank you for your interest in contributing to BookSpine & KTE! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Development Setup](#️-development-setup)
- [Testing](#-testing)
- [Code Style](#-code-style)
- [Submitting Changes](#-submitting-changes)
- [Release Process](#-release-process)

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- UV (recommended) or pip

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/book-analyse.git
cd book-analyse

# Add the upstream repository
git remote add upstream https://github.com/original-owner/book-analyse.git
```

## 📦 Project Structure

This project contains two separate packages under `src/`:

```
src/
├── bookspine/          # Book spine calculation library
│   ├── cli.py         # Command-line interface
│   ├── core/          # Core calculation logic
│   ├── config/        # Configuration management
│   ├── models/        # Data models
│   ├── utils/         # Utilities
│   └── tests/         # Unit and integration tests
└── kte/               # Keyword extraction library
    ├── cli.py         # Command-line interface
    ├── core/          # Core extraction logic
    ├── models/        # Data models
    ├── utils/         # Utilities
    └── tests/         # Unit and integration tests
```

## 🛠️ Development Setup

### Using UV (Recommended)

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the project in development mode
uv pip install -e ".[dev,test,docs]"

# Or install packages individually
uv pip install -e "src/bookspine[dev,test]"
uv pip install -e "src/kte[dev,test]"
```

### Using pip

```bash
# Install the project in development mode
pip install -e ".[dev,test,docs]"
```

### Using Hatch

```bash
# Install Hatch
pip install hatch

# Create and activate the development environment
hatch env create
hatch shell

# Install dependencies
hatch run pip install -e ".[dev,test,docs]"
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
hatch run test

# Run tests for specific packages
hatch run test src/bookspine/
hatch run test src/kte/

# Run with coverage
hatch run test-cov

# Run specific test files
pytest src/bookspine/tests/unit/test_calculator.py
pytest src/kte/tests/unit/test_core_components.py
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **CLI Tests**: Test command-line interface functionality
- **Performance Tests**: Test performance and memory usage

### Writing Tests

Follow these guidelines when writing tests:

1. **Use descriptive test names**: Test names should clearly describe what is being tested
2. **Test one thing at a time**: Each test should focus on a single behavior
3. **Use fixtures**: Reuse common test data and setup
4. **Mock external dependencies**: Don't rely on external services in tests
5. **Test edge cases**: Include tests for error conditions and boundary values

Example test structure:

```python
import pytest
from bookspine.models.book_metadata import BookMetadata

class TestBookMetadata:
    """Test cases for BookMetadata model."""

    def test_valid_metadata(self):
        """Test creating valid book metadata."""
        metadata = BookMetadata(
            page_count=200,
            paper_type="MCG",
            binding_type="Softcover Perfect Bound",
            paper_weight=80.0
        )
        assert metadata.page_count == 200
        assert metadata.paper_type == "MCG"

    def test_invalid_page_count(self):
        """Test validation of invalid page count."""
        with pytest.raises(ValueError, match="Page count must be positive"):
            BookMetadata(page_count=0, paper_type="MCG", binding_type="Softcover Perfect Bound")
```

## 🎨 Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Import sorting**: Use `isort` or `ruff` for import sorting
- **Type hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings

### Code Formatting

```bash
# Format code with Black
hatch run format

# Check code style
hatch run style

# Fix import sorting
hatch run style-fix
```

### Linting

```bash
# Run linting with Ruff
hatch run lint

# Run type checking with MyPy
hatch run typing
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install

# Run against all files
pre-commit run --all-files
```

## 📝 Submitting Changes

### Creating a Pull Request

1. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**:

   ```bash
   # Run all tests
   hatch run test

   # Run linting
   hatch run lint

   # Run type checking
   hatch run typing
   ```

4. **Commit your changes**:

   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**:
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill out the PR template
   - Submit the PR

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:

```
feat(bookspine): add support for new paper type
fix(kte): resolve memory leak in keyword extraction
docs: update installation instructions
```

### Pull Request Guidelines

- **Title**: Clear, descriptive title
- **Description**: Explain what the PR does and why
- **Tests**: Include tests for new functionality
- **Documentation**: Update docs if needed
- **Breaking changes**: Clearly mark any breaking changes

## 🚀 Release Process

### Version Management

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update version** in `pyproject.toml`
2. **Update changelog** with new features and fixes
3. **Create release branch**:

   ```bash
   git checkout -b release/v1.2.3
   ```

4. **Test the release**:

   ```bash
   hatch run test
   hatch run build
   ```

5. **Create release** on GitHub
6. **Publish to PyPI**:

   ```bash
   hatch run publish
   ```

## 🤝 Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and general discussion
- **Documentation**: Check the docs in each package's README

## 📋 Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] No breaking changes (or clearly marked)
- [ ] Commit messages follow conventional format
- [ ] PR description is clear and complete

## 🙏 Thank You

Thank you for contributing to BookSpine & KTE! 🎉
