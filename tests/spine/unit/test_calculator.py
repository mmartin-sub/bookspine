"""
Unit tests for SpineCalculator class.
"""

import unittest
from unittest.mock import Mock

import pytest

from bookspine.core.calculator import CalculationError, SpineCalculator
from bookspine.models.book_metadata import BookMetadata
from bookspine.models.spine_result import SpineResult


class TestSpineCalculator:
    """Test cases for SpineCalculator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config_loader = Mock()
        self.calculator = SpineCalculator(self.mock_config_loader)

        # Reset mock state
        self.mock_config_loader.reset_mock()
        self.mock_config_loader.load_printer_service_config.reset_mock()

        # Default test configuration
        self.default_config = {
            "name": "test",
            "paper_bulk": {"MCG": 0.80, "MCS": 0.90, "ECB": 1.20, "OFF": 1.22},
            "cover_thickness": {"Softcover Perfect Bound": 0.5, "Hardcover Casewrap": 2.0, "Hardcover Linen": 3.0},
            "formulas": {
                "Softcover Perfect Bound": {"type": "general", "params": {}},
                "Hardcover Casewrap": {
                    "type": "fixed_ranges",
                    "params": {
                        "ranges": [
                            {"min_pages": 24, "max_pages": 84, "width_inches": 0.25},
                            {"min_pages": 85, "max_pages": 140, "width_inches": 0.5},
                            {"min_pages": 141, "max_pages": 200, "width_inches": 0.75},
                        ]
                    },
                },
            },
        }

        # Pages per inch configuration (like KDP/Lulu)
        self.pages_per_inch_config = {
            "name": "test_ppi",
            "formulas": {
                "Softcover Perfect Bound": {
                    "type": "pages_per_inch",
                    "params": {"pages_per_inch": 444, "base_thickness": 0.06},
                }
            },
        }

    def test_init(self):
        """Test SpineCalculator initialization."""
        assert self.calculator.config_loader == self.mock_config_loader

    def test_calculate_spine_width_basic(self):
        """Test basic spine width calculation with general formula."""
        # Setup
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        book_metadata = BookMetadata(
            page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80.0
        )

        # Execute
        result = self.calculator.calculate_spine_width(book_metadata)

        # Verify
        assert isinstance(result, SpineResult)
        assert result.book_metadata == book_metadata
        assert result.dpi == 300  # default DPI
        assert result.manual_override_applied is False
        assert result.original_calculated_width_mm is None

        # Verify calculation: (80 * 0.80 * (200/2)) / 1000 + (2 * 0.5) = 6.4 + 1.0 = 7.4 mm
        expected_width_mm = 7.4
        assert result.width_mm == expected_width_mm
        assert abs(result.width_inches - (expected_width_mm / 25.4)) < 0.0001
        assert abs(result.width_pixels - ((expected_width_mm / 25.4) * 300)) < 0.01

    def test_calculate_spine_width_pages_per_inch_formula(self):
        """Test spine width calculation with pages per inch formula."""
        # Setup
        self.mock_config_loader.load_printer_service_config.return_value = self.pages_per_inch_config

        book_metadata = BookMetadata(page_count=200, binding_type="Softcover Perfect Bound")

        # Execute
        result = self.calculator.calculate_spine_width(book_metadata)

        # Verify calculation: (200 / 444) + 0.06 = 0.4505 + 0.06 = 0.5105 inches
        expected_width_inches = (200 / 444) + 0.06
        expected_width_mm = expected_width_inches * 25.4

        assert abs(result.width_inches - expected_width_inches) < 0.001
        assert abs(result.width_mm - expected_width_mm) < 0.1

    def test_calculate_spine_width_fixed_ranges_formula(self):
        """Test spine width calculation with fixed ranges formula."""
        # Setup
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        book_metadata = BookMetadata(page_count=100, binding_type="Hardcover Casewrap")  # Should fall in 85-140 range

        # Execute
        result = self.calculator.calculate_spine_width(book_metadata)

        # Verify calculation: 0.5 inches = 12.7 mm
        expected_width_inches = 0.5
        expected_width_mm = expected_width_inches * 25.4

        assert result.width_inches == expected_width_inches
        assert result.width_mm == expected_width_mm

    def test_calculate_spine_width_with_manual_override(self):
        """Test spine width calculation with manual override."""
        # Setup
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        book_metadata = BookMetadata(
            page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80.0
        )

        manual_override = 10.0  # 10 mm

        # Execute
        result = self.calculator.calculate_spine_width(book_metadata, manual_override=manual_override)

        # Verify
        assert result.width_mm == manual_override
        assert result.manual_override_applied is True
        assert result.original_calculated_width_mm == 7.4  # Original calculated value
        assert abs(result.width_inches - (manual_override / 25.4)) < 0.0001

    def test_calculate_spine_width_with_custom_dpi(self):
        """Test spine width calculation with custom DPI."""
        # Setup
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        book_metadata = BookMetadata(
            page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80.0
        )

        custom_dpi = 600

        # Execute
        result = self.calculator.calculate_spine_width(book_metadata, dpi=custom_dpi)

        # Verify
        assert result.dpi == custom_dpi
        expected_pixels = (result.width_mm / 25.4) * custom_dpi
        assert abs(result.width_pixels - expected_pixels) < 0.01

    def test_calculate_spine_width_with_printer_service(self):
        """Test spine width calculation with specific printer service."""
        # Setup
        service_name = "test_service"
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        book_metadata = BookMetadata(
            page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80.0
        )

        # Execute
        result = self.calculator.calculate_spine_width(book_metadata, printer_service=service_name)

        # Verify
        assert result.printer_service == service_name
        self.mock_config_loader.load_printer_service_config.assert_called_with(service_name)

    def test_calculate_spine_width_invalid_page_count(self):
        """Test error handling for invalid page count."""
        # BookMetadata validation will catch this first, so we test the ValidationError
        from bookspine.models.book_metadata import ValidationError

        with pytest.raises(ValidationError, match="Page count must be positive"):
            BookMetadata(
                page_count=0,
                paper_type="MCG",
                binding_type="Softcover Perfect Bound",
                paper_weight=80.0,  # Invalid
            )

    def test_calculate_spine_width_invalid_dpi(self):
        """Test error handling for invalid DPI."""
        book_metadata = BookMetadata(
            page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80.0
        )

        with pytest.raises(CalculationError, match="DPI must be positive"):
            self.calculator.calculate_spine_width(book_metadata, dpi=0)

    def test_calculate_spine_width_missing_binding_type(self):
        """Test error handling for missing binding type."""
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        book_metadata = BookMetadata(page_count=200, paper_type="MCG", binding_type=None, paper_weight=80.0)  # Missing

        with pytest.raises(CalculationError, match="Binding type is required"):
            self.calculator.calculate_spine_width(book_metadata)

    def test_calculate_spine_width_unsupported_binding_type(self):
        """Test error handling for unsupported binding type."""
        # BookMetadata validation will catch this first, so we test the ValidationError
        from bookspine.models.book_metadata import ValidationError

        with pytest.raises(ValidationError, match="Invalid binding type"):
            BookMetadata(
                page_count=200,
                paper_type="MCG",
                binding_type="Unsupported Binding",
                paper_weight=80.0,  # Not in config
            )

    def test_calculate_spine_width_missing_paper_type_for_general(self):
        """Test error handling for missing paper type in general formula."""
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        book_metadata = BookMetadata(
            page_count=200,
            paper_type=None,
            binding_type="Softcover Perfect Bound",
            paper_weight=80.0,  # Missing
        )

        with pytest.raises(CalculationError, match="Paper type is required"):
            self.calculator.calculate_spine_width(book_metadata)

    def test_calculate_spine_width_missing_paper_weight_for_general(self):
        """Test error handling for missing paper weight in general formula."""
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        book_metadata = BookMetadata(
            page_count=200,
            paper_type="MCG",
            binding_type="Softcover Perfect Bound",
            paper_weight=None,  # Missing
        )

        with pytest.raises(CalculationError, match="Paper weight is required"):
            self.calculator.calculate_spine_width(book_metadata)

    def test_calculate_spine_width_unsupported_paper_type(self):
        """Test error handling for unsupported paper type."""
        # BookMetadata validation will catch this first, so we test the ValidationError
        from bookspine.models.book_metadata import ValidationError

        with pytest.raises(ValidationError, match="Invalid paper type"):
            BookMetadata(
                page_count=200,
                paper_type="UNKNOWN",  # Not in config
                binding_type="Softcover Perfect Bound",
                paper_weight=80.0,
            )

    def test_calculate_spine_width_negative_manual_override(self):
        """Test error handling for negative manual override."""
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        book_metadata = BookMetadata(
            page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80.0
        )

        with pytest.raises(CalculationError, match="Manual override value must be non-negative"):
            self.calculator.calculate_spine_width(book_metadata, manual_override=-1.0)

    def test_calculate_spine_width_fixed_ranges_no_match(self):
        """Test error handling when page count doesn't match any range."""
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        book_metadata = BookMetadata(page_count=500, binding_type="Hardcover Casewrap")  # Outside all ranges

        with pytest.raises(CalculationError, match="No matching range found for page count: 500"):
            self.calculator.calculate_spine_width(book_metadata)

    def test_calculate_spine_width_unknown_formula_type(self):
        """Test error handling for unknown formula type."""
        # We need to test this with a valid binding type that has an unknown formula
        config_with_unknown_formula = {
            "formulas": {"Softcover Perfect Bound": {"type": "unknown_formula", "params": {}}}
        }
        self.mock_config_loader.load_printer_service_config.return_value = config_with_unknown_formula

        book_metadata = BookMetadata(page_count=200, binding_type="Softcover Perfect Bound")

        with pytest.raises(CalculationError, match="Unknown formula type"):
            self.calculator.calculate_spine_width(book_metadata)

    def test_get_supported_binding_types(self):
        """Test getting supported binding types."""
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        binding_types = self.calculator.get_supported_binding_types()

        expected_types = ["Softcover Perfect Bound", "Hardcover Casewrap"]
        assert set(binding_types) == set(expected_types)

    def test_get_supported_binding_types_with_service(self):
        """Test getting supported binding types for specific service."""
        service_name = "test_service"
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        binding_types = self.calculator.get_supported_binding_types(service_name)

        self.mock_config_loader.load_printer_service_config.assert_called_with(service_name)
        assert len(binding_types) > 0

    def test_get_supported_binding_types_error_handling(self):
        """Test error handling in get_supported_binding_types."""
        self.mock_config_loader.load_printer_service_config.side_effect = Exception("Config error")

        binding_types = self.calculator.get_supported_binding_types()

        assert binding_types == []

    def test_get_supported_paper_types(self):
        """Test getting supported paper types."""
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        paper_types = self.calculator.get_supported_paper_types()

        expected_types = ["MCG", "MCS", "ECB", "OFF"]
        assert set(paper_types) == set(expected_types)

    def test_get_supported_paper_types_with_service(self):
        """Test getting supported paper types for specific service."""
        service_name = "test_service"
        self.mock_config_loader.load_printer_service_config.return_value = self.default_config

        paper_types = self.calculator.get_supported_paper_types(service_name)

        self.mock_config_loader.load_printer_service_config.assert_called_with(service_name)
        assert len(paper_types) > 0

    def test_get_supported_paper_types_error_handling(self):
        """Test error handling in get_supported_paper_types."""
        self.mock_config_loader.load_printer_service_config.side_effect = Exception("Config error")

        paper_types = self.calculator.get_supported_paper_types()

        assert paper_types == []


