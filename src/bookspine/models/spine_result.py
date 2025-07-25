"""
Data models for spine calculation results.

This module contains the SpineResult class which represents the results
of spine width calculations with support for multiple output formats.
"""

import csv
import io
import json
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .book_metadata import BookMetadata


@dataclass
class SpineResult:
    """
    Data class for spine calculation results.

    This class represents the results of a spine width calculation, including
    the calculated dimensions in multiple units (mm, inches, pixels) and
    metadata about the calculation process.

    Attributes:
        width_mm (float): Spine width in millimeters.
        width_inches (float): Spine width in inches.
        width_pixels (float): Spine width in pixels at specified DPI.
        dpi (int): DPI used for pixel conversion.
        book_metadata (BookMetadata): Original book metadata used for calculation.
        printer_service (Optional[str]): Name of printer service used, if any.
        manual_override_applied (bool): Whether a manual override was applied.
        original_calculated_width_mm (Optional[float]): Original calculated width before override.
    """

    width_mm: float
    width_inches: float
    width_pixels: float
    dpi: int
    book_metadata: "BookMetadata"
    printer_service: Optional[str] = None
    manual_override_applied: bool = False
    original_calculated_width_mm: Optional[float] = None

    def __post_init__(self):
        """Post-initialization validation."""
        self._validate_dimensions()

    def _validate_dimensions(self) -> None:
        """
        Validate that all dimensions are positive numbers.

        Raises:
            ValueError: If any dimension is not a positive number.
        """
        if not isinstance(self.width_mm, (int, float)) or self.width_mm <= 0:
            raise ValueError("Width in mm must be a positive number")

        if not isinstance(self.width_inches, (int, float)) or self.width_inches <= 0:
            raise ValueError("Width in inches must be a positive number")

        if not isinstance(self.width_pixels, (int, float)) or self.width_pixels <= 0:
            raise ValueError("Width in pixels must be a positive number")

        if not isinstance(self.dpi, int) or self.dpi <= 0:
            raise ValueError("DPI must be a positive integer")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the result with
                          nested book_metadata as a dictionary.
        """
        result = asdict(self)
        # Convert book_metadata to dict for better serialization
        if hasattr(self.book_metadata, "to_dict"):
            result["book_metadata"] = self.book_metadata.to_dict()
        else:
            result["book_metadata"] = asdict(self.book_metadata)
        return result

    def to_json(self, indent: int = 2) -> str:
        """
        Convert to JSON string.

        Args:
            indent (int): Number of spaces for JSON indentation. Defaults to 2.

        Returns:
            str: JSON representation of the result.
        """
        return json.dumps(self.to_dict(), indent=indent)

    def to_csv(self, include_headers: bool = True) -> str:
        """
        Convert to CSV format.

        Args:
            include_headers (bool): Whether to include CSV headers. Defaults to True.

        Returns:
            str: CSV representation of the result.
        """
        headers = [
            "width_mm",
            "width_inches",
            "width_pixels",
            "dpi",
            "page_count",
            "paper_type",
            "binding_type",
            "paper_weight",
            "unit_system",
            "printer_service",
            "manual_override_applied",
            "original_calculated_width_mm",
        ]

        values = [
            f"{self.width_mm:.3f}",
            f"{self.width_inches:.4f}",
            f"{self.width_pixels:.1f}",
            str(self.dpi),
            str(self.book_metadata.page_count),
            self.book_metadata.paper_type or "",
            self.book_metadata.binding_type or "",
            f"{self.book_metadata.paper_weight:.1f}" if self.book_metadata.paper_weight else "",
            self.book_metadata.unit_system,
            self.printer_service or "",
            "Yes" if self.manual_override_applied else "No",
            f"{self.original_calculated_width_mm:.3f}" if self.original_calculated_width_mm else "",
        ]

        # Use proper CSV formatting to handle commas and quotes in values
        output = io.StringIO()
        writer = csv.writer(output)

        if include_headers:
            writer.writerow(headers)
        writer.writerow(values)

        return output.getvalue().strip()

    def get_formatted_summary(self) -> str:
        """
        Get a human-readable summary of the spine calculation results.

        Returns:
            str: Formatted summary string.
        """
        lines = [
            "Spine Width Calculation Results",
            "=" * 32,
            f"Width: {self.width_mm:.3f} mm ({self.width_inches:.4f} inches)",
            f"Pixels: {self.width_pixels:.1f} px at {self.dpi} DPI",
            "",
            "Input Parameters:",
            f"  Page Count: {self.book_metadata.page_count}",
            f"  Paper Type: {self.book_metadata.paper_type or 'Not specified'}",
            f"  Binding Type: {self.book_metadata.binding_type or 'Not specified'}",
            f"  Paper Weight: {self.book_metadata.paper_weight or 'Not specified'} gsm",
            f"  Unit System: {self.book_metadata.unit_system}",
        ]

        if self.printer_service:
            lines.append(f"  Printer Service: {self.printer_service}")

        if self.manual_override_applied:
            lines.extend(
                [
                    "",
                    "Manual Override Applied:",
                    f"  Original Calculated Width: {self.original_calculated_width_mm:.3f} mm",
                    f"  Override Width: {self.width_mm:.3f} mm",
                ]
            )

        return "\n".join(lines)

    def get_formatted_output(self, format_type: str) -> str:
        """
        Return the result in the specified output format.

        Args:
            format_type (str): Output format ('text', 'json', 'csv').

        Returns:
            str: Formatted output string.

        Raises:
            ValueError: If the format_type is not supported.
        """
        format_type = format_type.lower()
        if format_type == "text":
            return self.get_formatted_summary()
        elif format_type == "json":
            return self.to_json()
        elif format_type == "csv":
            return self.to_csv()
        else:
            raise ValueError(f"Unsupported output format: {format_type}")
