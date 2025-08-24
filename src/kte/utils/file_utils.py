"""
Utility functions for file handling and format detection.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class FileUtils:
    """
    Utility class for file handling and format detection.

    This class provides methods for detecting file formats, extracting text
    from different file types, and handling file operations.
    """

    SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt", ".pdf"}

    @staticmethod
    def detect_file_format(file_path: str) -> str:
        """
        Detect the format of a file based on its extension.

        Args:
            file_path: Path to the file.

        Returns:
            str: File format (md, txt, pdf, or unknown).

        Raises:
            ValueError: If file path is invalid.
        """
        if not file_path:
            raise ValueError("File path cannot be empty")

        path = Path(file_path)
        extension = path.suffix.lower()

        if extension in {".md", ".markdown"}:
            return "md"
        elif extension == ".txt":
            return "txt"
        elif extension == ".pdf":
            return "pdf"
        else:
            return "unknown"

    @staticmethod
    def is_supported_format(file_path: str) -> bool:
        """
        Check if the file format is supported.

        Args:
            file_path: Path to the file.

        Returns:
            bool: True if the format is supported, False otherwise.
        """
        format_type = FileUtils.detect_file_format(file_path)
        return format_type != "unknown"

    @staticmethod
    def extract_text_from_file(file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text content from a file.

        Args:
            file_path: Path to the file.

        Returns:
            Tuple[str, Dict[str, Any]]: Extracted text and metadata.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file format is not supported.
            Exception: If text extraction fails.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        format_type = FileUtils.detect_file_format(file_path)
        if format_type == "unknown":
            raise ValueError(f"Unsupported file format: {file_path}")

        metadata = {
            "file_path": file_path,
            "file_format": format_type,
            "file_size": os.path.getsize(file_path),
        }

        try:
            if format_type == "md":
                return FileUtils._extract_markdown_text(file_path), metadata
            elif format_type == "txt":
                return FileUtils._extract_plain_text(file_path), metadata
            elif format_type == "pdf":
                return FileUtils._extract_pdf_text(file_path), metadata
            else:
                raise ValueError(f"Unsupported file format: {format_type}")
        except Exception as e:
            raise Exception(f"Failed to extract text from {file_path}: {str(e)}")

    @staticmethod
    def _extract_markdown_text(file_path: str) -> str:
        """
        Extract text from a Markdown file.

        Args:
            file_path: Path to the Markdown file.

        Returns:
            str: Extracted text content.
        """
        import markdown

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Convert markdown to HTML first, then extract text
        html = markdown.markdown(content)

        # Simple HTML tag removal (for basic text extraction)
        import re

        text = re.sub(r"<[^>]+>", "", html)
        text = re.sub(r"\n\s*\n", "\n\n", text)  # Normalize line breaks

        return text.strip()

    @staticmethod
    def _extract_plain_text(file_path: str) -> str:
        """
        Extract text from a plain text file.

        Args:
            file_path: Path to the text file.

        Returns:
            str: Extracted text content.
        """
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        return content.strip()

    @staticmethod
    def _extract_pdf_text(file_path: str) -> str:
        """
        Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file.

        Returns:
            str: Extracted text content.
        """
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError("pypdf is required for PDF text extraction")

        reader = PdfReader(file_path)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        return "\n".join(text_parts).strip()

    @staticmethod
    def validate_input_text(text: Optional[str]) -> bool:
        """
        Validate input text for processing.

        Args:
            text: Text content to validate.

        Returns:
            bool: True if text is valid for processing.
        """
        # Check all conditions and return result
        return isinstance(text, str) and len(text.strip()) >= 10

    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.

        Args:
            file_path: Path to the file.

        Returns:
            Dict[str, Any]: File information.
        """
        path = Path(file_path)

        return {
            "name": path.name,
            "extension": path.suffix.lower(),
            "format": FileUtils.detect_file_format(file_path),
            "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "exists": os.path.exists(file_path),
        }
