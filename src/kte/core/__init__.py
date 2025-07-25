"""
KTE Core Components

This module contains the core components for keyword and theme extraction.
"""

from .extractor import extract_keywords
from .header_weighting import HeaderWeighting
from .input_handler import InputHandler
from .keybert_extractor import KeyBERTExtractor
from .output_handler import OutputHandler
from .result_formatter import ResultFormatter

__all__ = [
    "extract_keywords",
    "HeaderWeighting",
    "InputHandler",
    "KeyBERTExtractor",
    "OutputHandler",
    "ResultFormatter",
]
