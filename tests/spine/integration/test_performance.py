"""
Performance integration tests for the BookSpine Calculator.

These tests focus on performance characteristics including memory usage,
processing speed, and parallel execution scenarios.
"""

import os
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import psutil
import pytest

from src.bookspine import BookMetadata, ConfigLoader, SpineCalculator
from src.bookspine.core.pdf_processor import PDFProcessor
from tests.test_utils import PDFTestUtils, PerformanceTestUtils, TestDataUtils


class TestMemoryUsagePerformance:
    """Test memory usage performance with large files."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config_loader = ConfigLoader()
        self.calculator = SpineCalculator(self.config_loader)
        self.pdf_processor = PDFProcessor()

    def get_memory_usage(self):
        """Get current memory usage in MB."""
        return PerformanceTestUtils.get_memory_usage()

    def create_large_pdf(self, page_count):
        """Create a large PDF file for testing."""
        return PDFTestUtils.create_test_pdf(page_count)

    def test_memory_usage_with_large_pdf(self):
        """Test memory usage when processing large PDF files."""
        # Test with different PDF sizes
        pdf_sizes = [100, 500, 1000, 2000]

        for page_count in pdf_sizes:
            pdf_path = self.create_large_pdf(page_count)

            try:
                # Measure memory before processing
                memory_before = self.get_memory_usage()

                # Process the PDF
                start_time = time.time()
                extracted_page_count = self.pdf_processor.extract_page_count(pdf_path)
                processing_time = time.time() - start_time

                # Measure memory after processing
                memory_after = self.get_memory_usage()
                memory_increase = memory_after - memory_before

                # Verify results
                assert extracted_page_count == page_count
                assert processing_time < 10.0  # Should complete within 10 seconds
                assert memory_increase < 100.0  # Should not increase memory by more than 100MB

                print(f"PDF with {page_count} pages: {processing_time:.2f}s, Memory increase: {memory_increase:.2f}MB")

            finally:
                os.unlink(pdf_path)

    def test_memory_efficiency_with_multiple_calculations(self):
        """Test memory efficiency when performing multiple calculations."""
        # Create metadata for multiple calculations
        test_cases = TestDataUtils.create_book_metadata_cases()

        memory_before = self.get_memory_usage()

        for page_count, paper_type, binding_type, paper_weight in test_cases:
            metadata = BookMetadata(
                page_count=page_count, paper_type=paper_type, binding_type=binding_type, paper_weight=paper_weight
            )

            result = self.calculator.calculate_spine_width(metadata)

            # Verify calculation is correct
            assert result.width_mm > 0
            assert result.book_metadata.page_count == page_count

        memory_after = self.get_memory_usage()
        memory_increase = memory_after - memory_before

        # Memory should not increase significantly
        assert memory_increase < 50.0  # Should not increase by more than 50MB

    def test_pdf_processing_memory_limits(self):
        """Test PDF processing with memory constraints."""
        # Test with very large PDF (simulated)
        large_page_count = 5000
        pdf_path = self.create_large_pdf(large_page_count)

        try:
            memory_before = self.get_memory_usage()

            # Process large PDF
            start_time = time.time()
            page_count = self.pdf_processor.extract_page_count(pdf_path)
            processing_time = time.time() - start_time

            memory_after = self.get_memory_usage()
            memory_increase = memory_after - memory_before

            # Verify processing completed successfully
            assert page_count == large_page_count
            assert processing_time < 30.0  # Should complete within 30 seconds
            assert memory_increase < 200.0  # Should not exceed 200MB increase

            print(f"Large PDF processing: {processing_time:.2f}s, Memory increase: {memory_increase:.2f}MB")

        finally:
            os.unlink(pdf_path)


class TestParallelExecutionPerformance:
    """Test parallel execution performance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config_loader = ConfigLoader()
        self.calculator = SpineCalculator(self.config_loader)

    def test_parallel_calculations(self):
        """Test parallel spine calculations."""
        import concurrent.futures

        # Create multiple calculation tasks
        test_cases = [
            (100, "MCG", "Softcover Perfect Bound", 80),
            (200, "MCS", "Hardcover Casewrap", 100),
            (300, "ECB", "Hardcover Linen", 120),
            (400, "OFF", "Softcover Perfect Bound", 90),
            (500, "MCG", "Hardcover Casewrap", 110),
        ]

        def calculate_spine(args):
            page_count, paper_type, binding_type, paper_weight = args
            metadata = BookMetadata(
                page_count=page_count, paper_type=paper_type, binding_type=binding_type, paper_weight=paper_weight
            )
            return self.calculator.calculate_spine_width(metadata)

        # Test sequential execution
        start_time = time.time()
        sequential_results = []
        for case in test_cases:
            result = calculate_spine(case)
            sequential_results.append(result)
        sequential_time = time.time() - start_time

        # Test parallel execution
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            parallel_results = list(executor.map(calculate_spine, test_cases))
        parallel_time = time.time() - start_time

        # Verify results are consistent
        for seq_result, par_result in zip(sequential_results, parallel_results):
            assert abs(seq_result.width_mm - par_result.width_mm) < 0.001

        print(f"Sequential time: {sequential_time:.3f}s")
        print(f"Parallel time: {parallel_time:.3f}s")

        # Parallel should be faster (though with small datasets, overhead might make it slower)
        # We just verify it completes successfully

    def test_concurrent_pdf_processing(self):
        """Test concurrent PDF processing."""
        import concurrent.futures

        # Create multiple PDF files
        page_counts = [100, 200, 300, 400, 500]
        pdf_files = PDFTestUtils.create_multiple_test_pdfs(page_counts)

        try:

            def process_pdf(pdf_path):
                pdf_processor = PDFProcessor()
                return pdf_processor.extract_page_count(pdf_path)

            # Test parallel PDF processing
            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                results = list(executor.map(process_pdf, pdf_files))
            parallel_time = time.time() - start_time

            # Verify results
            for expected, actual in zip(page_counts, results):
                assert expected == actual

            print(f"Parallel PDF processing time: {parallel_time:.3f}s")

        finally:
            # Clean up PDF files
            PDFTestUtils.cleanup_pdf_files(pdf_files)

    def _create_test_pdf(self, page_count):
        """Create a test PDF file."""
        return PDFTestUtils.create_test_pdf(page_count)

    def test_thread_safety(self):
        """Test thread safety of calculator operations."""
        import concurrent.futures

        # Test concurrent access to calculator
        results = []
        errors = []

        def calculate_with_metadata(metadata):
            try:
                result = self.calculator.calculate_spine_width(metadata)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads with different metadata
        threads = []
        for i in range(10):
            metadata = BookMetadata(
                page_count=100 + i * 50, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
            )
            thread = threading.Thread(target=calculate_with_metadata, args=(metadata,))
            threads.append(thread)

        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        execution_time = time.time() - start_time

        # Verify no errors occurred
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 10, "Expected 10 results"

        # Verify all results are valid
        for result in results:
            assert result.width_mm > 0
            assert isinstance(result, type(results[0]))  # All should be same type

        print(f"Thread safety test completed in {execution_time:.3f}s")


