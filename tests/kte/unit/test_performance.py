"""
Performance tests for KTE module.

This module tests the performance characteristics of the keyword extraction
pipeline, including processing time and memory usage for various input sizes.
"""

import os
import time
import unittest
from pathlib import Path

import psutil
import pytest

from src.kte import ExtractionOptions, extract_keywords


class TestKTEPerformance:
    """Performance tests for KTE module."""

    def test_small_text_performance(self):
        """Test performance with small text input."""
        text = "This is a small test document about machine learning and data science."

        start_time = time.time()
        result = extract_keywords(text)
        end_time = time.time()

        processing_time = end_time - start_time

        # Small text should process in reasonable time (under 20 seconds including model loading)
        assert processing_time < 20.0
        assert len(result.keywords) > 0
        assert result.extraction_method == "KeyBERT"

    def test_medium_text_performance(self):
        """Test performance with medium text input."""
        text = """
        # Introduction to Data Science

        Data science is an interdisciplinary field that uses scientific methods,
        processes, algorithms, and systems to extract knowledge and insights from
        structured and unstructured data.

        ## Key Components

        ### Data Collection
        The first step in any data science project is collecting relevant data.

        ### Data Cleaning
        Raw data often contains errors, missing values, and inconsistencies.

        ### Data Analysis
        Once data is clean, analysis can begin with exploratory data analysis.

        ### Model Building
        Machine learning models are built to predict future outcomes and classify data.

        ## Applications

        Data science is used in various fields including business intelligence,
        healthcare, finance, and marketing. It helps organizations make better
        decisions and optimize their operations.
        """

        start_time = time.time()
        result = extract_keywords(text)
        end_time = time.time()

        processing_time = end_time - start_time

        # Medium text should process in reasonable time (under 25 seconds including model loading)
        assert processing_time < 25.0
        assert len(result.keywords) > 0
        assert result.extraction_method == "KeyBERT"

    def test_large_text_performance(self):
        """Test performance with large text input."""
        # Create a large text by repeating content
        base_text = """
        # Chapter {n}

        This is chapter {n} of a large document. It contains information about
        machine learning, artificial intelligence, and data science. The content
        includes various topics such as supervised learning, unsupervised learning,
        deep learning, neural networks, and statistical analysis.

        ## Section {n}.1

        This section discusses the fundamentals of machine learning algorithms
        and their applications in real-world scenarios.

        ## Section {n}.2

        This section covers advanced topics in artificial intelligence including
        natural language processing, computer vision, and robotics.

        ## Section {n}.3

        This section explores data science methodologies and best practices for
        data analysis and model development.
        """

        large_text = ""
        for i in range(1, 21):  # Create 20 chapters
            large_text += base_text.format(n=i)

        start_time = time.time()
        result = extract_keywords(large_text)
        end_time = time.time()

        processing_time = end_time - start_time

        # Large text should process in reasonable time (under 60 seconds including model loading)
        assert processing_time < 60.0
        assert len(result.keywords) > 0
        assert result.extraction_method == "KeyBERT"

    def test_memory_usage(self):
        """Test memory usage during extraction."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create medium-sized text
        text = """
        # Memory Test Document

        """ + "\n".join([f"## Section {i}\nContent for section {i}." for i in range(1, 51)])

        # Perform extraction
        result = extract_keywords(text)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (under 500MB)
        assert memory_increase < 500.0
        assert len(result.keywords) > 0

    def test_concurrent_processing_simulation(self):
        """Test that multiple extractions can be performed sequentially."""
        text = "This is a test document about machine learning and data science."

        results = []
        start_time = time.time()

        # Perform multiple extractions sequentially
        for _ in range(3):
            result = extract_keywords(text)
            results.append(result)

        end_time = time.time()
        total_time = end_time - start_time

        # Total time should be reasonable (under 60 seconds for 3 extractions with model loading)
        assert total_time < 60.0

        # All results should be valid
        for result in results:
            assert len(result.keywords) > 0
            assert result.extraction_method == "KeyBERT"

    def test_options_impact_on_performance(self):
        """Test how different options affect performance."""
        text = """
        # Performance Test Document

        This document tests how different extraction options affect processing time.
        It contains various topics including machine learning, data science,
        artificial intelligence, and statistical analysis.

        ## Machine Learning
        Machine learning algorithms and techniques.

        ## Data Science
        Data science methodologies and practices.

        ## Artificial Intelligence
        AI applications and developments.
        """

        # Test with default options
        start_time = time.time()
        result_default = extract_keywords(text)
        default_time = time.time() - start_time

        # Test with custom options
        options = {"max_keywords": 5, "min_relevance": 0.3, "header_weight_factor": 2.0, "prefer_phrases": True}

        start_time = time.time()
        result_custom = extract_keywords(text, options=options)
        custom_time = time.time() - start_time

        # Both should complete in reasonable time
        assert default_time < 10.0
        assert custom_time < 10.0

        # Results should be different due to options
        assert len(result_custom.keywords) <= 5
        assert len(result_default.keywords) >= len(result_custom.keywords)

    def test_file_input_performance(self):
        """Test performance with file input."""
        # Create a temporary file
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""
            # File Performance Test

            This document tests the performance of file-based keyword extraction.

            ## Section 1
            Content about machine learning and data science.

            ## Section 2
            More content about artificial intelligence and programming.

            ## Section 3
            Additional content about statistics and analysis.
            """)
            temp_file = f.name

        try:
            start_time = time.time()
            result = extract_keywords(temp_file)
            end_time = time.time()

            processing_time = end_time - start_time

            # File processing should be reasonable (under 15 seconds)
            assert processing_time < 15.0
            assert len(result.keywords) > 0
            assert result.extraction_method == "KeyBERT"

        finally:
            # Clean up
            os.unlink(temp_file)

    def test_error_handling_performance(self):
        """Test that error handling doesn't significantly impact performance."""
        # Test with invalid input
        start_time = time.time()

        with pytest.raises(ValueError):
            extract_keywords("")

        error_time = time.time() - start_time

        # Error handling should be fast (under 1 second)
        assert error_time < 1.0

        # Test with short but valid input that will fail KeyBERT extraction
        start_time = time.time()

        with pytest.raises(ValueError):
            extract_keywords("Short")

        short_error_time = time.time() - start_time

        # Short input error handling should also be fast
        assert short_error_time < 1.0

    def test_output_format_performance(self):
        """Test performance of different output formats."""
        text = """
        # Output Format Performance Test

        This document tests the performance of different output formats.

        ## JSON Output
        Testing JSON serialization performance.

        ## Console Output
        Testing console formatting performance.
        """

        result = extract_keywords(text)

        # Test JSON output performance
        start_time = time.time()
        json_output = result.to_json()
        json_time = time.time() - start_time

        # JSON serialization should be fast (under 0.1 seconds)
        assert json_time < 0.1
        assert isinstance(json_output, str)
        assert "keywords" in json_output

        # Test dictionary output performance
        start_time = time.time()
        dict_output = result.to_dict()
        dict_time = time.time() - start_time

        # Dictionary conversion should be fast (under 0.1 seconds)
        assert dict_time < 0.1
        assert isinstance(dict_output, dict)
        assert "keywords" in dict_output
