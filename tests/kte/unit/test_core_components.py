"""
Unit tests for KTE core components.

This module tests the core components of the Keyword Theme Extraction (KTE) module.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.kte.core.header_weighting import HeaderWeighting
from src.kte.core.input_handler import InputHandler
from src.kte.core.keybert_extractor import KeyBERTExtractor
from src.kte.core.output_handler import OutputHandler
from src.kte.core.result_formatter import ResultFormatter
from src.kte.models.extraction_options import ExtractionOptions
from src.kte.models.extraction_result import ExtractionResult
from src.kte.models.keyword_result import KeywordResult
from src.kte.utils.text_preprocessor import TextPreprocessor


class TestInputHandler:
    """Test cases for InputHandler."""

    def test_input_handler_creation(self):
        """Test InputHandler creation."""
        handler = InputHandler()
        assert handler is not None

    def test_validate_input_text_valid(self):
        """Test input text validation with valid text."""
        handler = InputHandler()

        # Valid text
        assert handler.validate_input_text("This is valid text with sufficient content.")

        # Invalid: too short
        assert not handler.validate_input_text("Short")

        # Invalid: empty
        assert not handler.validate_input_text("")

        # Invalid: None
        assert not handler.validate_input_text(None)

    def test_process_text_input(self):
        """Test processing text input."""
        handler = InputHandler()
        text = "This is a test document with some content."

        result = handler.process_text_input(text)

        assert result["text"] == text
        assert result["source_type"] == "text"
        assert "timestamp" in result

    def test_process_file_input(self):
        """Test processing file input."""
        handler = InputHandler()

        # Mock file processing
        with patch("src.kte.utils.file_utils.FileUtils.extract_text_from_file") as mock_extract:
            mock_extract.return_value = ("File content", {"file_path": "test.txt"})

            result = handler.process_file_input("test.txt")

            assert result["text"] == "File content"
            assert result["source_type"] == "file"
            assert result["metadata"]["file_path"] == "test.txt"

    def test_process_input_with_file(self):
        """Test processing input with file path."""
        handler = InputHandler()

        with patch("src.kte.utils.file_utils.FileUtils.extract_text_from_file") as mock_extract:
            mock_extract.return_value = ("File content", {"file_path": "test.txt"})

            result = handler.process_input("test.txt")

            assert result["text"] == "File content"
            assert result["source_type"] == "file"

    def test_process_input_with_text(self):
        """Test processing input with text content."""
        handler = InputHandler()
        text = "Direct text input"

        result = handler.process_input(text, is_text=True)

        assert result["text"] == text
        assert result["source_type"] == "text"


class TestTextPreprocessor:
    """Test cases for TextPreprocessor."""

    def test_text_preprocessor_creation(self):
        """Test TextPreprocessor creation."""
        preprocessor = TextPreprocessor()
        assert preprocessor is not None

    def test_normalize_text(self):
        """Test text normalization."""
        preprocessor = TextPreprocessor()

        text = "  This   is   a   test   with   extra   spaces  "
        normalized = preprocessor.normalize_text(text)

        assert normalized == "This is a test with extra spaces"

    def test_detect_headers(self):
        """Test header detection in text."""
        text = """
        # Main Title
        Content here.

        ## Subtitle
        More content.

        Regular paragraph text.
        """

        headers = TextPreprocessor.detect_headers(text)

        assert len(headers) == 2
        assert any("Main Title" in header["content"] for header in headers)
        assert any("Subtitle" in header["content"] for header in headers)

    def test_identify_structural_elements(self):
        """Test structural element identification."""
        text = """
        # Chapter 1
        Introduction content.

        ## Section 1.1
        Section content.

        ## Section 1.2
        More section content.

        Regular paragraph.
        """

        elements = TextPreprocessor.identify_structural_elements(text)

        assert elements["header_count"] == 3
        assert elements["has_structure"] is True
        assert len(elements["headers"]) == 3


class TestKeyBERTExtractor:
    """Test cases for KeyBERTExtractor."""

    def test_keybert_extractor_creation(self):
        """Test KeyBERTExtractor creation."""
        extractor = KeyBERTExtractor()
        assert extractor is not None

    @patch("builtins.__import__")
    def test_extract_keywords_success(self, mock_import):
        """Test successful keyword extraction."""
        # Mock the imports
        mock_keybert = Mock()
        mock_sentence_transformer = Mock()
        mock_sentence_model = Mock()
        mock_logging = Mock()
        mock_logger = Mock()
        mock_logging.getLogger.return_value = mock_logger

        def mock_import_side_effect(name, *args, **kwargs):
            if name == "keybert":
                return mock_keybert
            elif name == "sentence_transformers":
                return mock_sentence_transformer
            elif name == "logging":
                return mock_logging
            else:
                # For all other imports, use the real import to avoid recursion
                return __import__(name, *args, **kwargs)

        mock_import.side_effect = mock_import_side_effect
        mock_sentence_transformer.SentenceTransformer.return_value = mock_sentence_model
        mock_keybert.KeyBERT.return_value = Mock()

        extractor = KeyBERTExtractor()
        options = ExtractionOptions(max_keywords=5)

        # Mock the extract_keywords method to return test data
        with patch.object(extractor, "_extract_with_keybert") as mock_extract:
            mock_extract.return_value = [
                ("machine learning", 0.9),
                ("artificial intelligence", 0.8),
                ("data science", 0.7),
            ]

            result = extractor.extract_keywords("Test text about machine learning.", options)

            assert len(result) == 3
            assert all(isinstance(kw, KeywordResult) for kw in result)
            assert result[0].phrase == "machine learning"
            assert result[0].relevance_score == 0.9

    def test_extract_keywords_short_text(self):
        """Test keyword extraction with short text."""
        extractor = KeyBERTExtractor()
        options = ExtractionOptions(max_keywords=5)

        with pytest.raises(ValueError, match="Text is too short"):
            extractor.extract_keywords("Short", options)

    def test_extract_keywords_empty_text(self):
        """Test keyword extraction with empty text."""
        extractor = KeyBERTExtractor()
        options = ExtractionOptions(max_keywords=5)

        with pytest.raises(ValueError, match="Text cannot be empty"):
            extractor.extract_keywords("", options)

    def test_filter_keywords(self):
        """Test keyword filtering."""
        extractor = KeyBERTExtractor()
        options = ExtractionOptions(max_keywords=2, min_relevance=0.5)

        raw_keywords = [("high score", 0.9), ("medium score", 0.6), ("low score", 0.3)]

        filtered = extractor._filter_keywords(raw_keywords, options)

        assert len(filtered) == 2  # max_keywords limit
        assert all(score >= 0.5 for _, score in filtered)  # min_relevance filter


class TestHeaderWeighting:
    """Test cases for HeaderWeighting."""

    def test_header_weighting_creation(self):
        """Test HeaderWeighting creation."""
        weighting = HeaderWeighting()
        assert weighting is not None

    def test_identify_header_content(self):
        """Test header content identification."""
        weighting = HeaderWeighting()

        text = """
        # Main Title
        Content here.

        ## Subtitle
        More content.

        Regular paragraph text.
        """

        headers = weighting.identify_header_content(text)

        assert "Main Title" in headers
        assert "Subtitle" in headers
        assert "Regular paragraph text" not in headers

    def test_adjust_relevance_scores(self):
        """Test relevance score adjustment."""
        weighting = HeaderWeighting()
        options = ExtractionOptions(header_weight_factor=2.0)

        keywords = [KeywordResult("header term", 0.5, False, True), KeywordResult("regular term", 0.5, False, False)]

        adjusted = weighting.adjust_relevance_scores(keywords, options)

        # Header term should have higher score
        header_keyword = next(kw for kw in adjusted if kw.from_header)
        regular_keyword = next(kw for kw in adjusted if not kw.from_header)

        assert header_keyword.relevance_score > regular_keyword.relevance_score

    def test_different_header_levels(self):
        """Test different header level weighting."""
        weighting = HeaderWeighting()

        text = """
        # Level 1 Header
        ## Level 2 Header
        ### Level 3 Header
        Regular text.
        """

        headers = weighting.identify_header_content(text)

        assert "Level 1 Header" in headers
        assert "Level 2 Header" in headers
        assert "Level 3 Header" in headers


class TestResultFormatter:
    """Test cases for ResultFormatter."""

    def test_result_formatter_creation(self):
        """Test ResultFormatter creation."""
        formatter = ResultFormatter()
        assert formatter is not None

    def test_rank_keywords_by_relevance(self):
        """Test keyword ranking by relevance score."""
        formatter = ResultFormatter()

        keywords = [
            KeywordResult("low", 0.3, False, False),
            KeywordResult("high", 0.9, False, False),
            KeywordResult("medium", 0.6, False, False),
        ]

        ranked = formatter.rank_keywords_by_relevance(keywords)

        assert ranked[0].relevance_score == 0.9
        assert ranked[1].relevance_score == 0.6
        assert ranked[2].relevance_score == 0.3

    def test_prioritize_phrases(self):
        """Test phrase prioritization."""
        formatter = ResultFormatter()
        options = ExtractionOptions(prefer_phrases=True)

        keywords = [
            KeywordResult("single", 0.8, False, False),
            KeywordResult("multi word", 0.7, True, False),
            KeywordResult("another phrase", 0.6, True, False),
        ]

        prioritized = formatter.prioritize_phrases(keywords, options)

        # Phrases should come first
        assert prioritized[0].is_phrase is True
        assert prioritized[1].is_phrase is True
        assert prioritized[2].is_phrase is False

    def test_filter_and_limit_results(self):
        """Test result filtering and limiting."""
        formatter = ResultFormatter()
        options = ExtractionOptions(max_keywords=2, min_relevance=0.5)

        keywords = [
            KeywordResult("high", 0.9, False, False),
            KeywordResult("medium", 0.6, False, False),
            KeywordResult("low", 0.3, False, False),
        ]

        filtered = formatter.filter_and_limit_results(keywords, options)

        assert len(filtered) == 2  # max_keywords limit
        assert all(kw.relevance_score >= 0.5 for kw in filtered)  # min_relevance filter

    def test_generate_metadata(self):
        """Test metadata generation."""
        formatter = ResultFormatter()

        keywords = [KeywordResult("test1", 0.8, True, False), KeywordResult("test2", 0.6, False, True)]

        metadata = formatter.generate_metadata(keywords, "test_source")

        assert metadata["source"] == "test_source"
        assert metadata["total_keywords"] == 2
        assert metadata["phrases_count"] == 1
        assert metadata["header_keywords_count"] == 1
        assert metadata["average_relevance"] == pytest.approx(0.7, rel=1e-2)
