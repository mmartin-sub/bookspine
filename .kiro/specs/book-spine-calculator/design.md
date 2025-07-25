# Design Document: Book Spine Calculator

## Overview

The Book Spine Calculator is a Python tool designed to calculate the precise dimensions of a book's spine based on various input parameters such as page count, paper type, binding type, and paper weight. The tool will be developed as a professional Python package that can be installed via pip and used both as a command-line tool and as an importable library in other Python projects.

The system will follow a modular architecture that allows for easy extension with new printer service configurations without code changes. It will be memory-efficient when processing PDF files and will provide clear, unit-labeled output in multiple formats suitable for both human reading and machine parsing in automated workflows.

## Architecture

The Book Spine Calculator will follow a clean architecture pattern with clear separation of concerns:

```
book_spine_calculator/
├── __init__.py
├── cli.py                  # Command-line interface
├── core/
│   ├── __init__.py
│   ├── calculator.py       # Core calculation logic
│   ├── pdf_processor.py    # PDF processing functionality
│   └── unit_converter.py   # Unit conversion utilities
├── config/
│   ├── __init__.py
│   ├── config_loader.py    # Configuration loading logic
│   └── printer_services/   # Printer service configurations
│       ├── __init__.py
│       ├── default.json
│       ├── service_a.json
│       └── service_b.json
├── models/
│   ├── __init__.py
│   ├── book_metadata.py    # Data models for book metadata
│   └── spine_result.py     # Data models for calculation results
└── utils/
    ├── __init__.py
    ├── validators.py       # Input validation utilities
    └── formatters.py       # Output formatting utilities
```

### Key Components

1. **CLI Module**: Handles command-line argument parsing, input validation, and output formatting for command-line usage.

2. **Core Module**: Contains the central business logic for spine width calculations, PDF processing, and unit conversions.

3. **Config Module**: Manages loading and validating printer service configurations from JSON files.

4. **Models Module**: Defines data structures for book metadata and calculation results.

5. **Utils Module**: Provides utility functions for input validation and output formatting.

## Components and Interfaces

### CLI Component

The CLI component will use Python's `argparse` library to parse command-line arguments and provide a user-friendly interface.

```python
# Example CLI interface
def parse_args():
    parser = argparse.ArgumentParser(description='Calculate book spine dimensions')
    parser.add_argument('--pdf', type=str, help='Path to PDF file')
    parser.add_argument('--page-count', type=int, help='Total page count')
    parser.add_argument('--paper-type', type=str, help='Paper type (MCG, MCS, ECB, OFF)')
    parser.add_argument('--binding-type', type=str, help='Binding type')
    parser.add_argument('--paper-weight', type=float, help='Paper weight in gsm')
    parser.add_argument('--unit-system', type=str, choices=['metric', 'imperial'],
                        default='metric', help='Preferred unit system')
    parser.add_argument('--printer-service', type=str, help='Printer service name')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for pixel conversion')
    parser.add_argument('--output-format', type=str, choices=['text', 'json', 'csv'],
                        default='text', help='Output format')
    parser.add_argument('--output-file', type=str, help='Output file path')
    parser.add_argument('--list-services', action='store_true',
                        help='List available printer services')
    parser.add_argument('--manual-override', type=float,
                        help='Manual override for spine width (in mm)')
    return parser.parse_args()
```

### Core Calculator Component

The core calculator will implement the spine width calculation formulas and handle the logic for selecting the appropriate formula based on input parameters.

```python
# Example Calculator interface
class SpineCalculator:
    def __init__(self, config_loader):
        self.config_loader = config_loader

    def calculate_spine_width(self, book_metadata, printer_service=None, manual_override=None):
        """
        Calculate spine width based on book metadata and printer service config.

        Args:
            book_metadata (BookMetadata): Book metadata object
            printer_service (str, optional): Name of printer service
            manual_override (float, optional): Manual override value in mm

        Returns:
            SpineResult: Calculation result object
        """
        # Implementation of calculation logic
        pass
```

### PDF Processor Component

The PDF processor will handle extracting page count information from PDF files while minimizing memory usage.

```python
# Example PDF Processor interface
class PDFProcessor:
    def extract_page_count(self, pdf_path):
        """
        Extract page count from PDF file with minimal memory usage.

        Args:
            pdf_path (str): Path to PDF file

        Returns:
            int: Page count
        """
        # Implementation using PyPDF2 or similar library with memory optimization
        pass
```

### Configuration Loader Component

The configuration loader will handle loading and validating printer service configurations from JSON files.

```python
# Example Config Loader interface
class ConfigLoader:
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or self._get_default_config_dir()

    def load_printer_service_config(self, service_name=None):
        """
        Load printer service configuration.

        Args:
            service_name (str, optional): Name of printer service

        Returns:
            dict: Printer service configuration
        """
        # Implementation of configuration loading logic
        pass

    def list_available_services(self):
        """
        List all available printer services.

        Returns:
            list: List of available printer service names
        """
        # Implementation to list available services
        pass
```

## Data Models

### BookMetadata Model

```python
# Example BookMetadata model
@dataclass
class BookMetadata:
    page_count: int
    paper_type: str = None
    binding_type: str = None
    paper_weight: float = None
    unit_system: str = "metric"  # "metric" or "imperial"

    def validate(self):
        """Validate book metadata."""
        if self.page_count <= 0:
            raise ValueError("Page count must be positive")
        # Additional validation logic
```

### SpineResult Model

```python
# Example SpineResult model
@dataclass
class SpineResult:
    width_mm: float
    width_inches: float
    width_pixels: float
    dpi: int
    book_metadata: BookMetadata
    printer_service: str = None
    manual_override_applied: bool = False
    original_calculated_width_mm: float = None

    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self):
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    def to_csv(self):
        """Convert to CSV row."""
        # Implementation of CSV conversion
        pass
```

