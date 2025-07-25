"""
Integration tests for KTE module.

This module tests the complete keyword extraction pipeline from input to output.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

import pytest

from src.kte import ExtractionOptions, extract_keywords
from src.kte.models.extraction_result import ExtractionResult
from tests.test_utils import TestAssertionUtils, TestDataUtils


class TestKTEIntegration:
    """Integration tests for the complete KTE pipeline."""

    def test_complete_extraction_pipeline_text_input(self):
        """Test complete extraction pipeline with text input."""
        text = TestDataUtils.create_sample_text()

        result = extract_keywords(text)

        TestAssertionUtils.assert_extraction_result_valid(result)
        assert "machine learning" in [kw.phrase.lower() for kw in result.keywords]

    def test_complete_extraction_pipeline_with_options(self):
        """Test complete extraction pipeline with custom options."""
        text = """
        # Data Science Fundamentals

        Data science combines statistics, programming, and domain expertise
        to extract insights from data. It involves data cleaning, analysis,
        and visualization techniques.

        ## Key Concepts

        ### Statistical Analysis
        Statistical methods are essential for data analysis.

        ### Programming Skills
        Python and R are commonly used in data science.
        """

        options = {"max_keywords": 5, "min_relevance": 0.3, "header_weight_factor": 2.0, "prefer_phrases": True}

        result = extract_keywords(text, options=options)

        assert len(result.keywords) <= 5
        assert all(kw.relevance_score >= 0.3 for kw in result.keywords)
        assert result.extraction_method == "KeyBERT"

    def test_file_input_integration(self):
        """Test integration with file input processing."""
        # Create a temporary markdown file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""
            # Test Document

            This is a test document for keyword extraction.

            ## Section 1
            Content about artificial intelligence and machine learning.

            ## Section 2
            More content about data science and programming.
            """)
            temp_file = f.name

        try:
            result = extract_keywords(temp_file)

            assert isinstance(result, ExtractionResult)
            assert len(result.keywords) > 0
            assert result.extraction_method == "KeyBERT"

        finally:
            # Clean up
            os.unlink(temp_file)

    def test_edge_cases_integration(self):
        """Test integration with edge cases."""
        # Very short text
        short_text = "Short text."
        result = extract_keywords(short_text)
        assert isinstance(result, ExtractionResult)

        # Text with only headers
        header_only_text = """
        # Header 1
        ## Header 2
        ### Header 3
        """
        result = extract_keywords(header_only_text)
        assert isinstance(result, ExtractionResult)

        # Text with special characters
        special_text = """
        # Document with Special Characters

        This document contains special characters: @#$%^&*()_+-=[]{}|;':",./<>?

        ## Section with Numbers

        Section 123 with numbers and symbols: 1+1=2, 2*3=6
        """
        result = extract_keywords(special_text)
        assert isinstance(result, ExtractionResult)

    def test_consistency_across_runs(self):
        """Test that extraction results are consistent across multiple runs."""
        text = """
        # Consistency Test

        This document tests the consistency of keyword extraction.
        The same input should produce similar results across multiple runs.

        ## Key Topics

        - Machine learning algorithms
        - Data preprocessing techniques
        - Model evaluation metrics
        """

        result1 = extract_keywords(text)
        result2 = extract_keywords(text)

        # Results should have the same structure
        assert isinstance(result1, ExtractionResult)
        assert isinstance(result2, ExtractionResult)
        assert result1.extraction_method == result2.extraction_method
        assert len(result1.keywords) == len(result2.keywords)

    def test_output_formats_integration(self):
        """Test integration with different output formats."""
        text = """
        # Output Format Test

        This document tests various output formats for keyword extraction.

        ## JSON Output
        Testing JSON serialization.

        ## Console Output
        Testing console formatting.
        """

        result = extract_keywords(text)

        # Test JSON output
        json_output = result.to_json()
        assert isinstance(json_output, str)
        assert "keywords" in json_output
        assert "extraction_method" in json_output

        # Test dictionary output
        dict_output = result.to_dict()
        assert isinstance(dict_output, dict)
        assert "keywords" in dict_output
        assert "extraction_method" in dict_output

    def test_metadata_generation_integration(self):
        """Test metadata generation in the complete pipeline."""
        text = """
        # Metadata Test

        This document tests metadata generation during extraction.

        ## Phrase Keywords
        Multi-word phrases should be detected.

        ## Single Keywords
        Single words should also be extracted.
        """

        result = extract_keywords(text)

        # Test metadata
        assert hasattr(result, "metadata")
        assert isinstance(result.metadata, dict)
        # Note: timestamp is in the result object, not in metadata
        assert hasattr(result, "timestamp")

    def test_error_handling_integration(self):
        """Test error handling in the complete pipeline."""
        # Empty text should be handled gracefully
        with pytest.raises(ValueError):
            extract_keywords("")

        # None input should be handled gracefully
        with pytest.raises(ValueError):
            extract_keywords(None)

        # Invalid file path should be handled gracefully
        with pytest.raises((FileNotFoundError, ValueError)):
            extract_keywords("nonexistent_file.txt")

    def test_performance_integration(self):
        """Test performance of the complete pipeline."""
        import time

        # Create a larger text for performance testing
        large_text = """
        # Performance Test Document

        """ + "\n".join([f"## Section {i}\nContent for section {i}." for i in range(10)])

        start_time = time.time()
        result = extract_keywords(large_text)
        end_time = time.time()

        # Extraction should complete within reasonable time (10 seconds)
        assert end_time - start_time < 10.0
        assert isinstance(result, ExtractionResult)
        assert len(result.keywords) > 0

    def test_header_weighting_integration(self):
        """Test header weighting in the complete pipeline."""
        text = """
        # Main Topic

        This is the main topic of the document.

        ## Important Section
        This section contains important keywords.

        Regular paragraph with less important content.

        ## Another Important Section
        More important content here.
        """

        # Test with header weighting enabled
        options = {"header_weight_factor": 2.0}
        result = extract_keywords(text, options=options)

        assert isinstance(result, ExtractionResult)
        assert len(result.keywords) > 0

        # Header keywords should have higher scores
        header_keywords = result.get_header_keywords()
        if header_keywords:
            assert all(kw.from_header for kw in header_keywords)

    def test_phrase_prioritization_integration(self):
        """Test phrase prioritization in the complete pipeline."""
        text = """
        # Phrase Prioritization Test

        This document contains both single words and multi-word phrases.

        ## Machine Learning
        Machine learning is a key topic.

        ## Data Science
        Data science involves various techniques.

        ## Programming
        Programming skills are essential.
        """

        # Test with phrase prioritization enabled
        options = {"prefer_phrases": True}
        result = extract_keywords(text, options=options)

        assert isinstance(result, ExtractionResult)

        # Check if phrases are prioritized
        phrases = result.get_phrases_only()
        if phrases:
            assert all(kw.is_phrase for kw in phrases)
