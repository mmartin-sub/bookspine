"""
Utility functions for text preprocessing and header detection.
"""

import re
from typing import Any, Dict, List, Optional, Tuple


class TextPreprocessor:
    """
    Utility class for text preprocessing and header detection.

    This class provides methods for normalizing text, identifying structural
    elements like headers, and preparing text for keyword extraction.
    """

    # Header patterns for different formats
    HEADER_PATTERNS = {
        "markdown": [
            r"^#{1,6}\s+(.+)$",  # # Header, ## Header, etc.
            r"^(.+)\n={3,}$",  # Header\n=====
            r"^(.+)\n-{3,}$",  # Header\n-----
        ],
        "html": [
            r"<h[1-6][^>]*>(.+?)</h[1-6]>",  # <h1>Header</h1>
        ],
        "plain": [
            r"^([A-Z][A-Z\s]+)$",  # ALL CAPS lines
            r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)$",  # Title Case lines
        ],
    }

    @staticmethod
    def preprocess_text(text: str, detect_headers: bool = True) -> Dict[str, Any]:
        """
        Preprocess text for keyword extraction.

        Args:
            text: Raw text content.
            detect_headers: Whether to detect and tag headers.

        Returns:
            Dict[str, Any]: Preprocessed text with metadata.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Normalize text
        normalized_text = TextPreprocessor._normalize_text(text)

        # Detect headers if requested
        headers = []
        if detect_headers:
            headers = TextPreprocessor._detect_headers(normalized_text)

        # Create metadata
        metadata = {
            "original_length": len(text),
            "normalized_length": len(normalized_text),
            "header_count": len(headers),
            "headers": headers,
        }

        return {
            "text": normalized_text,
            "metadata": metadata,
        }

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for consistent processing.

        Args:
            text: Raw text content.

        Returns:
            str: Normalized text.
        """
        return TextPreprocessor._normalize_text(text)

    @staticmethod
    def detect_headers(text: str) -> List[Dict[str, Any]]:
        """
        Detect headers in text using various patterns.

        Args:
            text: Text content to analyze.

        Returns:
            List[Dict[str, Any]]: List of detected headers with metadata.
        """
        return TextPreprocessor._detect_headers(text)

    @staticmethod
    def identify_structural_elements(text: str) -> Dict[str, Any]:
        """
        Identify structural elements in text.

        Args:
            text: Text content to analyze.

        Returns:
            Dict[str, Any]: Structural elements with metadata.
        """
        headers = TextPreprocessor._detect_headers(text)

        return {
            "headers": headers,
            "header_count": len(headers),
            "has_structure": len(headers) > 0,
        }

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize text for consistent processing.

        Args:
            text: Raw text content.

        Returns:
            str: Normalized text.
        """
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Normalize line breaks
        text = re.sub(r"\n\s*\n", "\n\n", text)

        # Remove special characters that might interfere with processing
        text = re.sub(r"[^\w\s\-.,!?;:()]", "", text)

        # Normalize quotes and apostrophes
        text = re.sub(r"[''" "]", "'", text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    @staticmethod
    def _detect_headers(text: str) -> List[Dict[str, Any]]:
        """
        Detect headers in text using various patterns.

        Args:
            text: Text content to analyze.

        Returns:
            List[Dict[str, Any]]: List of detected headers with metadata.
        """
        headers = []
        lines = text.split("\n")

        for line_num, line in enumerate(lines):
            header_info = TextPreprocessor._check_header_line(line, line_num)
            if header_info:
                headers.append(header_info)

        return headers

    @staticmethod
    def _check_header_line(line: str, line_num: int) -> Optional[Dict[str, Any]]:
        """
        Check if a line is a header.

        Args:
            line: Line to check.
            line_num: Line number in the text.

        Returns:
            Dict[str, Any]: Header information if found, None otherwise.
        """
        line = line.strip()
        if not line:
            return None

        # Check markdown headers
        md_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if md_match:
            level = len(md_match.group(1))
            content = md_match.group(2).strip()
            return {
                "content": content,
                "level": level,
                "type": "markdown",
                "line": line_num,
                "original": line,
            }

        # Check HTML headers
        html_match = re.match(r"<h([1-6])[^>]*>(.+?)</h\1>", line)
        if html_match:
            level = int(html_match.group(1))
            content = html_match.group(2).strip()
            return {
                "content": content,
                "level": level,
                "type": "html",
                "line": line_num,
                "original": line,
            }

        # Check plain text headers (ALL CAPS)
        if line.isupper() and len(line.split()) <= 5:
            return {
                "content": line,
                "level": 1,
                "type": "plain",
                "line": line_num,
                "original": line,
            }

        # Check title case headers
        if TextPreprocessor._is_title_case(line) and len(line.split()) <= 8:
            return {
                "content": line,
                "level": 2,
                "type": "plain",
                "line": line_num,
                "original": line,
            }

        return None

    @staticmethod
    def _is_title_case(text: str) -> bool:
        """
        Check if text is in title case.

        Args:
            text: Text to check.

        Returns:
            bool: True if text is in title case.
        """
        words = text.split()
        if not words:
            return False

        # Check if first word starts with capital letter
        if not words[0][0].isupper():
            return False

        # Check if other words are properly capitalized
        for word in words[1:]:
            if word.lower() in ["a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]:
                # Prepositions and articles should be lowercase
                if word.isupper() or word[0].isupper():
                    return False
            else:
                # Other words should be capitalized
                if not word[0].isupper():
                    return False

        return True

    @staticmethod
    def extract_header_terms(headers: List[Dict[str, Any]]) -> List[str]:
        """
        Extract terms from headers for weighting.

        Args:
            headers: List of header information.

        Returns:
            List[str]: List of terms found in headers.
        """
        terms = []

        for header in headers:
            content = header["content"]

            # Split content into words and normalize
            words = re.findall(r"\b\w+\b", content.lower())

            # Filter out common stop words
            stop_words = {
                "the",
                "a",
                "an",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
                "is",
                "are",
                "was",
                "were",
                "be",
                "been",
                "being",
                "have",
                "has",
                "had",
                "do",
                "does",
                "did",
                "will",
                "would",
                "could",
                "should",
                "may",
                "might",
                "can",
                "this",
                "that",
                "these",
                "those",
            }

            for word in words:
                if word not in stop_words and len(word) > 2:
                    terms.append(word)

        return list(set(terms))  # Remove duplicates

    @staticmethod
    def get_header_weight(header_level: int) -> float:
        """
        Get weight factor for header level.

        Args:
            header_level: Header level (1-6).

        Returns:
            float: Weight factor for the header level.
        """
        # Higher level headers (lower numbers) get higher weights
        if header_level == 1:
            return 2.0
        elif header_level == 2:
            return 1.5
        elif header_level == 3:
            return 1.3
        elif header_level == 4:
            return 1.2
        elif header_level == 5:
            return 1.1
        else:
            return 1.0
