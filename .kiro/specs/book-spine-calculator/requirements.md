# Requirements Document

## Introduction

The Book Spine Calculator is a Python tool designed to compute the precise dimensions of a book's spine (also called spinner) based on various input parameters. This tool will take into account book metadata such as page count, paper type, binding type, and paper weight to calculate the spine width. The calculated dimensions will be used later to generate spine images or PDF/X files that can be integrated with front and back covers for professional book printing.

The tool is designed to be modular, memory-efficient, and suitable for integration into automated workflows where multiple instances may run in parallel. It will be developed as a professional Python package that can be installed via uv, with a well-structured Git repository following industry best practices for code organization, documentation, and testing.

## Requirements

### Requirement 1: Input Processing

**User Story:** As a book publisher, I want to provide book metadata in a structured format, so that the tool can accurately calculate the spine dimensions.

#### Acceptance Criteria

1. WHEN the user provides a PDF file THEN the system SHALL extract page count information while minimizing memory usage for large files.
2. WHEN the user provides metadata manually THEN the system SHALL accept and validate the following parameters:
   - Total page count
   - Paper type (e.g., "MCG", "MCS", "ECB", "OFF")
   - Binding type (e.g., "Softcover Perfect Bound", "Hardcover Casewrap/Linen")
   - Paper weight in gsm (Grams per Square Meter)
   - Preferred unit system (metric or imperial)
3. WHEN input is missing required parameters THEN the system SHALL provide clear error messages.
4. WHEN the system receives a PDF file THEN it SHALL verify it contains valid book content.
5. WHEN the user specifies a printer service THEN the system SHALL load the appropriate calculation parameters from a dedicated configuration file for that service.
6. WHEN operating in a workflow environment THEN the system SHALL avoid creating persistent temporary files that could conflict with parallel executions.

### Requirement 2: Spine Width Calculation

**User Story:** As a book designer, I want accurate spine width calculations based on industry-standard formulas, so that I can create properly sized spine designs.

#### Acceptance Criteria

1. WHEN calculating spine width for Softcover Perfect Bound with general paper THEN the system SHALL use the formula: Spine Width (inches) = (pages / 444) + 0.06".
2. WHEN calculating spine width for Softcover Perfect Bound with 460 PPI paper THEN the system SHALL use the formula: Spine Width (inches) = (pages / 460) + 0.06".
3. WHEN using the general metric formula THEN the system SHALL calculate: Spine in mm = (paperweight in gsm × paper bulk × (page count / 2)) / 1000 + (2 × cover thickness).
4. WHEN using the general imperial formula THEN the system SHALL calculate: Spine in inch = ((paperweight in gsm × paper bulk × (page count / 2)) / 1000 + (2 × cover thickness)) / 25.4.
5. WHEN calculating for Hardcover binding THEN the system SHALL use appropriate cover thickness values (e.g., 2.0 mm or 3.0 mm).
6. WHEN calculating for different paper types THEN the system SHALL use the correct paper bulk values:
   - MCG: 0.80
   - MCS: 0.90
   - ECB: 1.20
   - OFF: 1.22

### Requirement 3: Unit Conversion and Precision

**User Story:** As a graphic designer, I want spine dimensions converted to pixels at a specified DPI with clear unit labeling, so that I can create print-ready spine designs without unit confusion.

#### Acceptance Criteria

1. WHEN spine width is calculated in millimeters THEN the system SHALL convert it to pixels using the formula: pixels = (value_mm / 25.4) * DPI.
2. WHEN spine width is calculated in inches THEN the system SHALL convert it to pixels using the formula: pixels = value_inches * DPI.
3. WHEN no DPI is specified THEN the system SHALL default to 300 DPI for high-resolution print output.
4. WHEN converting units THEN the system SHALL maintain precision to at least 2 decimal places.
5. WHEN displaying measurements THEN the system SHALL clearly label all units (mm, inches, pixels) to prevent confusion.
6. WHEN the user specifies a preferred unit system (metric or imperial) THEN the system SHALL prioritize displaying results in that system first, followed by conversions.

### Requirement 4: Output Generation

**User Story:** As a book production manager, I want the spine dimensions output in a usable format, so that I can proceed with cover design and printing.

#### Acceptance Criteria

