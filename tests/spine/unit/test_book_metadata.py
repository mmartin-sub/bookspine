"""
Unit tests for the BookMetadata class.
"""

import unittest

import pytest

from src.bookspine.models.book_metadata import BookMetadata, ValidationError


class TestBookMetadata(unittest.TestCase):
    """Test cases for the BookMetadata class."""

    def test_valid_metadata(self):
        """Test creating a valid BookMetadata object."""
        # Test with all fields provided
        metadata = BookMetadata(
            page_count=200,
            paper_type="MCG",
            binding_type="Softcover Perfect Bound",
            paper_weight=80,
            unit_system="metric",
        )
        self.assertEqual(metadata.page_count, 200)
        self.assertEqual(metadata.paper_type, "MCG")
        self.assertEqual(metadata.binding_type, "Softcover Perfect Bound")
        self.assertEqual(metadata.paper_weight, 80)
        self.assertEqual(metadata.unit_system, "metric")

        # Test with only required fields
        metadata = BookMetadata(page_count=200)
        self.assertEqual(metadata.page_count, 200)
        self.assertIsNone(metadata.paper_type)
        self.assertIsNone(metadata.binding_type)
        self.assertIsNone(metadata.paper_weight)
        self.assertEqual(metadata.unit_system, "metric")

    def test_invalid_page_count(self):
        """Test validation of page count."""
        # Test with negative page count
        with self.assertRaises(ValidationError) as context:
            BookMetadata(page_count=-10)
        self.assertIn("Page count must be positive", str(context.exception))

        # Test with zero page count
        with self.assertRaises(ValidationError) as context:
            BookMetadata(page_count=0)
        self.assertIn("Page count must be positive", str(context.exception))

        # Test with non-integer page count
        with self.assertRaises(ValidationError) as context:
            BookMetadata(page_count="200")
        self.assertIn("Page count must be an integer", str(context.exception))

    def test_invalid_paper_type(self):
        """Test validation of paper type."""
        # Test with invalid paper type
        with self.assertRaises(ValidationError) as context:
            BookMetadata(page_count=200, paper_type="INVALID")
        self.assertIn("Invalid paper type", str(context.exception))

        # Test with each valid paper type
        for paper_type in BookMetadata.VALID_PAPER_TYPES:
            metadata = BookMetadata(page_count=200, paper_type=paper_type)
            self.assertEqual(metadata.paper_type, paper_type)

    def test_invalid_binding_type(self):
        """Test validation of binding type."""
        # Test with invalid binding type
        with self.assertRaises(ValidationError) as context:
            BookMetadata(page_count=200, binding_type="INVALID")
        self.assertIn("Invalid binding type", str(context.exception))

        # Test with each valid binding type
        for binding_type in BookMetadata.VALID_BINDING_TYPES:
            metadata = BookMetadata(page_count=200, binding_type=binding_type)
            self.assertEqual(metadata.binding_type, binding_type)

    def test_invalid_paper_weight(self):
        """Test validation of paper weight."""
        # Test with negative paper weight
        with self.assertRaises(ValidationError) as context:
            BookMetadata(page_count=200, paper_weight=-10)
        self.assertIn("Paper weight must be positive", str(context.exception))

        # Test with non-numeric paper weight
        with self.assertRaises(ValidationError) as context:
            BookMetadata(page_count=200, paper_weight="80")
        self.assertIn("Paper weight must be a number", str(context.exception))

        # Test with paper weight outside typical range (should print warning but not raise error)
        import io
        import sys

        # Capture stdout to check for warning message
        captured_output = io.StringIO()
        sys.stdout = captured_output

        # Test with paper weight below minimum
        metadata = BookMetadata(page_count=200, paper_weight=40)
        self.assertEqual(metadata.paper_weight, 40)
        self.assertIn("Warning: Paper weight 40 gsm is outside typical range", captured_output.getvalue())

        # Reset captured output
        captured_output = io.StringIO()
        sys.stdout = captured_output

        # Test with paper weight above maximum
        metadata = BookMetadata(page_count=200, paper_weight=350)
        self.assertEqual(metadata.paper_weight, 350)
        self.assertIn("Warning: Paper weight 350 gsm is outside typical range", captured_output.getvalue())

        # Restore stdout
        sys.stdout = sys.__stdout__

    def test_invalid_unit_system(self):
        """Test validation of unit system."""
        # Test with invalid unit system
        with self.assertRaises(ValidationError) as context:
            BookMetadata(page_count=200, unit_system="INVALID")
        self.assertIn("Invalid unit system", str(context.exception))

        # Test with each valid unit system
        for unit_system in BookMetadata.VALID_UNIT_SYSTEMS:
            metadata = BookMetadata(page_count=200, unit_system=unit_system)
            self.assertEqual(metadata.unit_system, unit_system)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metadata = BookMetadata(
            page_count=200,
            paper_type="MCG",
            binding_type="Softcover Perfect Bound",
            paper_weight=80,
            unit_system="metric",
        )
        metadata_dict = metadata.to_dict()

        self.assertEqual(metadata_dict["page_count"], 200)
        self.assertEqual(metadata_dict["paper_type"], "MCG")
        self.assertEqual(metadata_dict["binding_type"], "Softcover Perfect Bound")
        self.assertEqual(metadata_dict["paper_weight"], 80)
        self.assertEqual(metadata_dict["unit_system"], "metric")

    def test_is_complete(self):
        """Test checking if all required fields are provided."""
        # Test with all fields provided
        metadata = BookMetadata(
            page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
        )
        self.assertTrue(metadata.is_complete())

        # Test with missing paper_type
        metadata = BookMetadata(page_count=200, binding_type="Softcover Perfect Bound", paper_weight=80)
        self.assertFalse(metadata.is_complete())

        # Test with missing binding_type
        metadata = BookMetadata(page_count=200, paper_type="MCG", paper_weight=80)
        self.assertFalse(metadata.is_complete())

        # Test with missing paper_weight
        metadata = BookMetadata(page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound")
        self.assertFalse(metadata.is_complete())


if __name__ == "__main__":
    unittest.main()
