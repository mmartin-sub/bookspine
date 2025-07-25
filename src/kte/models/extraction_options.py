"""
Data model for keyword extraction configuration options.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ExtractionOptions:
    """
    Data class for keyword extraction configuration options.

    This class represents the configuration options for keyword extraction,
    including parameters for KeyBERT, header weighting, and output formatting.

    Attributes:
        max_keywords (int): Maximum number of keywords to return.
        min_relevance (float): Minimum relevance score threshold.
        header_weight_factor (float): Factor to increase relevance for header terms.
        prefer_phrases (bool): Whether to prioritize multi-word phrases.
        language (str): Language of the input text.
    """

    max_keywords: int = 20
    min_relevance: float = 0.1
    header_weight_factor: float = 1.5
    prefer_phrases: bool = True
    language: str = "english"

    def __post_init__(self):
        """
        Post-initialization validation.

        This method is automatically called after the object is initialized.
        It validates the provided values to ensure they meet the requirements.

        Raises:
            ValueError: If any of the values are invalid.
        """
        self._validate_max_keywords()
        self._validate_min_relevance()
        self._validate_header_weight_factor()
        self._validate_prefer_phrases()
        self._validate_language()

    def _validate_max_keywords(self) -> None:
        """
        Validate max_keywords.

        Raises:
            ValueError: If max_keywords is not a positive integer.
        """
        if not isinstance(self.max_keywords, int):
            raise ValueError("max_keywords must be an integer")

        if self.max_keywords <= 0:
            raise ValueError("max_keywords must be positive")

        if self.max_keywords > 100:
            raise ValueError("max_keywords cannot exceed 100")

    def _validate_min_relevance(self) -> None:
        """
        Validate min_relevance.

        Raises:
            ValueError: If min_relevance is not between 0.0 and 1.0.
        """
        if not isinstance(self.min_relevance, (int, float)):
            raise ValueError("min_relevance must be a number")

        if self.min_relevance < 0.0 or self.min_relevance > 1.0:
            raise ValueError("min_relevance must be between 0.0 and 1.0")

    def _validate_header_weight_factor(self) -> None:
        """
        Validate header_weight_factor.

        Raises:
            ValueError: If header_weight_factor is not a positive number.
        """
        if not isinstance(self.header_weight_factor, (int, float)):
            raise ValueError("header_weight_factor must be a number")

        if self.header_weight_factor <= 0.0:
            raise ValueError("header_weight_factor must be positive")

        if self.header_weight_factor > 5.0:
            raise ValueError("header_weight_factor cannot exceed 5.0")

    def _validate_prefer_phrases(self) -> None:
        """
        Validate prefer_phrases.

        Raises:
            ValueError: If prefer_phrases is not a boolean.
        """
        if not isinstance(self.prefer_phrases, bool):
            raise ValueError("prefer_phrases must be a boolean")

    def _validate_language(self) -> None:
        """
        Validate language.

        Raises:
            ValueError: If language is not a valid language code.
        """
        if not isinstance(self.language, str):
            raise ValueError("language must be a string")

        if not self.language.strip():
            raise ValueError("language cannot be empty")

        # Convert to lowercase for consistency
        self.language = self.language.lower()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the extraction options.
        """
        return {
            "max_keywords": self.max_keywords,
            "min_relevance": self.min_relevance,
            "header_weight_factor": self.header_weight_factor,
            "prefer_phrases": self.prefer_phrases,
            "language": self.language,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtractionOptions":
        """
        Create ExtractionOptions from dictionary.

        Args:
            data: Dictionary containing extraction options.

        Returns:
            ExtractionOptions: New ExtractionOptions instance.

        Raises:
            ValueError: If dictionary contains invalid data.
        """
        return cls(**data)

    def __str__(self) -> str:
        """
        String representation.

        Returns:
            str: String representation of the extraction options.
        """
        return (
            f"ExtractionOptions(max_keywords={self.max_keywords}, "
            f"min_relevance={self.min_relevance}, "
            f"header_weight_factor={self.header_weight_factor}, "
            f"prefer_phrases={self.prefer_phrases}, "
            f"language='{self.language}')"
        )
