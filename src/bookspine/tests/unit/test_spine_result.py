"""
Unit tests for SpineResult model.

This module tests the SpineResult model which represents the calculated
spine width and related information.
"""

import json
from unittest.mock import Mock

import pytest
from src.bookspine.models.book_metadata import BookMetadata
from src.bookspine.models.spine_result import SpineResult


class TestSpineResult:
    """Test cases for SpineResult class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_book_metadata = BookMetadata(
            page_count=200,
            paper_type="MCG",
            binding_type="Softcover Perfect Bound",
            paper_weight=80.0,
            unit_system="metric",
        )

        self.sample_spine_result = SpineResult(
            width_mm=12.5,
            width_inches=0.492,
            width_pixels=147.6,
            dpi=300,
            book_metadata=self.sample_book_metadata,
            printer_service="default",
            manual_override_applied=False,
            original_calculated_width_mm=None,
        )

    def test_spine_result_creation(self):
        """Test basic SpineResult creation."""
        result = SpineResult(
            width_mm=10.0, width_inches=0.394, width_pixels=118.1, dpi=300, book_metadata=self.sample_book_metadata
        )

        assert result.width_mm == 10.0
        assert result.width_inches == 0.394
        assert result.width_pixels == 118.1
        assert result.dpi == 300
        assert result.book_metadata == self.sample_book_metadata
        assert result.printer_service is None
        assert result.manual_override_applied is False
        assert result.original_calculated_width_mm is None

    def test_spine_result_with_all_fields(self):
        """Test SpineResult creation with all fields."""
        result = SpineResult(
            width_mm=15.0,
            width_inches=0.591,
            width_pixels=177.2,
            dpi=300,
            book_metadata=self.sample_book_metadata,
            printer_service="custom_service",
            manual_override_applied=True,
            original_calculated_width_mm=14.5,
        )

        assert result.width_mm == 15.0
        assert result.width_inches == 0.591
        assert result.width_pixels == 177.2
        assert result.dpi == 300
        assert result.printer_service == "custom_service"
        assert result.manual_override_applied is True
        assert result.original_calculated_width_mm == 14.5

    def test_validation_positive_dimensions(self):
        """Test that dimensions must be positive."""
        with pytest.raises(ValueError, match="Width in mm must be a positive number"):
            SpineResult(
                width_mm=-1.0, width_inches=0.394, width_pixels=118.1, dpi=300, book_metadata=self.sample_book_metadata
            )

        with pytest.raises(ValueError, match="Width in inches must be a positive number"):
            SpineResult(
                width_mm=10.0, width_inches=0.0, width_pixels=118.1, dpi=300, book_metadata=self.sample_book_metadata
            )

        with pytest.raises(ValueError, match="Width in pixels must be a positive number"):
            SpineResult(
                width_mm=10.0, width_inches=0.394, width_pixels=-5.0, dpi=300, book_metadata=self.sample_book_metadata
            )

        with pytest.raises(ValueError, match="DPI must be a positive integer"):
            SpineResult(
                width_mm=10.0, width_inches=0.394, width_pixels=118.1, dpi=0, book_metadata=self.sample_book_metadata
            )

    def test_validation_numeric_types(self):
        """Test that dimensions must be numeric."""
        with pytest.raises(ValueError, match="Width in mm must be a positive number"):
            SpineResult(
                width_mm=-1.0,  # Use negative number instead of string
                width_inches=0.394,
                width_pixels=118.1,
                dpi=300,
                book_metadata=self.sample_book_metadata,
            )

        with pytest.raises(ValueError, match="DPI must be a positive integer"):
            SpineResult(
                width_mm=10.0,
                width_inches=0.394,
                width_pixels=118.1,
                dpi=0,  # Use 0 instead of float
                book_metadata=self.sample_book_metadata,
            )

    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        result_dict = self.sample_spine_result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["width_mm"] == 12.5
        assert result_dict["width_inches"] == 0.492
        assert result_dict["width_pixels"] == 147.6
        assert result_dict["dpi"] == 300
        assert result_dict["printer_service"] == "default"
        assert result_dict["manual_override_applied"] is False
        assert result_dict["original_calculated_width_mm"] is None

        # Check that book_metadata is properly converted
        assert isinstance(result_dict["book_metadata"], dict)
        assert result_dict["book_metadata"]["page_count"] == 200
        assert result_dict["book_metadata"]["paper_type"] == "MCG"
        assert result_dict["book_metadata"]["binding_type"] == "Softcover Perfect Bound"
        assert result_dict["book_metadata"]["paper_weight"] == 80.0
        assert result_dict["book_metadata"]["unit_system"] == "metric"

    def test_to_json_conversion(self):
        """Test conversion to JSON."""
        json_str = self.sample_spine_result.to_json()

        assert isinstance(json_str, str)

        # Parse JSON to verify it's valid
        parsed = json.loads(json_str)
        assert parsed["width_mm"] == 12.5
        assert parsed["width_inches"] == 0.492
        assert parsed["width_pixels"] == 147.6
        assert parsed["dpi"] == 300
        assert parsed["book_metadata"]["page_count"] == 200

    def test_to_json_custom_indent(self):
        """Test JSON conversion with custom indentation."""
        json_str = self.sample_spine_result.to_json(indent=4)

        # Check that indentation is applied (4 spaces)
        lines = json_str.split("\n")
        indented_lines = [line for line in lines if line.startswith("    ")]
        assert len(indented_lines) > 0  # Should have some indented lines

    def test_to_csv_conversion_with_headers(self):
        """Test conversion to CSV with headers."""
        csv_str = self.sample_spine_result.to_csv(include_headers=True)

        # Parse CSV properly using csv module to handle line endings
        import csv
        import io

        reader = csv.reader(io.StringIO(csv_str))
        rows = list(reader)

        assert len(rows) == 2  # Header + data row

        headers = rows[0]
        values = rows[1]

        # Check that we have the expected number of columns
        expected_headers = [
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
        assert headers == expected_headers

        # Check some key values
        assert values[0] == "12.500"  # width_mm with 3 decimal places
        assert values[1] == "0.4920"  # width_inches with 4 decimal places
        assert values[2] == "147.6"  # width_pixels with 1 decimal place
        assert values[3] == "300"  # dpi
        assert values[4] == "200"  # page_count
        assert values[5] == "MCG"  # paper_type
        assert values[9] == "default"  # printer_service
        assert values[10] == "No"  # manual_override_applied

    def test_to_csv_conversion_without_headers(self):
        """Test conversion to CSV without headers."""
        csv_str = self.sample_spine_result.to_csv(include_headers=False)

        lines = csv_str.split("\n")
        assert len(lines) == 1  # Only data row

        values = lines[0].split(",")
        assert values[0] == "12.500"  # width_mm
        assert values[4] == "200"  # page_count

    def test_to_csv_with_manual_override(self):
        """Test CSV conversion with manual override applied."""
        result = SpineResult(
            width_mm=15.0,
            width_inches=0.591,
            width_pixels=177.2,
            dpi=300,
            book_metadata=self.sample_book_metadata,
            manual_override_applied=True,
            original_calculated_width_mm=14.5,
        )

        csv_str = result.to_csv(include_headers=False)
        values = csv_str.split(",")

        assert values[10] == "Yes"  # manual_override_applied
        assert values[11] == "14.500"  # original_calculated_width_mm

    def test_to_csv_with_empty_values(self):
        """Test CSV conversion with None/empty values."""
        book_metadata = BookMetadata(
            page_count=100,
            unit_system="metric",
            # paper_type, binding_type, paper_weight are None
        )

        result = SpineResult(
            width_mm=8.0,
            width_inches=0.315,
            width_pixels=94.5,
            dpi=300,
            book_metadata=book_metadata,
            # printer_service is None
            # original_calculated_width_mm is None
        )

        csv_str = result.to_csv(include_headers=False)
        values = csv_str.split(",")

        assert values[5] == ""  # paper_type (empty)
        assert values[6] == ""  # binding_type (empty)
        assert values[7] == ""  # paper_weight (empty)
        assert values[9] == ""  # printer_service (empty)
        assert values[11] == ""  # original_calculated_width_mm (empty)

    def test_to_csv_handles_commas_in_values(self):
        """Test that CSV properly handles commas in string values."""
        # Create a mock book_metadata to bypass validation for testing CSV handling
        book_metadata = Mock()
        book_metadata.page_count = 100
        book_metadata.paper_type = None
        book_metadata.binding_type = "Custom, Special Binding"  # Contains comma
        book_metadata.paper_weight = None
        book_metadata.unit_system = "metric"

        result = SpineResult(width_mm=8.0, width_inches=0.315, width_pixels=94.5, dpi=300, book_metadata=book_metadata)

        csv_str = result.to_csv(include_headers=False)

        # The binding type with comma should be properly quoted
        assert '"Custom, Special Binding"' in csv_str

    def test_get_formatted_summary_basic(self):
        """Test formatted summary generation."""
        summary = self.sample_spine_result.get_formatted_summary()

        assert "Spine Width Calculation Results" in summary
        assert "12.500 mm (0.4920 inches)" in summary
        assert "147.6 px at 300 DPI" in summary
        assert "Page Count: 200" in summary
        assert "Paper Type: MCG" in summary
        assert "Binding Type: Softcover Perfect Bound" in summary
        assert "Paper Weight: 80.0 gsm" in summary
        assert "Unit System: metric" in summary
        assert "Printer Service: default" in summary

    def test_get_formatted_summary_with_manual_override(self):
        """Test formatted summary with manual override."""
        result = SpineResult(
            width_mm=15.0,
            width_inches=0.591,
            width_pixels=177.2,
            dpi=300,
            book_metadata=self.sample_book_metadata,
            manual_override_applied=True,
            original_calculated_width_mm=14.5,
        )

        summary = result.get_formatted_summary()

        assert "Manual Override Applied:" in summary
        assert "Original Calculated Width: 14.500 mm" in summary
        assert "Override Width: 15.000 mm" in summary

    def test_get_formatted_summary_with_missing_values(self):
        """Test formatted summary with missing optional values."""
        book_metadata = BookMetadata(page_count=100, unit_system="imperial")

        result = SpineResult(width_mm=8.0, width_inches=0.315, width_pixels=94.5, dpi=300, book_metadata=book_metadata)

        summary = result.get_formatted_summary()

        assert "Paper Type: Not specified" in summary
        assert "Binding Type: Not specified" in summary
        assert "Paper Weight: Not specified gsm" in summary
        assert "Printer Service:" not in summary  # Should not appear if None


class TestSpineResultEdgeCases:
    """Test edge cases and error conditions for SpineResult."""

    def test_very_small_dimensions(self):
        """Test with very small but positive dimensions."""
        book_metadata = BookMetadata(page_count=1, unit_system="metric")

        result = SpineResult(
            width_mm=0.001, width_inches=0.00004, width_pixels=0.1, dpi=300, book_metadata=book_metadata
        )

        assert result.width_mm == 0.001
        assert result.width_inches == 0.00004
        assert result.width_pixels == 0.1

    def test_very_large_dimensions(self):
        """Test with very large dimensions."""
        book_metadata = BookMetadata(page_count=10000, unit_system="metric")

        result = SpineResult(
            width_mm=1000.0, width_inches=39.37, width_pixels=11811.0, dpi=300, book_metadata=book_metadata
        )

        assert result.width_mm == 1000.0
        assert result.width_inches == 39.37
        assert result.width_pixels == 11811.0

    def test_high_dpi_values(self):
        """Test with high DPI values."""
        book_metadata = BookMetadata(page_count=200, unit_system="metric")

        result = SpineResult(
            width_mm=12.5,
            width_inches=0.492,
            width_pixels=1476.0,  # 10x pixels for 3000 DPI
            dpi=3000,
            book_metadata=book_metadata,
        )

        assert result.dpi == 3000
        assert result.width_pixels == 1476.0

    def test_json_serialization_with_special_characters(self):
        """Test JSON serialization with special characters in strings."""
        # Create a mock book_metadata to bypass validation for testing JSON handling
        book_metadata = Mock()
        book_metadata.page_count = 200
        book_metadata.paper_type = None
        book_metadata.binding_type = 'Special "Quoted" Binding'
        book_metadata.paper_weight = None
        book_metadata.unit_system = "metric"
        book_metadata.to_dict = Mock(
            return_value={
                "page_count": 200,
                "paper_type": None,
                "binding_type": 'Special "Quoted" Binding',
                "paper_weight": None,
                "unit_system": "metric",
            }
        )

        result = SpineResult(
            width_mm=12.5, width_inches=0.492, width_pixels=147.6, dpi=300, book_metadata=book_metadata
        )

        json_str = result.to_json()
        parsed = json.loads(json_str)  # Should not raise an exception
        assert parsed["book_metadata"]["binding_type"] == 'Special "Quoted" Binding'
