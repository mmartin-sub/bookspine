# BookSpine Project Documentation

## Overview

The BookSpine project is a comprehensive tool for calculating book spine dimensions and extracting keywords from book content. It provides both spine calculation functionality and keyword theme extraction capabilities.

## Key Features

### Spine Calculation

- **PDF page count extraction**: Automatically extract page count from PDF files
- **Spine width calculation**: Calculate spine width based on paper type and binding
- **Multiple paper types**: Support for MCG, MCS, ECB, and OFF paper types
- **Binding options**: Softcover Perfect Bound, Hardcover Casewrap, Hardcover Linen

### Keyword Theme Extraction (KTE)

- **KeyBERT integration**: State-of-the-art keyword extraction using BERT
- **Multi-format support**: PDF, Markdown, and text file processing
- **Header weighting**: Prioritize terms found in document headers
- **Phrase prioritization**: Focus on multi-word phrases over single words
- **Semantic understanding**: Leverage transformer models for better results

## Technical Architecture

### Core Components

- **SpineCalculator**: Main calculation engine
- **PDFProcessor**: PDF file processing and page extraction
- **KeyBERTExtractor**: Keyword extraction using KeyBERT
- **TextPreprocessor**: Text normalization and header detection
- **FileUtils**: Multi-format file handling

### Data Models

- **BookMetadata**: Book specifications and parameters
- **SpineResult**: Calculation results with multiple unit formats
- **ExtractionResult**: Keyword extraction results
- **KeywordResult**: Individual keyword/phrase data

## Usage Examples

### Spine Calculation

```bash
bookspine --page-count 200 --paper-type MCG --binding-type "Softcover Perfect Bound" --paper-weight 80
```

### Keyword Extraction

```bash
bookspine extract --file book.pdf --max-keywords 15 --output-file keywords.json
```

## Installation

The project uses modern Python packaging with uv for dependency management:

```bash
uv pip install -e .
```

## Testing

Comprehensive test suite covering:

- Unit tests for all components
- Integration tests for complete workflows
- Performance tests for scalability
- Resource-based tests for file processing

This markdown file serves as a test resource for validating markdown processing capabilities and demonstrating the project's comprehensive feature set.
