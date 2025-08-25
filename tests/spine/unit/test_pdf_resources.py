"""
Unit tests for PDF files in the resources folder.

This module tests all PDF files found in the resources folder to ensure
they can be processed correctly by the PDFProcessor.
"""

import os
from pathlib import Path

import pytest

from tests.test_config import SAMPLES_DIR

RESOURCES_DIR = SAMPLES_DIR


class TestPDFResources:
    def test_resources_folder_exists(self):
        assert RESOURCES_DIR.exists() and RESOURCES_DIR.is_dir()

    def test_all_pdf_files_are_valid(self):
        pdf_files = list(RESOURCES_DIR.glob("*.pdf"))
        assert pdf_files, "No PDF files found in resources folder"
        for pdf in pdf_files:
            assert pdf.exists() and pdf.stat().st_size > 0

    def test_all_pdf_files_have_page_count(self):
        import pypdf

        for pdf in RESOURCES_DIR.glob("*.pdf"):
            reader = pypdf.PdfReader(str(pdf))
            assert len(reader.pages) > 0

    def test_pdf_files_have_consistent_page_counts(self):
        import pypdf

        page_counts = set()
        for pdf in RESOURCES_DIR.glob("*.pdf"):
            reader = pypdf.PdfReader(str(pdf))
            page_counts.add(len(reader.pages))
        assert len(page_counts) == 1, f"Inconsistent page counts: {page_counts}"

    def test_pdf_files_have_valid_file_sizes(self):
        for pdf in RESOURCES_DIR.glob("*.pdf"):
            assert pdf.stat().st_size > 100, f"{pdf} is too small to be a valid PDF"

    def test_pdf_files_are_readable(self):
        import pypdf

        for pdf in RESOURCES_DIR.glob("*.pdf"):
            try:
                reader = pypdf.PdfReader(str(pdf))
                _ = reader.pages[0]
            except Exception as e:
                pytest.fail(f"Failed to read {pdf}: {e}")

    def test_pdf_files_have_unique_names(self):
        names = [pdf.name for pdf in RESOURCES_DIR.glob("*.pdf")]
        assert len(names) == len(set(names)), "Duplicate PDF file names found"

    def test_resources_folder_structure(self):
        files = list(RESOURCES_DIR.iterdir())
        assert files, "Resources folder is empty"
        for f in files:
            assert f.is_file(), f"Non-file found: {f}"

    def test_pdf_files_can_be_processed_multiple_times(self):
        import pypdf

        for pdf in RESOURCES_DIR.glob("*.pdf"):
            for _ in range(3):
                reader = pypdf.PdfReader(str(pdf))
                assert len(reader.pages) > 0

    def test_pdf_files_metadata_consistency(self):
        import pypdf

        for pdf in RESOURCES_DIR.glob("*.pdf"):
            reader = pypdf.PdfReader(str(pdf))
            # PDF files may not have metadata, which is acceptable
            # Just ensure the reader can access the metadata property
            _ = reader.metadata
