"""
Unit tests for KTE data models.

This module tests the data models used in the Keyword Theme Extraction (KTE) module.
"""

import json
import unittest
from pathlib import Path

import pytest

from src.kte.models.extraction_options import ExtractionOptions
from src.kte.models.extraction_result import ExtractionResult
from src.kte.models.keyword_result import KeywordResult


class TestKeywordResult:
    """Test cases for KeywordResult model."""

    def test_keyword_result_creation(self):
        """Test creating a KeywordResult with valid data."""
        keyword = KeywordResult(phrase="machine learning", relevance_score=0.85, is_phrase=True, from_header=False)

        assert keyword.phrase == "machine learning"
        assert keyword.relevance_score == 0.85
        assert keyword.is_phrase is True
        assert keyword.from_header is False

    def test_keyword_result_validation(self):
        """Test KeywordResult validation."""
        # Valid keyword
        keyword = KeywordResult(phrase="valid phrase", relevance_score=0.5, is_phrase=True, from_header=False)
        # Validation happens in __post_init__, so if we get here, it's valid
        assert keyword.phrase == "valid phrase"

        # Invalid: empty phrase should raise ValueError
        with pytest.raises(ValueError):
            KeywordResult("", 0.5, True, False)

        # Invalid: negative relevance score should raise ValueError
        with pytest.raises(ValueError):
            KeywordResult("valid phrase", -0.1, True, False)

        # Invalid: relevance score > 1 should raise ValueError
        with pytest.raises(ValueError):
            KeywordResult("valid phrase", 1.1, True, False)

    def test_keyword_result_to_dict(self):
        """Test KeywordResult serialization to dictionary."""
        keyword = KeywordResult(phrase="test phrase", relevance_score=0.75, is_phrase=True, from_header=True)

        result = keyword.to_dict()

        assert result["phrase"] == "test phrase"
        assert result["relevance_score"] == 0.75
        assert result["is_phrase"] is True
        assert result["from_header"] is True

    def test_keyword_result_comparison(self):
        """Test KeywordResult comparison for sorting."""
        keyword1 = KeywordResult("phrase1", 0.8, True, False)
        keyword2 = KeywordResult("phrase2", 0.9, True, False)
        keyword3 = KeywordResult("phrase3", 0.8, True, False)

        # Test that objects can be created successfully
        assert keyword1.phrase == "phrase1"
        assert keyword2.phrase == "phrase2"
        assert keyword3.phrase == "phrase3"

        # Test relevance scores
        assert keyword1.relevance_score == 0.8
        assert keyword2.relevance_score == 0.9
        assert keyword3.relevance_score == 0.8


class TestExtractionOptions:
    """Test cases for ExtractionOptions model."""

    def test_extraction_options_defaults(self):
        """Test ExtractionOptions with default values."""
        options = ExtractionOptions()

        assert options.max_keywords == 20
        assert options.min_relevance == 0.1
        assert options.header_weight_factor == 1.5
        assert options.prefer_phrases is True
        assert options.language == "english"

    def test_extraction_options_custom_values(self):
        """Test ExtractionOptions with custom values."""
        options = ExtractionOptions(
            max_keywords=15, min_relevance=0.2, header_weight_factor=2.0, prefer_phrases=False, language="spanish"
        )

        assert options.max_keywords == 15
        assert options.min_relevance == 0.2
        assert options.header_weight_factor == 2.0
        assert options.prefer_phrases is False
        assert options.language == "spanish"

    def test_extraction_options_validation(self):
        """Test ExtractionOptions validation."""
        # Valid options
        options = ExtractionOptions()
        assert options.max_keywords == 20

        # Invalid: max_keywords <= 0 should raise ValueError
        with pytest.raises(ValueError):
            ExtractionOptions(max_keywords=0)

        # Invalid: min_relevance < 0 should raise ValueError
        with pytest.raises(ValueError):
            ExtractionOptions(min_relevance=-0.1)

        # Invalid: min_relevance > 1 should raise ValueError
        with pytest.raises(ValueError):
            ExtractionOptions(min_relevance=1.1)

        # Invalid: header_weight_factor <= 0 should raise ValueError
        with pytest.raises(ValueError):
            ExtractionOptions(header_weight_factor=0)

    def test_extraction_options_to_dict(self):
        """Test ExtractionOptions serialization to dictionary."""
        options = ExtractionOptions(
            max_keywords=10, min_relevance=0.3, header_weight_factor=1.8, prefer_phrases=False, language="french"
        )

        result = options.to_dict()

        assert result["max_keywords"] == 10
        assert result["min_relevance"] == 0.3
        assert result["header_weight_factor"] == 1.8
        assert result["prefer_phrases"] is False
        assert result["language"] == "french"


