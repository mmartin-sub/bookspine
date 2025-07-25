# BookSpine

A command-line tool for calculating book spine dimensions for printing.

## Features

- Calculate spine width based on page count, paper type, and binding type
- Support for PDF files with automatic page count extraction
- Pre-configured settings for popular printing services (KDP, etc.)
- Multiple output formats (text, JSON, CSV)
- Comprehensive input validation and error handling

## Installation

```bash
pip install bookspine
```

## Usage

### Basic Usage

Calculate spine width with manual parameters:

```bash
bookspine --page-count 200 --paper-type MCG --binding-type "Softcover Perfect Bound" --paper-weight 80
```

### PDF-based Calculation

Extract page count from PDF and calculate spine:

```bash
bookspine --pdf book.pdf --paper-type MCG --binding-type "Softcover Perfect Bound" --paper-weight 80
```

### Using Printer Services

Use pre-configured settings for popular printing services:

```bash
bookspine --page-count 200 --printer-service kdp --binding-type "Softcover Perfect Bound"
```

### List Available Services

```bash
bookspine --list-services
```

### Validate PDF

Check if a PDF file is suitable for processing:

```bash
bookspine --pdf book.pdf --validate-pdf
```

### Output Formats

Save results to a file:

```bash
bookspine --page-count 200 --paper-type MCG --binding-type "Softcover Perfect Bound" --paper-weight 80 --output-file result.txt
```

JSON output:

```bash
bookspine --page-count 200 --paper-type MCG --binding-type "Softcover Perfect Bound" --paper-weight 80 --format json
```

## Paper Types

- MCG (Machine Coated Gloss)
- MCS (Machine Coated Silk)
- ECB (Elemental Chlorine Free Bleached)
- OFF (Offset)

## Binding Types

- Softcover Perfect Bound
- Hardcover Casewrap
- Hardcover Linen

## Development

### Setup

```bash
git clone <repository>
cd src/bookspine
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
