"""
Unit tests for PDFProcessor.

This module tests the PDFProcessor class which handles PDF file
processing and metadata extraction.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from src.bookspine.core.pdf_processor import PDFProcessingError, PDFProcessor


class TestPDFProcessor(unittest.TestCase):
    """Test cases for PDFProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = PDFProcessor()
        self.test_dir = Path(__file__).parent.parent / "resources"
        self.test_dir.mkdir(exist_ok=True)

    def test_extract_page_count_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        non_existent_file = "non_existent_file.pdf"

        with self.assertRaises(FileNotFoundError) as context:
            self.processor.extract_page_count(non_existent_file)

        self.assertIn("PDF file not found", str(context.exception))

    def test_extract_page_count_invalid_extension(self):
        """Test that PDFProcessingError is raised for non-PDF files."""
        # Create a temporary non-PDF file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"This is not a PDF")
            temp_file_path = temp_file.name

        try:
            with self.assertRaises(PDFProcessingError) as context:
                self.processor.extract_page_count(temp_file_path)

            self.assertIn("File is not a PDF", str(context.exception))
        finally:
            os.unlink(temp_file_path)

    def test_extract_page_count_empty_file(self):
        """Test that PDFProcessingError is raised for empty files."""
        # Create an empty PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            with self.assertRaises(PDFProcessingError) as context:
                self.processor.extract_page_count(temp_file_path)

            self.assertIn("PDF file is empty", str(context.exception))
        finally:
            os.unlink(temp_file_path)

    @patch("src.bookspine.core.pdf_processor.PdfReader")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake pdf content")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    def test_extract_page_count_valid_pdf(self, mock_stat, mock_exists, mock_file, mock_pdf_reader):
        """Test successful page count extraction from a valid PDF."""
        # Mock file stats
        mock_stat.return_value.st_size = 1000

        # Mock PDF reader
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [MagicMock(), MagicMock(), MagicMock()]  # 3 pages
        mock_reader_instance.is_encrypted = False

        # Mock first page with valid mediabox
        mock_page = MagicMock()
        mock_page.mediabox.width = 612  # Standard letter width in points
        mock_page.mediabox.height = 792  # Standard letter height in points
        mock_reader_instance.pages = [mock_page, MagicMock(), MagicMock()]

        mock_pdf_reader.return_value = mock_reader_instance

        result = self.processor.extract_page_count("test.pdf")

        self.assertEqual(result, 3)
        mock_pdf_reader.assert_called_once()

    @patch("src.bookspine.core.pdf_processor.PdfReader")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake pdf content")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    def test_extract_page_count_encrypted_pdf(self, mock_stat, mock_exists, mock_file, mock_pdf_reader):
        """Test that PDFProcessingError is raised for encrypted PDFs."""
        # Mock file stats
        mock_stat.return_value.st_size = 1000

        # Mock PDF reader with encrypted PDF
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [MagicMock()]
        mock_reader_instance.is_encrypted = True
        mock_pdf_reader.return_value = mock_reader_instance

        with self.assertRaises(PDFProcessingError) as context:
            self.processor.extract_page_count("encrypted.pdf")

        self.assertIn("PDF is encrypted", str(context.exception))

    @patch("src.bookspine.core.pdf_processor.PdfReader")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake pdf content")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    def test_extract_page_count_no_pages(self, mock_stat, mock_exists, mock_file, mock_pdf_reader):
        """Test that PDFProcessingError is raised for PDFs with no pages."""
        # Mock file stats
        mock_stat.return_value.st_size = 1000

        # Mock PDF reader with no pages
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = []
        mock_reader_instance.is_encrypted = False
        mock_pdf_reader.return_value = mock_reader_instance

        with self.assertRaises(PDFProcessingError) as context:
            self.processor.extract_page_count("empty.pdf")

        self.assertIn("PDF contains no pages", str(context.exception))

    @patch("src.bookspine.core.pdf_processor.PdfReader")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake pdf content")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    def test_extract_page_count_invalid_dimensions(self, mock_stat, mock_exists, mock_file, mock_pdf_reader):
        """Test that PDFProcessingError is raised for PDFs with invalid page dimensions."""
        # Mock file stats
        mock_stat.return_value.st_size = 1000

        # Mock PDF reader with invalid page dimensions
        mock_reader_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.mediabox.width = 0  # Invalid width
        mock_page.mediabox.height = 792
        mock_reader_instance.pages = [mock_page]
        mock_reader_instance.is_encrypted = False
        mock_pdf_reader.return_value = mock_reader_instance

        with self.assertRaises(PDFProcessingError) as context:
            self.processor.extract_page_count("invalid_dimensions.pdf")

        self.assertIn("invalid page dimensions", str(context.exception))

    @patch("src.bookspine.core.pdf_processor.PdfReader")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake pdf content")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    def test_extract_page_count_too_small_dimensions(self, mock_stat, mock_exists, mock_file, mock_pdf_reader):
        """Test that PDFProcessingError is raised for PDFs with too small page dimensions."""
        # Mock file stats
        mock_stat.return_value.st_size = 1000

        # Mock PDF reader with too small page dimensions
        mock_reader_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.mediabox.width = 50  # Too small (less than 72 points)
        mock_page.mediabox.height = 50
        mock_reader_instance.pages = [mock_page]
        mock_reader_instance.is_encrypted = False
        mock_pdf_reader.return_value = mock_reader_instance

        with self.assertRaises(PDFProcessingError) as context:
            self.processor.extract_page_count("too_small.pdf")

        self.assertIn("too small to be a valid book", str(context.exception))

    @patch("src.bookspine.core.pdf_processor.PdfReader")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    def test_extract_page_count_corrupted_pdf(self, mock_stat, mock_exists, mock_file, mock_pdf_reader):
        """Test that PDFProcessingError is raised for corrupted PDFs."""
        from pypdf.errors import PdfReadError

        # Mock file stats
        mock_stat.return_value.st_size = 1000

        # Mock PDF reader to raise PdfReadError
        mock_pdf_reader.side_effect = PdfReadError("Invalid PDF structure")

        with self.assertRaises(PDFProcessingError) as context:
            self.processor.extract_page_count("corrupted.pdf")

        self.assertIn("Invalid or corrupted PDF file", str(context.exception))

    def test_validate_pdf_file_valid(self):
        """Test validate_pdf_file method with a valid PDF."""
        with patch.object(self.processor, "extract_page_count", side_effect=FileNotFoundError("File not found")):
            with self.assertRaises(FileNotFoundError):
                self.processor.validate_pdf_file("valid.pdf")

    def test_validate_pdf_file_invalid(self):
        """Test validate_pdf_file method with an invalid PDF."""
        with patch.object(self.processor, "extract_page_count", side_effect=FileNotFoundError("File not found")):
            with self.assertRaises(FileNotFoundError):
                self.processor.validate_pdf_file("invalid.pdf")

    def test_validate_pdf_file_not_found(self):
        """Test validate_pdf_file method with a non-existent file."""
        with patch.object(self.processor, "extract_page_count", side_effect=FileNotFoundError("File not found")):
            with self.assertRaises(FileNotFoundError):
                self.processor.validate_pdf_file("not_found.pdf")


if __name__ == "__main__":
    unittest.main()
