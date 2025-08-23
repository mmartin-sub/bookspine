"""
Unit tests for the UnitConverter class.
"""

import unittest

from bookspine.core.unit_converter import UnitConverter


class TestUnitConverter(unittest.TestCase):
    """Test case for the UnitConverter class."""

    def test_mm_to_inches_basic(self):
        """Test basic conversion from millimeters to inches."""
        # Test exact conversion
        self.assertEqual(UnitConverter.mm_to_inches(25.4), 1.0)
        # Test precision (requirement 3.4)
        self.assertEqual(UnitConverter.mm_to_inches(10.0), 0.3937)
        self.assertEqual(UnitConverter.mm_to_inches(50.8), 2.0)

    def test_mm_to_inches_edge_cases(self):
        """Test edge cases for mm to inches conversion."""
        self.assertEqual(UnitConverter.mm_to_inches(0), 0.0)
        with self.assertRaises(ValueError):
            UnitConverter.mm_to_inches(None)

    def test_inches_to_mm_basic(self):
        """Test basic conversion from inches to millimeters."""
        # Test exact conversion
        self.assertEqual(UnitConverter.inches_to_mm(1.0), 25.4)
        self.assertEqual(UnitConverter.inches_to_mm(0.5), 12.7)
        self.assertEqual(UnitConverter.inches_to_mm(2.0), 50.8)

    def test_inches_to_mm_edge_cases(self):
        """Test edge cases for inches to mm conversion."""
        self.assertEqual(UnitConverter.inches_to_mm(0), 0.0)
        with self.assertRaises(ValueError):
            UnitConverter.inches_to_mm(None)

    def test_mm_to_pixels_basic(self):
        """Test conversion from millimeters to pixels (requirement 3.1)."""
        # Test formula: pixels = (value_mm / 25.4) * DPI
        self.assertEqual(UnitConverter.mm_to_pixels(25.4, dpi=300), 300.0)
        self.assertEqual(UnitConverter.mm_to_pixels(12.7, dpi=300), 150.0)
        self.assertEqual(UnitConverter.mm_to_pixels(10.0, dpi=300), 118.11)

    def test_mm_to_pixels_default_dpi(self):
        """Test mm to pixels with default DPI (requirement 3.3)."""
        # Should default to 300 DPI
        self.assertEqual(UnitConverter.mm_to_pixels(25.4), 300.0)

    def test_mm_to_pixels_edge_cases(self):
        """Test edge cases for mm to pixels conversion."""
        self.assertEqual(UnitConverter.mm_to_pixels(0, dpi=300), 0.0)
        with self.assertRaises(ValueError):
            UnitConverter.mm_to_pixels(None, dpi=300)
        with self.assertRaises(ValueError):
            UnitConverter.mm_to_pixels(10.0, dpi=0)
        with self.assertRaises(ValueError):
            UnitConverter.mm_to_pixels(10.0, dpi=-100)

    def test_inches_to_pixels_basic(self):
        """Test conversion from inches to pixels (requirement 3.2)."""
        # Test formula: pixels = value_inches * DPI
        self.assertEqual(UnitConverter.inches_to_pixels(1.0, dpi=300), 300.0)
        self.assertEqual(UnitConverter.inches_to_pixels(0.5, dpi=300), 150.0)
        self.assertEqual(UnitConverter.inches_to_pixels(2.0, dpi=150), 300.0)

    def test_inches_to_pixels_default_dpi(self):
        """Test inches to pixels with default DPI (requirement 3.3)."""
        # Should default to 300 DPI
        self.assertEqual(UnitConverter.inches_to_pixels(1.0), 300.0)

    def test_inches_to_pixels_edge_cases(self):
        """Test edge cases for inches to pixels conversion."""
        self.assertEqual(UnitConverter.inches_to_pixels(0, dpi=300), 0.0)
        with self.assertRaises(ValueError):
            UnitConverter.inches_to_pixels(None, dpi=300)
        with self.assertRaises(ValueError):
            UnitConverter.inches_to_pixels(1.0, dpi=0)
        with self.assertRaises(ValueError):
            UnitConverter.inches_to_pixels(1.0, dpi=-100)

    def test_pixels_to_mm_basic(self):
        """Test conversion from pixels to millimeters."""
        self.assertEqual(UnitConverter.pixels_to_mm(300, dpi=300), 25.4)
        self.assertEqual(UnitConverter.pixels_to_mm(150, dpi=300), 12.7)
        self.assertEqual(UnitConverter.pixels_to_mm(600, dpi=600), 25.4)

    def test_pixels_to_mm_default_dpi(self):
        """Test pixels to mm with default DPI."""
        self.assertEqual(UnitConverter.pixels_to_mm(300), 25.4)

    def test_pixels_to_mm_edge_cases(self):
        """Test edge cases for pixels to mm conversion."""
        self.assertEqual(UnitConverter.pixels_to_mm(0, dpi=300), 0.0)
        with self.assertRaises(ValueError):
            UnitConverter.pixels_to_mm(None, dpi=300)
        with self.assertRaises(ValueError):
            UnitConverter.pixels_to_mm(300, dpi=0)

    def test_pixels_to_inches_basic(self):
        """Test conversion from pixels to inches."""
        self.assertEqual(UnitConverter.pixels_to_inches(300, dpi=300), 1.0)
        self.assertEqual(UnitConverter.pixels_to_inches(150, dpi=300), 0.5)
        self.assertEqual(UnitConverter.pixels_to_inches(600, dpi=600), 1.0)

    def test_pixels_to_inches_default_dpi(self):
        """Test pixels to inches with default DPI."""
        self.assertEqual(UnitConverter.pixels_to_inches(300), 1.0)

    def test_pixels_to_inches_edge_cases(self):
        """Test edge cases for pixels to inches conversion."""
        self.assertEqual(UnitConverter.pixels_to_inches(0, dpi=300), 0.0)
        with self.assertRaises(ValueError):
            UnitConverter.pixels_to_inches(None, dpi=300)
        with self.assertRaises(ValueError):
            UnitConverter.pixels_to_inches(300, dpi=0)

    def test_convert_to_all_units_from_mm(self):
        """Test converting from mm to all units (requirement 3.6)."""
        result = UnitConverter.convert_to_all_units(25.4, "mm", dpi=300)
        self.assertEqual(result["mm"], 25.4)
        self.assertEqual(result["inches"], 1.0)
        self.assertEqual(result["pixels"], 300.0)

    def test_convert_to_all_units_from_inches(self):
        """Test converting from inches to all units."""
        result = UnitConverter.convert_to_all_units(1.0, "inches", dpi=300)
        self.assertEqual(result["mm"], 25.4)
        self.assertEqual(result["inches"], 1.0)
        self.assertEqual(result["pixels"], 300.0)

    def test_convert_to_all_units_from_pixels(self):
        """Test converting from pixels to all units."""
        result = UnitConverter.convert_to_all_units(300, "pixels", dpi=300)
        self.assertEqual(result["mm"], 25.4)
        self.assertEqual(result["inches"], 1.0)
        self.assertEqual(result["pixels"], 300)

    def test_convert_to_all_units_case_insensitive(self):
        """Test that unit names are case insensitive."""
        result1 = UnitConverter.convert_to_all_units(25.4, "MM", dpi=300)
        result2 = UnitConverter.convert_to_all_units(25.4, "mm", dpi=300)
        self.assertEqual(result1, result2)

    def test_convert_to_all_units_edge_cases(self):
        """Test edge cases for convert_to_all_units."""
        with self.assertRaises(ValueError):
            UnitConverter.convert_to_all_units(None, "mm")
        with self.assertRaises(ValueError):
            UnitConverter.convert_to_all_units(25.4, "invalid_unit")
        with self.assertRaises(ValueError):
            UnitConverter.convert_to_all_units(25.4, "mm", dpi=0)

    def test_format_with_units_basic(self):
        """Test formatting values with unit labels (requirement 3.5)."""
        self.assertEqual(UnitConverter.format_with_units(25.4, "mm"), "25.40 mm")
        self.assertEqual(UnitConverter.format_with_units(1.0, "inches"), "1.0000 in")
        self.assertEqual(UnitConverter.format_with_units(300.0, "pixels"), "300.00 px")

    def test_format_with_units_custom_precision(self):
        """Test formatting with custom precision."""
        self.assertEqual(UnitConverter.format_with_units(25.4567, "mm", precision=1), "25.5 mm")
        self.assertEqual(UnitConverter.format_with_units(1.23456, "inches", precision=3), "1.235 in")

    def test_format_with_units_case_insensitive(self):
        """Test that unit formatting is case insensitive."""
        self.assertEqual(UnitConverter.format_with_units(25.4, "MM"), "25.40 mm")
        self.assertEqual(UnitConverter.format_with_units(1.0, "INCHES"), "1.0000 in")

    def test_format_with_units_edge_cases(self):
        """Test edge cases for format_with_units."""
        self.assertEqual(UnitConverter.format_with_units(None, "mm"), "N/A")
        self.assertEqual(UnitConverter.format_with_units(25.4, "unknown"), "25.40 unknown")

    def test_precision_requirements(self):
        """Test that precision requirements are met (requirement 3.4)."""
        # Test that conversions maintain at least 2 decimal places precision
        mm_value = 12.34  # Use value that rounds cleanly
        inches_value = UnitConverter.mm_to_inches(mm_value)
        back_to_mm = UnitConverter.inches_to_mm(inches_value)

        # Should be very close due to rounding
        self.assertAlmostEqual(mm_value, back_to_mm, places=2)

        # Test pixel conversions maintain precision
        pixels = UnitConverter.mm_to_pixels(mm_value, dpi=300)
        self.assertIsInstance(pixels, float)
        # Should have at most 2 decimal places
        self.assertEqual(pixels, round(pixels, 2))

        # Test that all conversions provide at least 2 decimal places precision
        test_values = [10.12, 25.67, 100.99]
        for val in test_values:
            # mm to pixels should maintain 2 decimal precision
            pixels = UnitConverter.mm_to_pixels(val, dpi=300)
            self.assertEqual(pixels, round(pixels, 2))

            # inches to pixels should maintain 2 decimal precision
            inches_val = val / 25.4
            pixels = UnitConverter.inches_to_pixels(inches_val, dpi=300)
            self.assertEqual(pixels, round(pixels, 2))

    def test_default_dpi_constant(self):
        """Test that default DPI is 300 (requirement 3.3)."""
        self.assertEqual(UnitConverter.DEFAULT_DPI, 300)

    def test_conversion_formulas_accuracy(self):
        """Test that conversion formulas match requirements exactly."""
        # Requirement 3.1: pixels = (value_mm / 25.4) * DPI
        mm_val = 50.8
        dpi = 150
        expected_pixels = (mm_val / 25.4) * dpi
        actual_pixels = UnitConverter.mm_to_pixels(mm_val, dpi)
        self.assertEqual(actual_pixels, round(expected_pixels, 2))

        # Requirement 3.2: pixels = value_inches * DPI
        inches_val = 2.0
        expected_pixels = inches_val * dpi
        actual_pixels = UnitConverter.inches_to_pixels(inches_val, dpi)
        self.assertEqual(actual_pixels, round(expected_pixels, 2))


if __name__ == "__main__":
    unittest.main()
