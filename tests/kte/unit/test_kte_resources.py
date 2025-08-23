"""
Unit tests for KTE (Keyword Theme Extraction) on files in the resources folder.

This module tests all files found in the resources folder to ensure
they can be processed correctly by the KTE module.
"""

import tempfile
import unittest
from pathlib import Path

import pytest

from kte import ExtractionOptions, extract_keywords
from kte.utils.file_utils import FileUtils

RESOURCES_DIR = Path(__file__).parent.parent.parent / "resources"


class TestKTEResources:
    def test_resources_folder_exists(self):
        assert RESOURCES_DIR.exists() and RESOURCES_DIR.is_dir()

    def test_supported_files_exist(self):
        files = list(RESOURCES_DIR.glob("*"))
        assert any(f.suffix in {".pdf", ".md", ".txt"} for f in files)

    def test_all_pdf_files_can_be_processed_by_kte(self):
        for pdf in RESOURCES_DIR.glob("*.pdf"):
            text, metadata = FileUtils.extract_text_from_file(str(pdf))
            assert isinstance(text, str) and len(text) > 10
            result = extract_keywords(text)
            assert result.keywords and len(result.keywords) > 0

    def test_all_supported_files_can_be_processed(self):
        for f in RESOURCES_DIR.glob("*"):
            if f.suffix in {".pdf", ".md", ".txt"}:
                text, metadata = FileUtils.extract_text_from_file(str(f))
                assert isinstance(text, str) and len(text) > 10
                result = extract_keywords(text)
                assert result.keywords and len(result.keywords) > 0

    def test_pdf_files_with_custom_options(self):
        for pdf in RESOURCES_DIR.glob("*.pdf"):
            text, metadata = FileUtils.extract_text_from_file(str(pdf))
            options = {"max_keywords": 5, "min_relevance": 0.1, "header_weight_factor": 2.0}
            result = extract_keywords(text, options=options)
            assert len(result.keywords) <= 5

    def test_file_utils_detect_all_supported_formats(self):
        for f in RESOURCES_DIR.glob("*"):
            if f.suffix in {".pdf", ".md", ".txt"}:
                fmt = FileUtils.detect_file_format(str(f))
                assert fmt in {"md", "txt", "pdf"}

    def test_text_extraction_from_all_supported_files(self):
        for f in RESOURCES_DIR.glob("*"):
            if f.suffix in {".pdf", ".md", ".txt"}:
                text, metadata = FileUtils.extract_text_from_file(str(f))
                assert isinstance(text, str) and len(text) > 10

    def test_kte_consistency_across_multiple_runs(self):
        for f in RESOURCES_DIR.glob("*"):
            if f.suffix in {".pdf", ".md", ".txt"}:
                text, metadata = FileUtils.extract_text_from_file(str(f))
                result1 = extract_keywords(text)
                result2 = extract_keywords(text)
                assert result1.keywords == result2.keywords

    def test_kte_performance_on_resources(self):
        import time

        for f in RESOURCES_DIR.glob("*"):
            if f.suffix in {".pdf", ".md", ".txt"}:
                text, metadata = FileUtils.extract_text_from_file(str(f))
                start = time.time()
                try:
                    extract_keywords(text)  # Just call the function to test performance
                    elapsed = time.time() - start
                    # More lenient timeout for first-time model loading
                    max_time = 60 if "test1.pdf" in str(f) else 30
                    assert elapsed < max_time, f"KTE took too long on {f} ({elapsed:.2f}s)"
                except Exception as e:
                    if "429" in str(e) or "rate limit" in str(e).lower():
                        pytest.skip(f"Rate limited by Hugging Face Hub: {e}")
                    else:
                        raise

    def test_kte_output_formats(self):
        for f in RESOURCES_DIR.glob("*"):
            if f.suffix in {".pdf", ".md", ".txt"}:
                text, metadata = FileUtils.extract_text_from_file(str(f))
                result = extract_keywords(text)
                d = result.to_dict()
                assert isinstance(d, dict)
                assert "keywords" in d
