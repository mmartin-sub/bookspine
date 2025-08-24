"""
Extraction result model for keyword extraction.

This module defines the data model for keyword extraction results,
including metadata and processing information.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .extraction_options import ExtractionOptions
from .keyword_result import KeywordResult


@dataclass
class ExtractionResult:
    """
    Data class for complete keyword extraction results.

    This class represents the complete results of a keyword extraction operation,
    including the extracted keywords, metadata about the extraction process,
    and the options used for extraction.

    Attributes:
        keywords (List[KeywordResult]): List of extracted keywords/phrases.
        extraction_method (str): Method used for extraction (e.g., "KeyBERT").
        timestamp (str): ISO format timestamp of when extraction was performed.
        metadata (Dict[str, Any]): Additional metadata about the extraction.
        options_used (ExtractionOptions): Options used for extraction.
    """

    keywords: List[KeywordResult]
    extraction_method: str = "KeyBERT"
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    options_used: Optional[ExtractionOptions] = None

    def __post_init__(self):
        """
        Post-initialization setup.

        This method is automatically called after the object is initialized.
        It sets up default values and validates the data.
        """
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

        if self.metadata is None:
            self.metadata = {}

        if self.options_used is None:
            self.options_used = ExtractionOptions()

        self._validate_keywords()
        self._validate_extraction_method()
        self._validate_timestamp()
        self._validate_metadata()

    def _validate_keywords(self) -> None:
        """
        Validate keywords list.

        Raises:
            ValueError: If keywords is not a list of KeywordResult objects.
        """
        if not isinstance(self.keywords, list):
            raise ValueError("keywords must be a list")

        for keyword in self.keywords:
            if not isinstance(keyword, KeywordResult):
                raise ValueError("All keywords must be KeywordResult objects")

    def _validate_extraction_method(self) -> None:
        """
        Validate extraction_method.

        Raises:
            ValueError: If extraction_method is not a string.
        """
        if not isinstance(self.extraction_method, str):
            raise ValueError("extraction_method must be a string")

        if not self.extraction_method.strip():
            raise ValueError("extraction_method cannot be empty")

    def _validate_timestamp(self) -> None:
        """
        Validate timestamp.

        Raises:
            ValueError: If timestamp is not a valid ISO format string.
        """
        if not isinstance(self.timestamp, str):
            raise ValueError("timestamp must be a string")

        try:
            datetime.fromisoformat(self.timestamp)
        except ValueError:
            raise ValueError("timestamp must be in ISO format")

    def _validate_metadata(self) -> None:
        """
        Validate metadata.

        Raises:
            ValueError: If metadata is not a dictionary.
        """
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the extraction result.
        """
        result = {
            "keywords": [keyword.to_dict() for keyword in self.keywords],
            "extraction_method": self.extraction_method,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

        if self.options_used is not None:
            result["options_used"] = self.options_used.to_dict()

        return result

    def to_json(self, indent: int = 2) -> str:
        """
        Convert to JSON string.

        Args:
            indent: Number of spaces for indentation.

        Returns:
            str: JSON string representation of the extraction result.
        """
        return json.dumps(self.to_dict(), indent=indent)

    def get_top_keywords(self, count: Optional[int] = None) -> List[KeywordResult]:
        """
        Get top keywords by relevance score.

        Args:
            count: Number of top keywords to return. If None, returns all.

        Returns:
            List[KeywordResult]: Top keywords sorted by relevance score.
        """
        sorted_keywords = sorted(self.keywords, key=lambda k: k.relevance_score, reverse=True)

        if count is None:
            return sorted_keywords

        return sorted_keywords[:count]

    def get_phrases_only(self) -> List[KeywordResult]:
        """
        Get only multi-word phrases.

        Returns:
            List[KeywordResult]: List of multi-word phrases only.
        """
        return [keyword for keyword in self.keywords if keyword.is_phrase]

    def get_header_keywords(self) -> List[KeywordResult]:
        """
        Get keywords found in headers.

        Returns:
            List[KeywordResult]: List of keywords found in headers.
        """
        return [keyword for keyword in self.keywords if keyword.from_header]

    def get_average_relevance_score(self) -> float:
        """
        Calculate average relevance score.

        Returns:
            float: Average relevance score of all keywords.
        """
        if not self.keywords:
            return 0.0

        total_score = sum(keyword.relevance_score for keyword in self.keywords)
        return total_score / len(self.keywords)

    def __str__(self) -> str:
        """
        String representation.

        Returns:
            str: String representation of the extraction result.
        """
        keyword_count = len(self.keywords)
        phrase_count = len(self.get_phrases_only())
        header_count = len(self.get_header_keywords())
        avg_score = self.get_average_relevance_score()

        return (
            f"ExtractionResult(keywords={keyword_count}, "
            f"phrases={phrase_count}, header_keywords={header_count}, "
            f"avg_score={avg_score:.3f}, method='{self.extraction_method}')"
        )
