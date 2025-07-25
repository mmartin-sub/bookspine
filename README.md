# BookSpine & KTE - Professional Book Analysis Tools

A comprehensive Python toolkit for calculating book spine dimensions and extracting keywords from book content. This project provides two separate, professional-grade libraries:

- **BookSpine**: Calculate precise book spine dimensions for various printing services
- **KTE (Keyword Theme Extraction)**: Extract and analyze keywords from book content using AI

## 🚀 Quick Start

### Installation

```bash
# Install both packages
pip install bookspine kte

# Or install individually
pip install bookspine  # For spine calculations only
pip install kte        # For keyword extraction only
```

### BookSpine Usage

```bash
# Basic spine calculation
bookspine --page-count 200 --paper-type MCG --binding-type "Softcover Perfect Bound" --paper-weight 80

# From PDF file
bookspine --pdf book.pdf --paper-type MCG --binding-type "Softcover Perfect Bound" --paper-weight 80

# Using printer service
bookspine --page-count 200 --printer-service kdp --binding-type "Softcover Perfect Bound"

# List available services
bookspine --list-services
```

### KTE Usage

```bash
# Extract keywords from text
kte --text "Your book content here" --max-keywords 10

# Extract from file
kte --file book.md --max-keywords 15 --output-file keywords.json

# Extract from PDF
kte --file book.pdf --format json
```

## 📦 Project Structure

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

## 🛠️ Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/book-analyse.git
cd book-analyse

# Install development dependencies
pip install -e ".[dev,test,docs]"

# Run tests
hatch run test
```

### Testing

```bash
# Run all tests
hatch run test

# Run specific package tests
hatch run test src/bookspine/
hatch run test src/kte/

# Run with coverage
hatch run test-cov
```

## 📚 Documentation

- [BookSpine Documentation](src/bookspine/README.md)
- [KTE Documentation](src/kte/README.md)
- [API Reference](docs/api.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