1. WHEN calculations are complete THEN the system SHALL output the spine dimensions in millimeters, inches, and pixels with clear unit labels.
2. WHEN requested THEN the system SHALL save the output to a specified file format.
3. WHEN displaying results THEN the system SHALL include all input parameters used for calculation for reference.
4. WHEN generating output THEN the system SHALL format the data in a clear, structured manner.
5. WHEN running in a script or workflow THEN the system SHALL provide machine-readable output options (e.g., JSON, CSV) for easy parsing by other tools.
6. WHEN running in a workflow THEN the system SHALL support both stdout output and file output modes.

### Requirement 5: Manual Adjustments

**User Story:** As a print production specialist, I want to manually override calculated spine dimensions, so that I can account for real-world variations from print partners.

#### Acceptance Criteria

1. WHEN the user provides a manual override value THEN the system SHALL use this value instead of the calculated one.
2. WHEN a manual adjustment is applied THEN the system SHALL clearly indicate in the output that a manual override was used.
3. WHEN manual adjustments are made THEN the system SHALL still display the originally calculated value for reference.

### Requirement 6: Error Handling and Validation

**User Story:** As a user, I want clear error messages and input validation, so that I can quickly identify and fix issues with my inputs.

#### Acceptance Criteria

1. WHEN invalid input is provided THEN the system SHALL display specific error messages.
2. WHEN page count is negative or zero THEN the system SHALL reject the input and prompt for correction.
3. WHEN an unsupported paper type or binding type is provided THEN the system SHALL list the supported options.
4. WHEN paper weight is outside reasonable bounds (e.g., < 50 or > 300 gsm) THEN the system SHALL warn the user but allow the calculation to proceed.
5. WHEN running in a workflow or script THEN the system SHALL use appropriate exit codes to indicate success or specific error conditions.

### Requirement 7: Modularity and Printer Service Configuration

**User Story:** As a production coordinator working with multiple print vendors, I want to select specific printer services with their own calculation parameters, so that I can get accurate spine calculations for each vendor.

#### Acceptance Criteria

1. WHEN a printer service is specified THEN the system SHALL load calculation parameters specific to that service.
2. WHEN no printer service is specified THEN the system SHALL use default calculation parameters.
3. WHEN a new printer service needs to be added THEN the system SHALL support adding configuration files without code changes.
4. WHEN loading printer service configurations THEN the system SHALL validate the configuration format.
5. WHEN a printer service configuration is missing required parameters THEN the system SHALL provide clear error messages.
6. WHEN multiple printer services are available THEN the system SHALL provide a way to list all available services.

### Requirement 8: Command-Line Interface and User Experience

**User Story:** As a user, I want comprehensive help and clear guidance when using the command-line interface, so that I can quickly understand how to use the tool effectively.

#### Acceptance Criteria

1. WHEN the user runs the tool with --help THEN the system SHALL display comprehensive help text with organized argument groups.
2. WHEN displaying help THEN the system SHALL include clear descriptions for each argument with expected values and formats.
3. WHEN displaying help THEN the system SHALL provide practical usage examples for common scenarios.
4. WHEN displaying help THEN the system SHALL group related arguments logically (input options, book specifications, printer services, output options, advanced options).
5. WHEN displaying help THEN the system SHALL include information about supported paper types, binding types, and typical value ranges.
6. WHEN displaying help THEN the system SHALL provide a link to additional documentation or resources.
7. WHEN the user provides invalid arguments THEN the system SHALL suggest the correct usage and refer to --help for more information.

### Requirement 9: Package Distribution and Project Structure

**User Story:** As a developer, I want to easily install and integrate the book spine calculator into my projects, so that I can automate book production workflows.

#### Acceptance Criteria

1. WHEN distributing the tool THEN the system SHALL be packaged as a proper Python module installable via uv.
2. WHEN organizing the codebase THEN the system SHALL follow a professional project structure with clear separation of concerns.
3. WHEN documenting the code THEN the system SHALL include comprehensive docstrings and API documentation.
4. WHEN releasing the package THEN the system SHALL include proper versioning following semantic versioning principles.
5. WHEN setting up the project THEN the system SHALL include:
   - A comprehensive README with installation and usage instructions
   - Proper license information
   - Contribution guidelines
   - Unit and integration tests with good coverage
   - Continuous integration setup
   - Example usage scripts
6. WHEN developing the package THEN the system SHALL follow PEP 8 style guidelines and best practices.
7. WHEN importing the package THEN users SHALL be able to use it both as a command-line tool and as an importable library.

## Additional Requirements (Beyond Original Scope)