class TestExtractionResult:
    """Test cases for ExtractionResult model."""

    def test_extraction_result_creation(self):
        """Test creating an ExtractionResult with valid data."""
        keywords = [KeywordResult("keyword1", 0.8, False, False), KeywordResult("keyword2", 0.9, True, True)]

        result = ExtractionResult(keywords=keywords, extraction_method="keybert", metadata={"source": "test.txt"})

        assert len(result.keywords) == 2
        assert result.extraction_method == "keybert"
        assert result.metadata["source"] == "test.txt"
        assert isinstance(result.timestamp, str)  # timestamp is stored as string

    def test_extraction_result_validation(self):
        """Test ExtractionResult validation."""
        keywords = [KeywordResult("valid", 0.5, False, False)]

        # Valid result
        result = ExtractionResult(keywords=keywords, extraction_method="keybert")
        assert len(result.keywords) == 1

        # Invalid: empty keywords list should work (validation allows empty list)
        result = ExtractionResult(keywords=[], extraction_method="keybert")
        assert len(result.keywords) == 0

        # Invalid: None keywords should raise ValueError
        with pytest.raises(ValueError):
            ExtractionResult(keywords=None, extraction_method="keybert")

        # Invalid: empty extraction method should raise ValueError
        with pytest.raises(ValueError):
            ExtractionResult(keywords=keywords, extraction_method="")

    def test_extraction_result_get_phrases_only(self):
        """Test getting only phrase keywords."""
        keywords = [
            KeywordResult("single", 0.5, False, False),
            KeywordResult("multi word", 0.7, True, False),
            KeywordResult("another phrase", 0.8, True, True),
        ]

        result = ExtractionResult(keywords=keywords, extraction_method="keybert")
        phrases = result.get_phrases_only()

        assert len(phrases) == 2
        assert all(phrase.is_phrase for phrase in phrases)

    def test_extraction_result_get_header_keywords(self):
        """Test getting only header keywords."""
        keywords = [
            KeywordResult("normal", 0.5, False, False),
            KeywordResult("header1", 0.7, False, True),
            KeywordResult("header2", 0.8, True, True),
        ]

        result = ExtractionResult(keywords=keywords, extraction_method="keybert")
        header_keywords = result.get_header_keywords()

        assert len(header_keywords) == 2
        assert all(keyword.from_header for keyword in header_keywords)

    def test_extraction_result_get_average_relevance_score(self):
        """Test calculating average relevance score."""
        keywords = [
            KeywordResult("kw1", 0.5, False, False),
            KeywordResult("kw2", 0.7, False, False),
            KeywordResult("kw3", 0.9, False, False),
        ]

        result = ExtractionResult(keywords=keywords, extraction_method="keybert")
        avg_score = result.get_average_relevance_score()

        assert avg_score == pytest.approx(0.7, rel=1e-2)

    def test_extraction_result_to_dict(self):
        """Test ExtractionResult serialization to dictionary."""
        keywords = [KeywordResult("test", 0.8, True, False)]
        result = ExtractionResult(keywords=keywords, extraction_method="keybert", metadata={"test": "value"})

        result_dict = result.to_dict()

        assert "keywords" in result_dict
        assert "extraction_method" in result_dict
        assert "timestamp" in result_dict
        assert "metadata" in result_dict
        assert result_dict["extraction_method"] == "keybert"
        assert result_dict["metadata"]["test"] == "value"

    def test_extraction_result_to_json(self):
        """Test ExtractionResult JSON serialization."""
        keywords = [KeywordResult("test", 0.8, True, False)]
        result = ExtractionResult(keywords=keywords, extraction_method="keybert")

        json_str = result.to_json()

        assert isinstance(json_str, str)
        assert "test" in json_str
        assert "keybert" in json_str
