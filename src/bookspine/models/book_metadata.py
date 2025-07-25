"""
Data models for book metadata.

This module contains the BookMetadata class which represents the metadata
of a book needed for spine width calculation.
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


class BookMetadataError(Exception):
    """Base exception for all book metadata related errors."""

    pass


class ValidationError(BookMetadataError):
    """Raised when book metadata validation fails."""

    pass


@dataclass
class BookMetadata:
    """
    Data class for book metadata.

    This class represents the metadata of a book needed for spine width calculation.
    It includes fields for page count, paper type, binding type, paper weight, and
    preferred unit system.

    Attributes:
        page_count (int): Total number of pages in the book.
        paper_type (Optional[str]): Type of paper (e.g., "MCG", "MCS", "ECB", "OFF").
        binding_type (Optional[str]): Type of binding (e.g., "Softcover Perfect Bound").
        paper_weight (Optional[float]): Weight of paper in gsm (Grams per Square Meter).
        unit_system (str): Preferred unit system ("metric" or "imperial").
    """

    # Valid values for paper_type and binding_type
    VALID_PAPER_TYPES = ["MCG", "MCS", "ECB", "OFF"]
    VALID_BINDING_TYPES = ["Softcover Perfect Bound", "Hardcover Casewrap", "Hardcover Linen"]
    VALID_UNIT_SYSTEMS = ["metric", "imperial"]

    # Paper weight bounds
    MIN_PAPER_WEIGHT = 50
    MAX_PAPER_WEIGHT = 300

    page_count: int
    paper_type: Optional[str] = None
    binding_type: Optional[str] = None
    paper_weight: Optional[float] = None
    unit_system: str = "metric"

    def __post_init__(self):
        """
        Post-initialization validation.

        This method is automatically called after the object is initialized.
        It validates the provided values to ensure they meet the requirements.

        Raises:
            ValidationError: If any of the values are invalid.
        """
        try:
            self.validate()
        except ValueError as e:
            raise ValidationError(str(e))

    def validate(self) -> None:
        """
        Validate book metadata.

        This method validates all fields of the book metadata to ensure they
        meet the requirements. It checks that:
        - page_count is positive
        - paper_type is one of the valid types
        - binding_type is one of the valid types
        - paper_weight is within reasonable bounds
        - unit_system is one of the valid systems

        Raises:
            ValueError: If validation fails for any field.
        """
        self._validate_page_count()
        self._validate_paper_type()
        self._validate_binding_type()
        self._validate_paper_weight()
        self._validate_unit_system()

    def _validate_page_count(self) -> None:
        """
        Validate page count.

        Raises:
            ValueError: If page count is not positive.
        """
        if not isinstance(self.page_count, int):
            raise ValueError("Page count must be an integer")

        if self.page_count <= 0:
            raise ValueError("Page count must be positive")

    def _validate_paper_type(self) -> None:
        """
        Validate paper type.

        Raises:
            ValueError: If paper type is not one of the valid types.
        """
        if self.paper_type is not None and self.paper_type not in self.VALID_PAPER_TYPES:
            valid_types = ", ".join(self.VALID_PAPER_TYPES)
            raise ValueError(f"Invalid paper type. Valid types are: {valid_types}")

    def _validate_binding_type(self) -> None:
        """
        Validate binding type.

        Raises:
            ValueError: If binding type is not one of the valid types.
        """
        if self.binding_type is not None and self.binding_type not in self.VALID_BINDING_TYPES:
            valid_types = ", ".join(self.VALID_BINDING_TYPES)
            raise ValueError(f"Invalid binding type. Valid types are: {valid_types}")

    def _validate_paper_weight(self) -> None:
        """
        Validate paper weight.

        This method checks if the paper weight is within reasonable bounds.
        If it's outside the bounds, it prints a warning but doesn't raise an error.

        Raises:
            ValueError: If paper weight is not a positive number.
        """
        if self.paper_weight is not None:
            if not isinstance(self.paper_weight, (int, float)):
                raise ValueError("Paper weight must be a number")

            if self.paper_weight <= 0:
                raise ValueError("Paper weight must be positive")

            if self.paper_weight < self.MIN_PAPER_WEIGHT or self.paper_weight > self.MAX_PAPER_WEIGHT:
                print(
                    f"Warning: Paper weight {self.paper_weight} gsm is outside typical range "
                    f"({self.MIN_PAPER_WEIGHT}-{self.MAX_PAPER_WEIGHT} gsm)"
                )

    def _validate_unit_system(self) -> None:
        """
        Validate unit system.

        Raises:
            ValueError: If unit system is not one of the valid systems.
        """
        if self.unit_system not in self.VALID_UNIT_SYSTEMS:
            valid_systems = ", ".join(self.VALID_UNIT_SYSTEMS)
            raise ValueError(f"Invalid unit system. Valid systems are: {valid_systems}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the book metadata.
        """
        return asdict(self)

    def is_complete(self) -> bool:
        """
        Check if all required fields for calculation are provided.

        Returns:
            bool: True if all required fields are provided, False otherwise.
        """
        return (
            self.page_count is not None
            and self.paper_type is not None
            and self.binding_type is not None
            and self.paper_weight is not None
        )