### Requirement 10: Keyword Theme Extraction (KTE) Module

**User Story:** As a book publisher, I want to extract keywords and themes from book content, so that I can create effective book covers and marketing materials.

#### Acceptance Criteria

1. WHEN processing book content THEN the system SHALL extract relevant keywords and phrases using KeyBERT.
2. WHEN extracting keywords THEN the system SHALL prioritize multi-word phrases over single keywords when they have similar relevance.
3. WHEN processing text with headers THEN the system SHALL give higher weight to terms found in headers.
4. WHEN extracting keywords THEN the system SHALL support multiple input formats (PDF, Markdown, text).
5. WHEN generating output THEN the system SHALL provide structured JSON output with metadata.
6. WHEN processing large texts THEN the system SHALL complete extraction within a reasonable time frame.
7. WHEN the user specifies extraction parameters THEN the system SHALL respect max keywords, relevance thresholds, and header weighting factors.
8. WHEN running keyword extraction THEN the system SHALL provide a command-line interface integrated with the main tool.

### Requirement 11: Hugging Face Model Integration

**User Story:** As a developer, I want reliable access to AI models for keyword extraction, so that the system can work consistently in production environments.

#### Acceptance Criteria

1. WHEN downloading models THEN the system SHALL cache them locally to avoid repeated downloads.
2. WHEN using Hugging Face models THEN the system SHALL support API token authentication for better rate limits.
3. WHEN rate limiting occurs THEN the system SHALL provide clear guidance on obtaining and configuring API tokens.
4. WHEN models are cached THEN the system SHALL support offline mode for improved performance.
5. WHEN downloading models THEN the system SHALL provide progress indicators and error handling.
6. WHEN configuring the system THEN the system SHALL support environment variables for API tokens and cache directories.
7. WHEN running in production THEN the system SHALL handle model loading failures gracefully.

### Requirement 12: Modern Development Tools Integration

**User Story:** As a developer, I want to use modern Python development tools, so that I can maintain high code quality and development efficiency.

#### Acceptance Criteria

1. WHEN managing dependencies THEN the system SHALL use UV for fast package management.
2. WHEN managing project environments THEN the system SHALL use Hatch for advanced environment handling.
3. WHEN checking code quality THEN the system SHALL use Ruff for fast linting.
4. WHEN checking types THEN the system SHALL use MyPy for static type checking.
5. WHEN formatting code THEN the system SHALL use Black for consistent formatting.
6. WHEN running tests THEN the system SHALL use pytest with comprehensive coverage reporting.
7. WHEN checking security THEN the system SHALL use Bandit for security analysis.
8. WHEN setting up CI/CD THEN the system SHALL use GitHub Actions for automated testing and deployment.

### Requirement 13: Comprehensive Testing Framework

**User Story:** As a developer, I want comprehensive testing coverage, so that I can ensure the system works reliably across different scenarios.

#### Acceptance Criteria

1. WHEN testing the system THEN it SHALL include unit tests for all components.
2. WHEN testing the system THEN it SHALL include integration tests for complete workflows.
3. WHEN testing the system THEN it SHALL include performance tests for memory usage and speed.
4. WHEN testing the system THEN it SHALL include resource tests for file processing and model loading.
5. WHEN running tests THEN the system SHALL provide detailed coverage reporting.
6. WHEN testing KTE functionality THEN the system SHALL handle rate limiting gracefully.
7. WHEN testing PDF processing THEN the system SHALL test with various file sizes and formats.
8. WHEN testing CLI functionality THEN the system SHALL test all command-line options and error conditions.

### Requirement 14: Production-Ready Documentation

**User Story:** As a user, I want comprehensive documentation, so that I can quickly understand and use the system effectively.

#### Acceptance Criteria

1. WHEN documenting the system THEN it SHALL include complete API documentation with type hints.
2. WHEN documenting the system THEN it SHALL include comprehensive CLI help and examples.
3. WHEN documenting the system THEN it SHALL include developer setup and contribution guidelines.
4. WHEN documenting the system THEN it SHALL include testing and debugging guides.
5. WHEN documenting the system THEN it SHALL include environment configuration for Hugging Face integration.
6. WHEN documenting the system THEN it SHALL include performance characteristics and usage examples.
7. WHEN documenting the system THEN it SHALL include troubleshooting guides for common issues.
8. WHEN documenting the system THEN it SHALL include future enhancement roadmaps.
