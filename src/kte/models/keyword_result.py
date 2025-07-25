"""
Data model for individual keyword/phrase extraction results.
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class KeywordResult:
    """
    Data class for individual keyword/phrase extraction results.

    This class represents a single keyword or phrase extracted from text content,
    including its relevance score and metadata about the extraction.

    Attributes:
        phrase (str): The extracted keyword or phrase.
        relevance_score (float): Relevance score between 0.0 and 1.0.
        is_phrase (bool): Whether this is a multi-word phrase.
        from_header (bool): Whether this term was found in a header.
    """

    phrase: str
    relevance_score: float
    is_phrase: bool
    from_header: bool

    def __post_init__(self):
        """
        Post-initialization validation.

        This method is automatically called after the object is initialized.
        It validates the provided values to ensure they meet the requirements.

        Raises:
            ValueError: If any of the values are invalid.
        """
        self._validate_phrase()
        self._validate_relevance_score()
        self._validate_is_phrase()

    def _validate_phrase(self) -> None:
        """
        Validate phrase.

        Raises:
            ValueError: If phrase is empty or invalid.
        """
        if not isinstance(self.phrase, str):
            raise ValueError("Phrase must be a string")

        if not self.phrase.strip():
            raise ValueError("Phrase cannot be empty")

    def _validate_relevance_score(self) -> None:
        """
        Validate relevance score.

        Raises:
            ValueError: If relevance score is not between 0.0 and 1.0.
        """
        if not isinstance(self.relevance_score, (int, float)):
            raise ValueError("Relevance score must be a number")

        if self.relevance_score < 0.0 or self.relevance_score > 1.0:
            raise ValueError("Relevance score must be between 0.0 and 1.0")

    def _validate_is_phrase(self) -> None:
        """
        Validate is_phrase flag.

        Raises:
            ValueError: If is_phrase is not a boolean.
        """
        if not isinstance(self.is_phrase, bool):
            raise ValueError("is_phrase must be a boolean")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the keyword result.
        """
        return {
            "phrase": self.phrase,
            "relevance_score": self.relevance_score,
            "is_phrase": self.is_phrase,
            "from_header": self.from_header,
        }

    def __str__(self) -> str:
        """
        String representation.

        Returns:
            str: String representation of the keyword result.
        """
        phrase_type = "phrase" if self.is_phrase else "keyword"
        header_info = " (from header)" if self.from_header else ""
        return f"{self.phrase} ({self.relevance_score:.3f}) - {phrase_type}{header_info}"