class TestSpineCalculatorFormulas:
    """Test cases for specific calculation formulas."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config_loader = Mock()
        self.calculator = SpineCalculator(self.mock_config_loader)

    def test_general_formula_calculation_accuracy(self):
        """Test accuracy of general formula calculation."""
        config = {
            "paper_bulk": {"MCG": 0.80},
            "cover_thickness": {"Softcover Perfect Bound": 0.5},
            "formulas": {"Softcover Perfect Bound": {"type": "general", "params": {}}},
        }
        self.mock_config_loader.load_printer_service_config.return_value = config

        book_metadata = BookMetadata(
            page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80.0
        )

        result = self.calculator.calculate_spine_width(book_metadata)

        # Manual calculation: (80 * 0.80 * (200/2)) / 1000 + (2 * 0.5)
        # = (80 * 0.80 * 100) / 1000 + 1.0
        # = 6400 / 1000 + 1.0
        # = 6.4 + 1.0 = 7.4 mm
        assert result.width_mm == 7.4

    def test_pages_per_inch_formula_accuracy_444_ppi(self):
        """Test accuracy of 444 PPI formula (Lulu)."""
        config = {
            "formulas": {
                "Softcover Perfect Bound": {
                    "type": "pages_per_inch",
                    "params": {"pages_per_inch": 444, "base_thickness": 0.06},
                }
            }
        }
        self.mock_config_loader.load_printer_service_config.return_value = config

        book_metadata = BookMetadata(page_count=200, binding_type="Softcover Perfect Bound")

        result = self.calculator.calculate_spine_width(book_metadata)

        # Manual calculation: (200 / 444) + 0.06 = 0.4505 + 0.06 = 0.5105 inches
        expected_inches = (200 / 444) + 0.06
        expected_mm = expected_inches * 25.4

        assert abs(result.width_inches - expected_inches) < 0.001
        assert abs(result.width_mm - expected_mm) < 0.1

    def test_pages_per_inch_formula_accuracy_460_ppi(self):
        """Test accuracy of 460 PPI formula (KDP)."""
        config = {
            "formulas": {
                "Softcover Perfect Bound": {
                    "type": "pages_per_inch",
                    "params": {"pages_per_inch": 460, "base_thickness": 0.06},
                }
            }
        }
        self.mock_config_loader.load_printer_service_config.return_value = config

        book_metadata = BookMetadata(page_count=200, binding_type="Softcover Perfect Bound")

        result = self.calculator.calculate_spine_width(book_metadata)

        # Manual calculation: (200 / 460) + 0.06 = 0.4348 + 0.06 = 0.4948 inches
        expected_inches = (200 / 460) + 0.06
        expected_mm = expected_inches * 25.4

        assert abs(result.width_inches - expected_inches) < 0.001
        assert abs(result.width_mm - expected_mm) < 0.1

    def test_different_paper_types_bulk_values(self):
        """Test calculation with different paper types and their bulk values."""
        config = {
            "paper_bulk": {"MCG": 0.80, "MCS": 0.90, "ECB": 1.20, "OFF": 1.22},
            "cover_thickness": {"Softcover Perfect Bound": 0.5},
            "formulas": {"Softcover Perfect Bound": {"type": "general", "params": {}}},
        }
        self.mock_config_loader.load_printer_service_config.return_value = config

        base_metadata = BookMetadata(page_count=200, binding_type="Softcover Perfect Bound", paper_weight=80.0)

        # Test each paper type
        paper_types_and_expected = [
            ("MCG", 0.80, 7.4),  # (80 * 0.80 * 100) / 1000 + 1.0 = 7.4
            ("MCS", 0.90, 8.2),  # (80 * 0.90 * 100) / 1000 + 1.0 = 8.2
            ("ECB", 1.20, 10.6),  # (80 * 1.20 * 100) / 1000 + 1.0 = 10.6
            ("OFF", 1.22, 10.76),  # (80 * 1.22 * 100) / 1000 + 1.0 = 10.76
        ]

        for paper_type, _bulk, expected_mm in paper_types_and_expected:
            base_metadata.paper_type = paper_type
            result = self.calculator.calculate_spine_width(base_metadata)
            assert result.width_mm == expected_mm, f"Failed for paper type {paper_type}"

    def test_different_binding_types_cover_thickness(self):
        """Test calculation with different binding types and their cover thickness."""
        config = {
            "paper_bulk": {"MCG": 0.80},
            "cover_thickness": {"Softcover Perfect Bound": 0.5, "Hardcover Casewrap": 2.0, "Hardcover Linen": 3.0},
            "formulas": {
                "Softcover Perfect Bound": {"type": "general", "params": {}},
                "Hardcover Casewrap": {"type": "general", "params": {}},
                "Hardcover Linen": {"type": "general", "params": {}},
            },
        }
        self.mock_config_loader.load_printer_service_config.return_value = config

        base_metadata = BookMetadata(page_count=200, paper_type="MCG", paper_weight=80.0)

        # Test each binding type
        binding_types_and_expected = [
            ("Softcover Perfect Bound", 0.5, 7.4),  # 6.4 + (2 * 0.5) = 7.4
            ("Hardcover Casewrap", 2.0, 10.4),  # 6.4 + (2 * 2.0) = 10.4
            ("Hardcover Linen", 3.0, 12.4),  # 6.4 + (2 * 3.0) = 12.4
        ]

        for binding_type, _thickness, expected_mm in binding_types_and_expected:
            base_metadata.binding_type = binding_type
            result = self.calculator.calculate_spine_width(base_metadata)
            assert result.width_mm == expected_mm, f"Failed for binding type {binding_type}"