## Error Handling

The system will implement a comprehensive error handling strategy:

1. **Input Validation Errors**: Raised when input parameters fail validation checks.
2. **Configuration Errors**: Raised when printer service configurations are invalid or missing.
3. **PDF Processing Errors**: Raised when PDF files cannot be processed or are invalid.
4. **Calculation Errors**: Raised when spine width calculations fail due to invalid parameters.

All errors will be properly categorized and will provide clear, actionable error messages. When running as a command-line tool, appropriate exit codes will be used to indicate different error conditions.

```python
# Example error handling
class BookSpineCalculatorError(Exception):
    """Base exception for all book spine calculator errors."""
    pass

class InputValidationError(BookSpineCalculatorError):
    """Raised when input validation fails."""
    pass

class ConfigurationError(BookSpineCalculatorError):
    """Raised when configuration loading fails."""
    pass

class PDFProcessingError(BookSpineCalculatorError):
    """Raised when PDF processing fails."""
    pass

class CalculationError(BookSpineCalculatorError):
    """Raised when spine width calculation fails."""
    pass
```

## Testing Strategy

The testing strategy will include:

1. **Unit Tests**: For individual components and functions.
2. **Integration Tests**: For interactions between components.
3. **End-to-End Tests**: For complete workflows from input to output.
4. **Performance Tests**: To ensure memory efficiency with large PDF files.

Tests will be organized in a parallel directory structure to the main code:

```
tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_calculator.py
│   ├── test_pdf_processor.py
│   └── test_unit_converter.py
├── integration/
│   ├── __init__.py
│   └── test_end_to_end.py
└── resources/
    ├── sample.pdf
    └── test_configs/
        ├── valid_config.json
        └── invalid_config.json
```

## Printer Service Configuration Format

Printer service configurations will be stored in JSON files with the following structure:

```json
{
  "name": "service_name",
  "description": "Service description",
  "paper_bulk": {
    "MCG": 0.80,
    "MCS": 0.90,
    "ECB": 1.20,
    "OFF": 1.22
  },
  "cover_thickness": {
    "Softcover Perfect Bound": 0.5,
    "Hardcover Casewrap": 2.0,
    "Hardcover Linen": 3.0
  },
  "formulas": {
    "Softcover Perfect Bound": {
      "type": "general",
      "params": {}
    },
    "Hardcover Casewrap": {
      "type": "fixed_ranges",
      "params": {
        "ranges": [
          {"min_pages": 24, "max_pages": 84, "width_inches": 0.25},
          {"min_pages": 85, "max_pages": 140, "width_inches": 0.5}
        ]
      }
    }
  }
}
```

## Package Distribution

The package will be distributed via PyPI and will include:

1. **setup.py**: For package installation.
2. **requirements.txt**: For dependency management.
3. **README.md**: With installation and usage instructions.
4. **LICENSE**: With license information.
5. **CONTRIBUTING.md**: With contribution guidelines.
6. **.github/workflows/**: With CI/CD configuration.

## Command-Line Usage Examples

```bash
# Basic usage with manual input
book-spine-calc --page-count 200 --paper-type MCG --binding-type "Softcover Perfect Bound" --paper-weight 80

# Using a PDF file
book-spine-calc --pdf book.pdf --paper-type MCG --binding-type "Softcover Perfect Bound" --paper-weight 80

# Using a specific printer service
book-spine-calc --page-count 200 --printer-service service_a

# Output to JSON file
book-spine-calc --page-count 200 --paper-type MCG --output-format json --output-file spine.json

# List available printer services
book-spine-calc --list-services

# With manual override
book-spine-calc --page-count 200 --paper-type MCG --manual-override 12.5
```

## Library Usage Examples

```python
from book_spine_calculator import SpineCalculator, BookMetadata, ConfigLoader

# Create config loader
config_loader = ConfigLoader()

# Create calculator
calculator = SpineCalculator(config_loader)

# Create book metadata
metadata = BookMetadata(
    page_count=200,
    paper_type="MCG",
    binding_type="Softcover Perfect Bound",
    paper_weight=80,
    unit_system="metric"
)

# Calculate spine width
result = calculator.calculate_spine_width(metadata, printer_service="service_a")

# Access results
print(f"Spine width: {result.width_mm} mm")
print(f"Spine width: {result.width_inches} inches")
print(f"Spine width: {result.width_pixels} pixels at {result.dpi} DPI")
```

## Performance Considerations

1. **Memory Efficiency**: The PDF processor will use streaming techniques to minimize memory usage when processing large PDF files.

2. **Caching**: Frequently used printer service configurations will be cached to improve performance.

3. **Parallel Processing**: When processing multiple books, the system will support parallel processing to improve throughput.

4. **Resource Cleanup**: All resources (file handles, etc.) will be properly cleaned up to prevent resource leaks.

## Security Considerations

1. **Input Validation**: All user inputs will be validated to prevent security issues.

2. **Safe PDF Processing**: PDF processing will be done in a secure manner to prevent security vulnerabilities.

3. **Configuration Validation**: All printer service configurations will be validated before use to prevent security issues.

4. **No Execution of External Code**: The system will not execute any external code or commands.

## Future Extensions

1. **Web API**: Add a REST API for remote access.

2. **GUI**: Add a graphical user interface for desktop usage.

3. **Additional Output Formats**: Support for additional output formats (XML, YAML, etc.).

4. **Integration with Design Tools**: Direct integration with design tools like Adobe InDesign.

5. **Batch Processing**: Support for processing multiple books in batch mode.
