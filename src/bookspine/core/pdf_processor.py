"""
PDF processing functionality for extracting page count information.

This module provides memory-efficient PDF processing capabilities for extracting
page count information from PDF files. It uses pypdf's lazy loading features
to minimize memory usage when processing large PDF files.
"""

from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class PDFMetadata:
    """
    Metadata extracted from a PDF file.

    This class holds metadata information extracted from PDF files including
    page count and file size information.

    Attributes:
        page_count: Number of pages in the PDF file.
        file_size_mb: File size in megabytes.
    """

    def __init__(self, page_count: int, file_size_mb: float):
        """
        Initialize PDF metadata.

        Args:
            page_count: Number of pages in the PDF file.
            file_size_mb: File size in megabytes.
        """
        self.page_count = page_count
        self.file_size_mb = file_size_mb


class PDFProcessingError(Exception):
    """
    Exception raised when PDF processing fails.

    This exception is raised when there are errors in processing PDF files,
    such as invalid PDF format, corrupted files, encrypted files, or other
    PDF-related issues.
    """

    pass


class PDFProcessor:
    """
    Processor for extracting information from PDF files with memory-efficient operations.

    This class provides methods to extract page count information from PDF files
    while minimizing memory usage. It uses pypdf's lazy loading capabilities to
    avoid loading entire PDF content into memory, making it suitable for processing
    large files efficiently.

    The processor includes validation to ensure PDF files contain valid book content
    and are suitable for spine width calculations.
    """

    def extract_page_count(self, pdf_path):
        """
        Extract page count from PDF file with minimal memory usage.

        This method uses pypdf's lazy loading capabilities to minimize memory usage
        when processing large PDF files. It only reads the PDF metadata and structure
        without loading the actual page content into memory.

        Args:
            pdf_path (str or Path): Path to PDF file to process.

        Returns:
            int: Number of pages in the PDF file.

        Raises:
            PDFProcessingError: If the PDF file cannot be processed, is invalid,
                corrupted, encrypted, or contains no pages.
            FileNotFoundError: If the PDF file does not exist.
        """
        pdf_path = Path(pdf_path)

        # Validate file exists
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Validate file extension
        if pdf_path.suffix.lower() != ".pdf":
            raise PDFProcessingError(f"File is not a PDF: {pdf_path}")

        # Validate file is not empty
        if pdf_path.stat().st_size == 0:
            raise PDFProcessingError(f"PDF file is empty: {pdf_path}")

        try:
            # Use pypdf's lazy loading to minimize memory usage
            # This only reads the PDF structure, not the actual page content
            with open(pdf_path, "rb") as file:
                reader = PdfReader(file, strict=False)

                # Validate this is a valid PDF with book content
                self._validate_pdf_content(reader, pdf_path)

                # Get page count without loading page content
                page_count = len(reader.pages)

                if page_count <= 0:
                    raise PDFProcessingError(f"PDF contains no pages: {pdf_path}")

                return page_count

        except PdfReadError as e:
            raise PDFProcessingError(f"Invalid or corrupted PDF file: {pdf_path}. Error: {str(e)}")
        except Exception as e:
            raise PDFProcessingError(f"Failed to process PDF file: {pdf_path}. Error: {str(e)}")

    def _validate_pdf_content(self, reader, pdf_path):
        """
        Validate that the PDF contains valid book content.

        This method performs basic validation to ensure the PDF is suitable for
        book spine calculation without loading page content into memory. It checks
        for the presence of pages, encryption status, basic PDF structure, and
        page dimensions.

        Args:
            reader (PdfReader): The PDF reader object containing the loaded PDF.
            pdf_path (Path): Path to the PDF file for error messages.

        Raises:
            PDFProcessingError: If the PDF doesn't contain valid book content,
                is encrypted, has structural issues, or has invalid page dimensions.
        """
        try:
            # Check if PDF has any pages
            if len(reader.pages) == 0:
                raise PDFProcessingError(f"PDF contains no pages: {pdf_path}")

            # Check if PDF is encrypted (which might indicate it's not a standard book)
            if reader.is_encrypted:
                raise PDFProcessingError(f"PDF is encrypted and cannot be processed: {pdf_path}")

            # Try to access the first page to ensure PDF structure is valid
            # This doesn't load the page content, just validates the structure
            first_page = reader.pages[0]

            # Basic validation that the page object exists and has expected structure
            if first_page is None:
                raise PDFProcessingError(f"PDF has invalid page structure: {pdf_path}")

            # Validate page dimensions
            if hasattr(first_page, "mediabox") and first_page.mediabox:
                width = first_page.mediabox.width
                height = first_page.mediabox.height

                # Check for invalid dimensions (zero or negative)
                if width <= 0 or height <= 0:
                    raise PDFProcessingError(f"PDF has invalid page dimensions: {pdf_path}")

                # Check for too small dimensions (less than 72 points = 1 inch)
                if width < 72 or height < 72:
                    raise PDFProcessingError(f"PDF page dimensions are too small to be a valid book: {pdf_path}")

        except Exception as e:
            raise PDFProcessingError(f"PDF validation failed: {pdf_path}. Error: {str(e)}")

    def extract_metadata(self, pdf_path):
        """
        Extract metadata from PDF file including page count and file size.

        This method extracts comprehensive metadata from a PDF file including
        page count and file size information. It uses memory-efficient processing
        to handle large files.

        Args:
            pdf_path (str or Path): Path to PDF file to process.

        Returns:
            PDFMetadata: Object containing page count and file size information.

        Raises:
            PDFProcessingError: If the PDF file cannot be processed, is invalid,
                corrupted, encrypted, or contains no pages.
            FileNotFoundError: If the PDF file does not exist.
        """
        pdf_path = Path(pdf_path)

        # Get file size in MB
        file_size_bytes = pdf_path.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)

        # Extract page count
        page_count = self.extract_page_count(pdf_path)

        # Create metadata object
        return PDFMetadata(page_count=page_count, file_size_mb=file_size_mb)

    def validate_pdf_file(self, pdf_path):
        """
        Validate that a PDF file is suitable for processing.

        This method performs comprehensive validation of a PDF file to ensure
        it can be processed for page count extraction. It checks file existence,
        format, size, and basic PDF structure.

        Args:
            pdf_path (str or Path): Path to PDF file to validate.

        Returns:
            bool: True if the PDF file is valid and suitable for processing.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            PDFProcessingError: If the PDF file is invalid, empty, or unsuitable
                for processing.
        """
        pdf_path = Path(pdf_path)

        # Check if file exists
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Check if file is a PDF
        if pdf_path.suffix.lower() != ".pdf":
            raise PDFProcessingError(f"File is not a PDF: {pdf_path}")

        # Check if file is empty
        if pdf_path.stat().st_size == 0:
            raise PDFProcessingError(f"PDF file is empty: {pdf_path}")

        # Try to open and validate the PDF structure
        try:
            with open(pdf_path, "rb") as file:
                reader = PdfReader(file, strict=False)
                self._validate_pdf_content(reader, pdf_path)
                return True
        except Exception as e:
            raise PDFProcessingError(f"PDF validation failed: {pdf_path}. Error: {str(e)}")
