"""
Shared test utilities for the BookSpine project.

This module contains common functionality used across multiple test files,
including PDF generation, test data creation, and other shared utilities.
"""

import os
import tempfile
import time
from pathlib import Path


class PDFTestUtils:
    """Utilities for creating test PDF files."""

    @staticmethod
    def generate_pdf_content(page_count: int) -> bytes:
        """
        Generate PDF content with specified page count.

        This is a simplified PDF generation for testing purposes.
        In a real scenario, you'd use a proper PDF library.

        Args:
            page_count: Number of pages to include in the PDF.

        Returns:
            bytes: PDF content as bytes.
        """
        header = b"%PDF-1.4\n"
        trailer = b"\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n175\n%%EOF"

        # Create basic PDF structure
        catalog_obj = b"1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        pages_obj = b"2 0 obj\n<<\n/Type /Pages\n/Kids ["

        # Add page references
        page_refs = []
        for i in range(page_count):
            page_refs.append(f"{3 + i} 0 R".encode())

        pages_obj += b" ".join(page_refs) + b"]\n/Count " + str(page_count).encode() + b"\n>>\nendobj\n"

        # Create page objects
        page_objects = []
        for i in range(page_count):
            page_obj = f"{3 + i} 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\n".encode()
            page_objects.append(page_obj)

        return header + catalog_obj + pages_obj + b"".join(page_objects) + trailer

    @staticmethod
    def create_test_pdf(page_count: int) -> str:
        """
        Create a test PDF file with the specified number of pages.

        Args:
            page_count: Number of pages to include in the PDF.

        Returns:
            str: Path to the created PDF file.
        """
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            pdf_content = PDFTestUtils.generate_pdf_content(page_count)
            tmp_file.write(pdf_content)
            tmp_file.flush()
            return tmp_file.name

    @staticmethod
    def create_multiple_test_pdfs(page_counts: list[int]) -> list[str]:
        """
        Create multiple test PDF files with specified page counts.

        Args:
            page_counts: List of page counts for each PDF.

        Returns:
            List[str]: List of paths to the created PDF files.
        """
        pdf_files = []
        for page_count in page_counts:
            pdf_path = PDFTestUtils.create_test_pdf(page_count)
            pdf_files.append(pdf_path)
        return pdf_files

    @staticmethod
    def cleanup_pdf_files(pdf_files: list[str]) -> None:
        """
        Clean up test PDF files.

        Args:
            pdf_files: List of PDF file paths to delete.
        """
        for pdf_path in pdf_files:
            try:
                os.unlink(pdf_path)
            except OSError:
                pass  # File might already be deleted


class PerformanceTestUtils:
    """Utilities for performance testing."""

    @staticmethod
    def get_memory_usage() -> float:
        """
        Get current memory usage in MB.

        Returns:
            float: Memory usage in MB.
        """
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0  # psutil not available

    @staticmethod
    def measure_execution_time(func, *args, **kwargs) -> tuple[any, float]:
        """
        Measure execution time of a function.

        Args:
            func: Function to measure.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            Tuple[any, float]: Function result and execution time in seconds.
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time


class TestDataUtils:
    """Utilities for creating test data."""

    @staticmethod
    def create_book_metadata_cases() -> list[tuple[int, str, str, float]]:
        """
        Create a list of test cases for book metadata.

        Returns:
            List[Tuple[int, str, str, float]]: List of (page_count, paper_type, binding_type, paper_weight) tuples.
        """
        return [
            (100, "MCG", "Softcover Perfect Bound", 80),
            (200, "MCS", "Hardcover Casewrap", 100),
            (300, "ECB", "Hardcover Linen", 120),
            (400, "OFF", "Softcover Perfect Bound", 90),
            (500, "MCG", "Hardcover Casewrap", 110),
        ]

    @staticmethod
    def create_sample_text() -> str:
        """
        Create sample text for testing.

        Returns:
            str: Sample text content.
        """
        return """
        # Introduction to Machine Learning

        Machine learning is a subset of artificial intelligence that focuses on
        developing algorithms and statistical models that enable computers to
        perform tasks without explicit programming.

        ## Types of Machine Learning

        ### Supervised Learning
        Supervised learning involves training a model on labeled data.

        ### Unsupervised Learning
        Unsupervised learning finds patterns in unlabeled data.

        ## Applications

        Machine learning is used in various fields including:
        - Data science
        - Natural language processing
        - Computer vision
        - Robotics
        """

    @staticmethod
    def create_temp_file(content: str, suffix: str = ".txt") -> str:
        """
        Create a temporary file with the given content.

        Args:
            content: Content to write to the file.
            suffix: File extension.

        Returns:
            str: Path to the created temporary file.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(content)
            f.flush()
            return f.name


class TestAssertionUtils:
    """Utilities for test assertions."""

    @staticmethod
    def assert_spine_result_valid(result) -> None:
        """
        Assert that a spine result is valid.

        Args:
            result: SpineResult object to validate.
        """
        assert result.width_mm > 0
        assert result.width_inches > 0
        assert result.width_pixels > 0
        assert result.dpi == 300
        assert not result.manual_override_applied

    @staticmethod
    def assert_extraction_result_valid(result) -> None:
        """
        Assert that an extraction result is valid.

        Args:
            result: ExtractionResult object to validate.
        """
        assert len(result.keywords) > 0
        assert result.extraction_method == "KeyBERT"
        assert hasattr(result, "metadata")
        assert isinstance(result.metadata, dict)
