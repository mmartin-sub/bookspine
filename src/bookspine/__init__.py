"""
Book Spine Calculator - A tool for calculating book spine dimensions.

This package provides utilities for calculating book spine dimensions based on
various parameters such as page count, paper type, binding type, and paper weight.
"""

__version__ = "0.1.0"

# Import main classes for easier access
from .config.config_loader import ConfigLoader
from .core.calculator import SpineCalculator
from .core.pdf_processor import PDFProcessor
from .core.unit_converter import UnitConverter
from .models.book_metadata import BookMetadata
from .models.spine_result import SpineResult

__all__ = [
    "BookMetadata",
    "SpineResult",
    "ConfigLoader",
    "SpineCalculator",
    "PDFProcessor",
    "UnitConverter",
]
