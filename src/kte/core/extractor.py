"""
Main extractor module for keyword and theme extraction.

This module provides the main interface for extracting keywords and themes
from book content using KeyBERT and various preprocessing techniques.
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from ..models.extraction_options import ExtractionOptions
from ..models.extraction_result import ExtractionResult
from ..models.keyword_result import KeywordResult
from .header_weighting import HeaderWeighting
from .input_handler import InputHandler
from .keybert_extractor import KeyBERTExtractor
from .output_handler import OutputHandler
from .result_formatter import ResultFormatter


def _initialize_components() -> Tuple[InputHandler, KeyBERTExtractor, HeaderWeighting, ResultFormatter, OutputHandler]:
    """Initialize all components needed for the extraction pipeline."""
    engine = os.environ.get("KTE_ENGINE", "local")
    api_url = os.environ.get("KTE_API_URL", "")
    auth_token = os.environ.get("KTE_AUTH_TOKEN")
    model_name = os.environ.get("KTE_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

    input_handler = InputHandler()
    keybert_extractor = KeyBERTExtractor(
        engine=engine,
        api_url=api_url,
        auth_token=auth_token,
        model_name=model_name,
    )
    header_weighting = HeaderWeighting()
    result_formatter = ResultFormatter()
    output_handler = OutputHandler()

    return input_handler, keybert_extractor, header_weighting, result_formatter, output_handler


def _process_input(
    input_handler: InputHandler,
    input_source: Union[str, Dict[str, Any]],
    options: Dict[str, Any],
) -> Dict[str, Any]:
    """Handle the input and return the processed text and metadata."""
    if input_source is None:
        raise ValueError("Input source cannot be None")
    return input_handler.handle_input(input_source, options)


def _extract_and_format_keywords(
    keybert_extractor: KeyBERTExtractor,
    header_weighting: HeaderWeighting,
    result_formatter: ResultFormatter,
    processed_input: Dict[str, Any],
    extraction_options: ExtractionOptions,
) -> List[KeywordResult]:
    """Perform keyword extraction, weighting, and formatting."""
    keywords = keybert_extractor.extract_keywords(processed_input["text"], extraction_options)
    headers = processed_input["metadata"].get("headers", [])
    weighted_keywords = header_weighting.apply_header_weighting(keywords, headers, extraction_options)
    return result_formatter.format_results(weighted_keywords, extraction_options)


def _create_extraction_result(
    formatted_keywords: List[KeywordResult],
    processed_input: Dict[str, Any],
    extraction_options: ExtractionOptions,
    start_time: float,
) -> ExtractionResult:
    """Create the final ExtractionResult object."""
    processing_time = time.time() - start_time
    metadata = {
        **processed_input["metadata"],
        "processing_time": processing_time,
    }
    return ExtractionResult(
        keywords=formatted_keywords,
        extraction_method="KeyBERT",
        metadata=metadata,
        options_used=extraction_options,
    )


def extract_keywords(
    input_source: Optional[Union[str, Dict[str, Any]]],
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
    start_time = time.time()
    try:
        input_handler, keybert_extractor, header_weighting, result_formatter, output_handler = _initialize_components()
        extraction_options = ExtractionOptions.from_dict(options or {})

        if input_source is None:
            raise ValueError("Input source cannot be None")

        processed_input = _process_input(input_handler, input_source, options or {})
        formatted_keywords = _extract_and_format_keywords(
            keybert_extractor, header_weighting, result_formatter, processed_input, extraction_options
        )
        extraction_result = _create_extraction_result(
            formatted_keywords, processed_input, extraction_options, start_time
        )

        if output_file:
            output_handler.prepare_output(extraction_result, output_file)

        return extraction_result

    except Exception as e:
        processing_time = time.time() - start_time
        if isinstance(e, (ValueError, FileNotFoundError)):
            raise e
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
        (
            self.input_handler,
            self.keybert_extractor,
            self.header_weighting,
            self.result_formatter,
            self.output_handler,
        ) = _initialize_components()

    def extract(
        self,
        input_source: Optional[Union[str, Dict[str, Any]]],
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
