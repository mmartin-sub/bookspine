# KTE (Keyword Theme Extraction)

A command-line tool for extracting keywords and themes from book content using KeyBERT.

## Features

- Extract keywords and themes from various file formats (PDF, TXT, MD)
- Support for direct text input
- Multi-word phrase detection with configurable preferences
- Header content weighting for better keyword relevance
- Multiple output formats (text, JSON)
- Comprehensive input validation and error handling

## Installation

```bash
pip install kte
```

## Usage

### Basic Usage

Extract keywords from a file:

```bash
kte --file document.pdf --max-keywords 10
```

Extract keywords from text:

```bash
kte --text "Your book content here" --max-keywords 10
```

### Advanced Options

Configure extraction parameters:

```bash
kte --file book.pdf --max-keywords 15 --min-relevance 0.3 --header-weight-factor 2.0
```

### Output Formats

JSON output:

```bash
kte --file document.pdf --format json
```

Save to file:

```bash
kte --file document.pdf --output-file keywords.json
```

### Verbose Output

Enable detailed logging:

```bash
kte --file document.pdf --verbose
```

## Parameters

- `--file, -f`: Path to input file (PDF, TXT, MD, etc.)
- `--text, -t`: Input text content directly
- `--max-keywords, -k`: Maximum number of keywords to extract (default: 10)
- `--min-relevance, -r`: Minimum relevance score for keywords (0.0-1.0, default: 0.1)
- `--header-weight-factor, -w`: Weight factor for header content (default: 1.5)
- `--no-prefer-phrases`: Don't prefer multi-word phrases over single words
- `--format, -o`: Output format (text, json, default: text)
- `--output-file, -O`: Output file path
- `--verbose, -v`: Enable verbose output

## Supported File Formats

- PDF files
- Text files (.txt)
- Markdown files (.md)
- Direct text input

## Development

### Setup

```bash
git clone <repository>
cd src/kte
uv sync
```

### Running Tests

```bash
uv run test
```

### Linting

```bash
uv run lint
```

## License

MIT License - see LICENSE file for details.
