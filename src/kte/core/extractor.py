"""
Main extractor module for keyword and theme extraction.

This module provides the main interface for extracting keywords and themes
from book content using KeyBERT and various preprocessing techniques.
"""

import logging
import time
from typing import Any, Dict, Optional, Union

from ..models.extraction_options import ExtractionOptions
from ..models.extraction_result import ExtractionResult
from .header_weighting import HeaderWeighting
from .input_handler import InputHandler
from .keybert_extractor import KeyBERTExtractor
from .output_handler import OutputHandler
from .result_formatter import ResultFormatter


def extract_keywords(
    input_source: Union[str, Dict[str, Any]],
    options: Optional[Dict[str, Any]] = None,
    output_file: Optional[str] = None,
) -> ExtractionResult:
    """
    Main API function for keyword extraction.

    Args:
        input_source: Path to a file, raw text content, or dict with text.
        options: Optional configuration parameters.
        output_file: Optional path to save results.

    Returns:
        ExtractionResult: Extracted keywords in standardized format.

    Raises:
        ValueError: If input is empty or invalid.
        FileNotFoundError: If specified input file doesn't exist.
        Exception: If extraction process fails.
    """
    # Initialize components
    input_handler = InputHandler()
    keybert_extractor = KeyBERTExtractor()
    header_weighting = HeaderWeighting()
    result_formatter = ResultFormatter()
    output_handler = OutputHandler()

    # Parse options
    extraction_options = ExtractionOptions()
    if options:
        extraction_options = ExtractionOptions.from_dict(options)

    # Start timing
    start_time = time.time()

    try:
        # Step 1: Handle input
        processed_input = input_handler.handle_input(input_source, options or {})

        # Step 2: Extract keywords using KeyBERT
        keywords = keybert_extractor.extract_keywords(processed_input["text"], extraction_options)

        # Step 3: Apply header weighting
        headers = processed_input["metadata"].get("headers", [])
        weighted_keywords = header_weighting.apply_header_weighting(keywords, headers, extraction_options)

        # Step 4: Format and rank results
        formatted_keywords = result_formatter.format_results(weighted_keywords, extraction_options)

        # Step 5: Create extraction result
        processing_time = time.time() - start_time
        metadata = {
            **processed_input["metadata"],
            "processing_time": processing_time,
        }

        extraction_result = ExtractionResult(
            keywords=formatted_keywords,
            extraction_method="KeyBERT",
            metadata=metadata,
            options_used=extraction_options,
        )

        # Step 6: Handle output
        if output_file:
            output_handler.prepare_output(extraction_result, output_file)

        return extraction_result

    except Exception as e:
        # Add processing time to error context
        processing_time = time.time() - start_time

        # Preserve original exception types for known errors
        if isinstance(e, (ValueError, FileNotFoundError)):
            raise e

        # Wrap other exceptions with timing information
        raise Exception(f"Keyword extraction failed after {processing_time:.2f}s: {str(e)}")


class KeywordExtractor:
    """
    Main class for keyword extraction with configurable components.

    This class provides a high-level interface for keyword extraction
    with the ability to customize individual components.
    """

    def __init__(self):
        """
        Initialize the keyword extractor with default components.
        """
        self.input_handler = InputHandler()
        self.keybert_extractor = KeyBERTExtractor()
        self.header_weighting = HeaderWeighting()
        self.result_formatter = ResultFormatter()
        self.output_handler = OutputHandler()

    def extract(
        self,
        input_source: Union[str, Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None,
        output_file: Optional[str] = None,
    ) -> ExtractionResult:
        """
        Extract keywords using the configured pipeline.

        Args:
            input_source: Path to a file, raw text content, or dict with text.
            options: Optional configuration parameters.
            output_file: Optional path to save results.

        Returns:
            ExtractionResult: Extracted keywords in standardized format.
        """
        return extract_keywords(input_source, options, output_file)

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded models.

        Returns:
            Dict[str, Any]: Model information.
        """
        return {
            "keybert": self.keybert_extractor.get_model_info(),
            "components": {
                "input_handler": "Initialized",
                "header_weighting": "Initialized",
                "result_formatter": "Initialized",
                "output_handler": "Initialized",
            },
        }
