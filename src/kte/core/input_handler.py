"""
Input handler for processing various input sources.

This module handles different types of input sources including files,
raw text, and structured data for keyword extraction.
"""

import logging
import os
from typing import Any, Dict, Union

from ..utils.file_utils import FileUtils
from ..utils.text_preprocessor import TextPreprocessor


class InputHandler:
    """
    Core component for handling input from files or text content.

    This class provides methods for processing input from different sources,
    including file reading, text validation, and format detection.
    """

    def handle_input(self, input_source: Union[str, Dict[str, Any]], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process and validate input from file or text content.

        Args:
            input_source: Path to a file, raw text content, or dict with text.
            options: Optional configuration parameters.

        Returns:
            Dict[str, Any]: Processed text with metadata.

        Raises:
            ValueError: If input is empty or invalid.
            FileNotFoundError: If specified file doesn't exist.
            Exception: If file type is not supported or processing fails.
        """
        if options is None:
            options = {}

        # Handle different input types
        if isinstance(input_source, str):
            return self._handle_string_input(input_source, options)
        elif isinstance(input_source, dict):
            return self._handle_dict_input(input_source, options)
        else:
            raise ValueError(f"Unsupported input type: {type(input_source)}")

    def validate_input_text(self, text: str) -> bool:
        """
        Validate input text for processing.

        Args:
            text: Text to validate.

        Returns:
            bool: True if text is valid for processing.
        """
        return FileUtils.validate_input_text(text)

    def process_text_input(self, text: str) -> Dict[str, Any]:
        """
        Process text input and return with metadata.

        Args:
            text: Text content to process.

        Returns:
            Dict[str, Any]: Processed text with metadata.
        """
        import datetime

        return {
            "text": text,
            "source_type": "text",
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def process_file_input(self, file_path: str) -> Dict[str, Any]:
        """
        Process file input and return with metadata.

        Args:
            file_path: Path to the file to process.

        Returns:
            Dict[str, Any]: Processed text with metadata.
        """
        text, file_metadata = FileUtils.extract_text_from_file(file_path)

        return {
            "text": text,
            "source_type": "file",
            "metadata": file_metadata,
        }

    def process_input(self, input_source: str, is_text: bool = False) -> Dict[str, Any]:
        """
        Process input (file or text) and return with metadata.

        Args:
            input_source: File path or text content.
            is_text: Whether the input is text content.

        Returns:
            Dict[str, Any]: Processed text with metadata.
        """
        if is_text:
            return self.process_text_input(input_source)
        else:
            return self.process_file_input(input_source)

    def _handle_string_input(self, input_source: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle string input (file path or raw text).

        Args:
            input_source: File path or raw text content.
            options: Processing options.

        Returns:
            Dict[str, Any]: Processed text with metadata.
        """
        # Check if input looks like a file path (has extension and no newlines)
        if self._looks_like_file_path(input_source):
            # Try to handle as file, will raise FileNotFoundError if file doesn't exist
            return self._handle_file_input(input_source, options)
        else:
            return self._handle_text_input(input_source, options)

    def _looks_like_file_path(self, input_source: str) -> bool:
        """
        Check if the input string looks like a file path.

        Args:
            input_source: String to check.

        Returns:
            bool: True if it looks like a file path, False otherwise.
        """
        # Check if it has a file extension
        if not any(input_source.endswith(ext) for ext in [".txt", ".md", ".markdown", ".pdf"]):
            return False

        # Check if it doesn't contain newlines (raw text would have newlines)
        if "\n" in input_source:
            return False

        # Check if it's not too long (file paths are typically short)
        if len(input_source) > 200:  # Reasonable max length for a file path
            return False

        return True

    def _handle_file_input(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle file input.

        Args:
            file_path: Path to the file.
            options: Processing options.

        Returns:
            Dict[str, Any]: Processed text with metadata.
        """
        # Extract text from file
        text, file_metadata = FileUtils.extract_text_from_file(file_path)

        # Validate extracted text
        if not FileUtils.validate_input_text(text):
            raise ValueError(f"Extracted text from {file_path} is too short or invalid")

        # Preprocess text
        preprocessed = TextPreprocessor.preprocess_text(text, detect_headers=options.get("detect_headers", True))

        # Combine metadata
        metadata = {
            **file_metadata,
            **preprocessed["metadata"],
            "input_type": "file",
            "file_path": file_path,
        }

        return {
            "text": preprocessed["text"],
            "metadata": metadata,
        }

    def _handle_text_input(self, text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle raw text input.

        Args:
            text: Raw text content.
            options: Processing options.

        Returns:
            Dict[str, Any]: Processed text with metadata.
        """
        # Validate input text
        if not FileUtils.validate_input_text(text):
            raise ValueError("Input text is too short or invalid")

        # Preprocess text
        preprocessed = TextPreprocessor.preprocess_text(text, detect_headers=options.get("detect_headers", True))

        metadata = {
            **preprocessed["metadata"],
            "input_type": "text",
            "text_length": len(text),
        }

        return {
            "text": preprocessed["text"],
            "metadata": metadata,
        }

    def _handle_dict_input(self, input_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle dictionary input.

        Args:
            input_data: Dictionary containing text and metadata.
            options: Processing options.

        Returns:
            Dict[str, Any]: Processed text with metadata.
        """
        text = input_data.get("text", "")
        if not text:
            raise ValueError("No text content found in input dictionary")

        # Validate text
        if not FileUtils.validate_input_text(text):
            raise ValueError("Text content in dictionary is too short or invalid")

        # Preprocess text
        preprocessed = TextPreprocessor.preprocess_text(text, detect_headers=options.get("detect_headers", True))

        # Combine with existing metadata
        existing_metadata = input_data.get("metadata", {})
        metadata = {
            **existing_metadata,
            **preprocessed["metadata"],
            "input_type": "dict",
        }

        return {
            "text": preprocessed["text"],
            "metadata": metadata,
        }

    def validate_input(self, input_source: Union[str, Dict[str, Any]]) -> bool:
        """
        Validate input without processing.

        Args:
            input_source: Input to validate.

        Returns:
            bool: True if input is valid.
        """
        try:
            if isinstance(input_source, str):
                if os.path.exists(input_source):
                    # Check if file format is supported
                    return FileUtils.is_supported_format(input_source)
                else:
                    # Check if it's valid text
                    return FileUtils.validate_input_text(input_source)
            elif isinstance(input_source, dict):
                text = input_source.get("text", "")
                return FileUtils.validate_input_text(text)
            else:
                return False  # type: ignore[unreachable]
        except Exception:
            return False
