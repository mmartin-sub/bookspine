# TODO

This file lists potential improvements and tasks for the BookSpine project.

## Development Environment

-   [ ] **Unify Development Setup:** The `scripts/setup_dev.sh` script uses `venv` and `pip`, while the `pyproject.toml` is configured for `hatch`. We should standardize on `hatch` and update or remove the `setup_dev.sh` script.
-   [ ] **Improve Stub Generation Script:** The `scripts/update-stubs.py` script could be refactored for better clarity and robustness.
-   [ ] **Document Scripts:** Add documentation for the developer scripts in `scripts/`, explaining their purpose and usage.

## Testing

-   [ ] **Increase Test Coverage:** Improve test coverage, especially for the `cli.py` modules of both `bookspine` and `kte`.
-   [ ] **Edge Case Testing:** Add more tests for error conditions and edge cases in the core logic.
-   [ ] **Use a Real PDF Library for Tests:** Replace the custom `PDFTestUtils` with a more robust PDF generation library to create test PDFs. This would allow for testing with more realistic and complex PDF files.
-   [ ] **Performance Benchmarks:** Add a suite of benchmarks to track performance over time and prevent regressions.

## Documentation

-   [ ] **User Guide:** Write a comprehensive user guide for both the `bookspine` and `kte` tools, with examples.
-   [ ] **API Documentation:** Generate API documentation for the core libraries.

## Features

-   [ ] **More Keyword Extractors:** Explore adding more keyword extraction backends to `kte`, such as spaCy or other models.
-   [ ] **Support More Printer Services:** Add more printer service configurations to `bookspine`.
-   [ ] **GUI:** A simple graphical user interface could make the tools more accessible to non-technical users.
