"""
Output handler for keyword extraction results.

This module handles the formatting and output of keyword extraction
results in various formats including text and JSON.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

from ..models.extraction_result import ExtractionResult


class OutputHandler:
    """
    Core component for handling output formatting and file saving.

    This class provides methods for formatting extraction results in different
    formats and saving them to files.
    """

    def prepare_output(self, extraction_result: ExtractionResult, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare the final output in the required format and optionally save to file.

        Args:
            extraction_result: Extraction result to format.
            output_file: Optional path to save results.

        Returns:
            Dict[str, Any]: Final output in standardized format.

        Raises:
            FileExistsError: If output file already exists.
            PermissionError: If unable to write to specified location.
        """
        # Convert to dictionary format
        output_dict = extraction_result.to_dict()

        # Save to file if specified
        if output_file:
            self._save_to_file(output_dict, output_file)

        return output_dict

    def _save_to_file(self, output_dict: Dict[str, Any], output_file: str):
        """
        Save output to file.

        Args:
            output_dict: Output dictionary to save.
            output_file: Path to save the file.

        Raises:
            FileExistsError: If output file already exists.
            PermissionError: If unable to write to specified location.
        """
        # Check if file already exists
        if os.path.exists(output_file):
            raise FileExistsError(f"Output file already exists: {output_file}")

        # Ensure directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                raise PermissionError(f"Cannot create directory {output_dir}: {e}")

        # Save as JSON
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_dict, f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise PermissionError(f"Cannot write to file {output_file}: {e}")

    def format_console_output(self, extraction_result: ExtractionResult) -> str:
        """
        Format extraction result for console output.

        Args:
            extraction_result: Extraction result to format.

        Returns:
            str: Formatted console output.
        """
        lines = []
        lines.append("Keyword Extraction Results")
        lines.append("=" * 50)
        lines.append("")

        # Add metadata
        metadata = extraction_result.metadata
        lines.append(f"Extraction Method: {extraction_result.extraction_method}")
        lines.append(f"Timestamp: {extraction_result.timestamp}")
        lines.append(f"Total Keywords: {len(extraction_result.keywords)}")
        lines.append("")

        # Add processing time if available
        if metadata and "processing_time" in metadata:
            lines.append(f"Processing Time: {metadata['processing_time']:.2f} seconds")
            lines.append("")

        # Add statistics
        stats = extraction_result.get_average_relevance_score()
        lines.append(f"Average Relevance Score: {stats:.3f}")
        lines.append("")

        # Add keywords
        lines.append("Extracted Keywords:")
        lines.append("-" * 30)

        for i, keyword in enumerate(extraction_result.keywords, 1):
            phrase_type = "phrase" if keyword.is_phrase else "keyword"
            header_info = " (header)" if keyword.from_header else ""
            lines.append(f"{i:2d}. {keyword.phrase} ({keyword.relevance_score:.3f}) - {phrase_type}{header_info}")

        return "\n".join(lines)

    def format_json_output(self, extraction_result: ExtractionResult, indent: int = 2) -> str:
        """
        Format extraction result as JSON string.

        Args:
            extraction_result: Extraction result to format.
            indent: JSON indentation.

        Returns:
            str: JSON formatted output.
        """
        return extraction_result.to_json(indent=indent)

    def get_output_summary(self, extraction_result: ExtractionResult) -> Dict[str, Any]:
        """
        Get a summary of the extraction results.

        Args:
            extraction_result: Extraction result to summarize.

        Returns:
            Dict[str, Any]: Summary of extraction results.
        """
        keywords = extraction_result.keywords
        phrases = extraction_result.get_phrases_only()
        header_keywords = extraction_result.get_header_keywords()

        return {
            "total_keywords": len(keywords),
            "phrases": len(phrases),
            "single_words": len(keywords) - len(phrases),
            "header_keywords": len(header_keywords),
            "avg_relevance_score": extraction_result.get_average_relevance_score(),
            "extraction_method": extraction_result.extraction_method,
            "timestamp": extraction_result.timestamp,
        }