class TestPerformanceBenchmarks:
    """Test performance benchmarks."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config_loader = ConfigLoader()
        self.calculator = SpineCalculator(self.config_loader)

    def test_calculation_speed_benchmark(self):
        """Benchmark calculation speed."""
        # Test calculation speed with different page counts
        page_counts = [50, 100, 200, 500, 1000]

        for page_count in page_counts:
            metadata = BookMetadata(
                page_count=page_count, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
            )

            # Measure calculation time
            start_time = time.time()
            result = self.calculator.calculate_spine_width(metadata)
            calculation_time = time.time() - start_time

            # Verify result
            assert result.width_mm > 0

            # Performance requirements
            assert calculation_time < 0.1, f"Calculation took {calculation_time:.3f}s for {page_count} pages"

            print(f"{page_count} pages: {calculation_time:.6f}s")

    def test_memory_efficiency_benchmark(self):
        """Benchmark memory efficiency."""
        import gc

        # Force garbage collection
        gc.collect()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Perform many calculations
        for i in range(1000):
            metadata = BookMetadata(
                page_count=100 + (i % 100), paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
            )
            result = self.calculator.calculate_spine_width(metadata)
            assert result.width_mm > 0

        # Force garbage collection again
        gc.collect()
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        # Memory should not increase significantly
        assert memory_increase < 50.0, f"Memory increased by {memory_increase:.2f}MB"

        print(f"Memory efficiency test: {memory_increase:.2f}MB increase after 1000 calculations")

    def test_large_scale_processing_benchmark(self):
        """Benchmark large-scale processing."""
        # Test processing many different configurations
        configurations = []
        for page_count in range(50, 1001, 50):
            for paper_type in ["MCG", "MCS", "ECB", "OFF"]:
                for binding_type in ["Softcover Perfect Bound", "Hardcover Casewrap", "Hardcover Linen"]:
                    configurations.append((page_count, paper_type, binding_type, 80))

        start_time = time.time()
        results = []

        for page_count, paper_type, binding_type, paper_weight in configurations[:100]:  # Limit for testing
            metadata = BookMetadata(
                page_count=page_count, paper_type=paper_type, binding_type=binding_type, paper_weight=paper_weight
            )
            result = self.calculator.calculate_spine_width(metadata)
            results.append(result)

        processing_time = time.time() - start_time

        # Verify all calculations completed
        assert len(results) == 100
        for result in results:
            assert result.width_mm > 0

        # Performance requirements
        assert processing_time < 10.0, f"Large-scale processing took {processing_time:.2f}s"

        print(f"Large-scale processing: {len(results)} calculations in {processing_time:.2f}s")
        print(f"Average time per calculation: {processing_time / len(results):.6f}s")
