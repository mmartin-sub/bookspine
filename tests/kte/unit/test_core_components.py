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
from kte.core.keybert_extractor import KeyBERTExtractor
from kte.core.output_handler import OutputHandler
from kte.core.result_formatter import ResultFormatter
from kte.models.extraction_options import ExtractionOptions
from kte.models.extraction_result import ExtractionResult
from kte.models.keyword_result import KeywordResult
from kte.utils.text_preprocessor import TextPreprocessor


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
        with patch("kte.utils.file_utils.FileUtils.extract_text_from_file") as mock_extract:
            mock_extract.return_value = ("File content", {"file_path": "test.txt"})

            result = handler.process_file_input("test.txt")

            assert result["text"] == "File content"
            assert result["source_type"] == "file"
            assert result["metadata"]["file_path"] == "test.txt"

    def test_process_input_with_file(self):
        """Test processing input with file path."""
        handler = InputHandler()

        with patch("kte.utils.file_utils.FileUtils.extract_text_from_file") as mock_extract:
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


class TestKeyBERTExtractor(unittest.TestCase):
    """Test cases for KeyBERTExtractor."""

    @patch("kte.core.keybert_extractor.KeyBERT")
    @patch("kte.core.keybert_extractor.UniversalEmbedder")
    def test_initialize_model_with_universal_embedder(self, mock_universal_embedder, mock_keybert):
        """Test that the universal embedder is used for remote engines."""
        extractor = KeyBERTExtractor(
            engine="hf",
            api_url="https://api.example.com",
            auth_token="test_token",
            model_name="test_model",
        )
        extractor._initialize_model()
        mock_universal_embedder.assert_called_once_with(
            engine="hf",
            api_url="https://api.example.com",
            auth_token="test_token",
            model_name="test_model",
        )
        mock_keybert.assert_called_once_with(model=mock_universal_embedder.return_value)

    @patch("kte.core.keybert_extractor.KeyBERT")
    @patch("sentence_transformers.SentenceTransformer")
    def test_initialize_model_with_local_embedder(self, mock_sentence_transformer, mock_keybert):
        """Test that the local embedder is used for the 'local' engine."""
        extractor = KeyBERTExtractor(
            engine="local",
            api_url="",
            model_name="test_model",
        )
        extractor._initialize_model()
        mock_sentence_transformer.assert_called_once_with("test_model")
        mock_keybert.assert_called_once_with(model=mock_sentence_transformer.return_value)

    def test_extract_keywords_short_text(self):
        """Test keyword extraction with short text."""
        extractor = KeyBERTExtractor(engine="local", api_url="")
        options = ExtractionOptions(max_keywords=5)

        with self.assertRaises(ValueError):
            extractor.extract_keywords("Short", options)

    def test_extract_keywords_empty_text(self):
        """Test keyword extraction with empty text."""
        extractor = KeyBERTExtractor(engine="local", api_url="")
        options = ExtractionOptions(max_keywords=5)

        with self.assertRaises(ValueError):
            extractor.extract_keywords("", options)


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
