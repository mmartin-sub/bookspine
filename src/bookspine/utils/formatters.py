"""
Output formatting utilities for spine calculation results.

This module provides utilities for formatting spine calculation results
in various output formats including text, JSON, and CSV.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.spine_result import SpineResult


def format_output(result: "SpineResult", format_type: str = "text") -> str:
    """
    Format spine calculation results for display or export.

    This function takes a SpineResult object and formats it according to the
    specified format type. It supports text (human-readable), JSON (machine-readable),
    and CSV (spreadsheet-compatible) formats.

    Args:
        result (SpineResult): The spine calculation result object to format.
        format_type (str, optional): The desired output format. Must be one of:
            - "text": Human-readable text format (default)
            - "json": JSON format for machine processing
            - "csv": CSV format for spreadsheet applications

    Returns:
        str: The formatted output string ready for display or file output.

    Raises:
        AttributeError: If the result object doesn't have required methods.

    Example:
        >>> from bookspine.models.spine_result import SpineResult
        >>> from bookspine.models.book_metadata import BookMetadata
        >>> metadata = BookMetadata(page_count=200)
        >>> result = SpineResult(width_mm=10.5, width_inches=0.41,
        ...                     width_pixels=125.0, dpi=300, book_metadata=metadata)
        >>> formatted = format_output(result, "text")
        >>> print(formatted)
        Book Spine Calculator Results
        ===========================
        Spine Width: 10.50 mm
        ...
    """
    if format_type == "json":
        return result.to_json()
    elif format_type == "csv":
        return result.to_csv()
    else:  # text
        output = []
        output.append("Book Spine Calculator Results")
        output.append("===========================")
        output.append(f"Spine Width: {result.width_mm:.2f} mm")
        output.append(f"Spine Width: {result.width_inches:.2f} inches")
        output.append(f"Spine Width: {result.width_pixels:.2f} pixels at {result.dpi} DPI")

        if result.manual_override_applied:
            output.append(
                f"Note: Manual override applied. Original calculated width: "
                f"{result.original_calculated_width_mm:.2f} mm"
            )

        output.append("\nInput Parameters:")
        output.append(f"Page Count: {result.book_metadata.page_count}")

        if result.book_metadata.paper_type:
            output.append(f"Paper Type: {result.book_metadata.paper_type}")

        if result.book_metadata.binding_type:
            output.append(f"Binding Type: {result.book_metadata.binding_type}")

        if result.book_metadata.paper_weight:
            output.append(f"Paper Weight: {result.book_metadata.paper_weight} gsm")

        output.append(f"Unit System: {result.book_metadata.unit_system}")

        if result.printer_service:
            output.append(f"Printer Service: {result.printer_service}")

        return "\n".join(output)
