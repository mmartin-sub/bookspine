"""
Keyword Theme Extraction (KTE) Package

This package provides functionality for extracting keywords and themes from book content
using KeyBERT, with special emphasis on multi-word phrases and header content.
"""

from .core.extractor import extract_keywords
from .models.extraction_options import ExtractionOptions
from .models.extraction_result import ExtractionResult
from .models.keyword_result import KeywordResult

__all__ = [
    "extract_keywords",
    "ExtractionOptions",
    "ExtractionResult",
    "KeywordResult",
]

# CLI entry point
__version__ = "0.1.0"
