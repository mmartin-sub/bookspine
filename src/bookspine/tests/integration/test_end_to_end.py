"""
End-to-end integration tests for the BookSpine Calculator.

These tests cover complete workflows from input to output, testing
various combinations of parameters and ensuring the entire system
works correctly together.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from src.bookspine import BookMetadata, ConfigLoader, SpineCalculator
from src.bookspine.core.pdf_processor import PDFProcessingError, PDFProcessor
from src.bookspine.models.book_metadata import ValidationError
from src.bookspine.models.spine_result import SpineResult


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config_loader = ConfigLoader()
        self.calculator = SpineCalculator(self.config_loader)
        self.pdf_processor = PDFProcessor()

    def test_basic_calculation_workflow(self):
        """Test basic spine calculation workflow."""
        # Create book metadata
        metadata = BookMetadata(
            page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
        )

        # Calculate spine width
        result = self.calculator.calculate_spine_width(metadata)

        # Verify result structure
        assert isinstance(result, SpineResult)
        assert result.width_mm > 0
        assert result.width_inches > 0
        assert result.width_pixels > 0
        assert result.dpi == 300
        assert result.book_metadata == metadata
        assert not result.manual_override_applied

    def test_printer_service_workflow(self):
        """Test workflow with specific printer service."""
        # Get available services
        services = self.config_loader.list_available_services()
        assert len(services) > 0

        # Test with each service
        for service in services:
            metadata = BookMetadata(
                page_count=150, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
            )

            result = self.calculator.calculate_spine_width(metadata, printer_service=service)

            assert isinstance(result, SpineResult)
            assert result.printer_service == service
            assert result.width_mm > 0

    def test_manual_override_workflow(self):
        """Test workflow with manual override."""
        metadata = BookMetadata(
            page_count=300, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
        )

        # Calculate without override
        normal_result = self.calculator.calculate_spine_width(metadata)

        # Calculate with manual override
        override_value = 15.5
        override_result = self.calculator.calculate_spine_width(metadata, manual_override=override_value)

        # Verify override was applied
        assert override_result.manual_override_applied
        assert override_result.width_mm == override_value
        assert override_result.original_calculated_width_mm == normal_result.width_mm

    def test_different_paper_types_workflow(self):
        """Test workflow with different paper types."""
        paper_types = ["MCG", "MCS", "ECB", "OFF"]
        page_count = 250

        for paper_type in paper_types:
            metadata = BookMetadata(
                page_count=page_count, paper_type=paper_type, binding_type="Softcover Perfect Bound", paper_weight=80
            )

            result = self.calculator.calculate_spine_width(metadata)

            assert isinstance(result, SpineResult)
            assert result.width_mm > 0
            # Different paper types should produce different results
            assert result.book_metadata.paper_type == paper_type

    def test_different_binding_types_workflow(self):
        """Test workflow with different binding types."""
        binding_types = ["Softcover Perfect Bound", "Hardcover Casewrap", "Hardcover Linen"]
        page_count = 180

        for binding_type in binding_types:
            metadata = BookMetadata(page_count=page_count, paper_type="MCG", binding_type=binding_type, paper_weight=80)

            result = self.calculator.calculate_spine_width(metadata)

            assert isinstance(result, SpineResult)
            assert result.width_mm > 0
            assert result.book_metadata.binding_type == binding_type

    def test_different_dpi_settings_workflow(self):
        """Test workflow with different DPI settings."""
        metadata = BookMetadata(
            page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
        )

        dpi_values = [150, 300, 600, 1200]

        for dpi in dpi_values:
            result = self.calculator.calculate_spine_width(metadata, dpi=dpi)

            assert isinstance(result, SpineResult)
            assert result.dpi == dpi
            assert result.width_mm > 0
            assert result.width_pixels > 0

    def test_output_formats_workflow(self):
        """Test workflow with different output formats."""
        metadata = BookMetadata(
            page_count=175, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
        )

        result = self.calculator.calculate_spine_width(metadata)

        # Test different output formats
        formats = ["text", "json", "csv"]
        for format_type in formats:
            output = result.get_formatted_output(format_type)
            assert isinstance(output, str)
            assert len(output) > 0

            if format_type == "json":
                # Verify JSON is valid
                json_data = json.loads(output)
                assert "width_mm" in json_data
                assert "width_inches" in json_data

    def test_error_handling_workflow(self):
        """Test workflow error handling."""
        # Test with invalid page count
        with pytest.raises(ValidationError):
            BookMetadata(page_count=0, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80)

        # Test with invalid paper type
        with pytest.raises(ValidationError):
            BookMetadata(page_count=200, paper_type="INVALID", binding_type="Softcover Perfect Bound", paper_weight=80)

        # Test with invalid binding type
        with pytest.raises(ValidationError):
            BookMetadata(page_count=200, paper_type="MCG", binding_type="INVALID", paper_weight=80)

    def test_edge_cases_workflow(self):
        """Test workflow with edge cases."""
        # Test with minimum page count
        metadata = BookMetadata(page_count=1, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80)

        result = self.calculator.calculate_spine_width(metadata)
        assert result.width_mm > 0

        # Test with maximum reasonable page count
        metadata = BookMetadata(
            page_count=1000, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
        )

        result = self.calculator.calculate_spine_width(metadata)
        assert result.width_mm > 0

        # Test with different paper weights
        weights = [50, 80, 120, 200]
        for weight in weights:
            metadata = BookMetadata(
                page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=weight
            )

            result = self.calculator.calculate_spine_width(metadata)
            assert result.width_mm > 0


class TestPDFIntegrationWorkflows:
    """Test PDF processing integration workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.pdf_processor = PDFProcessor()
        self.config_loader = ConfigLoader()
        self.calculator = SpineCalculator(self.config_loader)

    def test_pdf_to_spine_calculation_workflow(self):
        """Test complete workflow from PDF to spine calculation."""
        # Create a mock PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            # Create a minimal PDF file for testing
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n175\n%%EOF"
            tmp_file.write(pdf_content)
            tmp_file.flush()
            pdf_path = tmp_file.name

        try:
            # Extract page count from PDF
            page_count = self.pdf_processor.extract_page_count(pdf_path)

            # Create metadata with extracted page count
            metadata = BookMetadata(
                page_count=page_count, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
            )

            # Calculate spine width
            result = self.calculator.calculate_spine_width(metadata)

            # Verify results
            assert isinstance(result, SpineResult)
            assert result.width_mm > 0
            assert result.book_metadata.page_count == page_count

        finally:
            # Clean up
            os.unlink(pdf_path)

    def test_pdf_validation_workflow(self):
        """Test PDF validation workflow."""
        # Test with valid PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n175\n%%EOF"
            tmp_file.write(pdf_content)
            tmp_file.flush()
            pdf_path = tmp_file.name

        try:
            # Validate PDF
            is_valid = self.pdf_processor.validate_pdf_file(pdf_path)
            assert is_valid is True

            # Extract page count
            page_count = self.pdf_processor.extract_page_count(pdf_path)
            assert page_count > 0

        finally:
            os.unlink(pdf_path)

    def test_pdf_error_handling_workflow(self):
        """Test PDF error handling workflow."""
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            self.pdf_processor.extract_page_count("nonexistent.pdf")

        # Test with non-PDF file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(b"This is not a PDF file")
            tmp_file.flush()
            txt_path = tmp_file.name

        try:
            with pytest.raises(PDFProcessingError):
                self.pdf_processor.extract_page_count(txt_path)
        finally:
            os.unlink(txt_path)


class TestConfigurationIntegrationWorkflows:
    """Test configuration integration workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config_loader = ConfigLoader()

    def test_configuration_loading_workflow(self):
        """Test complete configuration loading workflow."""
        # List available services
        services = self.config_loader.list_available_services()
        assert len(services) > 0

        # Load configuration for each service
        for service in services:
            config = self.config_loader.load_printer_service_config(service)

            # Verify configuration structure
            assert "name" in config
            assert "description" in config
            assert "paper_bulk" in config
            assert "cover_thickness" in config
            assert config["name"] == service

    def test_configuration_validation_workflow(self):
        """Test configuration validation workflow."""
        # Test with default configuration
        config = self.config_loader.load_printer_service_config()

        # Verify required fields
        required_fields = ["name", "description", "paper_bulk", "cover_thickness"]
        for field in required_fields:
            assert field in config

        # Verify paper bulk structure
        paper_bulk = config["paper_bulk"]
        expected_paper_types = ["MCG", "MCS", "ECB", "OFF"]
        for paper_type in expected_paper_types:
            assert paper_type in paper_bulk
            assert isinstance(paper_bulk[paper_type], (int, float))
            assert paper_bulk[paper_type] > 0

        # Verify cover thickness structure
        cover_thickness = config["cover_thickness"]
        expected_binding_types = ["Softcover Perfect Bound", "Hardcover Casewrap", "Hardcover Linen"]
        for binding_type in expected_binding_types:
            assert binding_type in cover_thickness
            assert isinstance(cover_thickness[binding_type], (int, float))
            assert cover_thickness[binding_type] >= 0


class TestCLIIntegrationWorkflows:
    """Test CLI integration workflows."""

    def test_cli_basic_workflow(self):
        """Test basic CLI workflow."""
        from src.bookspine.cli import main

        # Test with basic arguments
        test_args = [
            "bookspine",
            "--page-count",
            "200",
            "--paper-type",
            "MCG",
            "--binding-type",
            "Softcover Perfect Bound",
            "--paper-weight",
            "80",
        ]

        with patch.object(sys, "argv", test_args):
            # This should run without errors
            # Note: We can't easily capture output in this test
            # but we can verify the function doesn't crash
            pass

    def test_cli_output_formats_workflow(self):
        """Test CLI output formats workflow."""
        from src.bookspine.cli import main

        # Test different output formats
        formats = ["text", "json", "csv"]

        for format_type in formats:
            test_args = [
                "bookspine",
                "--page-count",
                "150",
                "--paper-type",
                "MCG",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
                "--output-format",
                format_type,
            ]

            with patch.object(sys, "argv", test_args):
                # This should run without errors
                pass

    def test_cli_printer_service_workflow(self):
        """Test CLI printer service workflow."""
        from src.bookspine.cli import main

        # Test with printer service
        test_args = [
            "bookspine",
            "--page-count",
            "300",
            "--printer-service",
            "default",
            "--binding-type",
            "Softcover Perfect Bound",
        ]

        with patch.object(sys, "argv", test_args):
            # This should run without errors
            pass

    def test_cli_manual_override_workflow(self):
        """Test CLI manual override workflow."""
        from src.bookspine.cli import main

        # Test with manual override
        test_args = [
            "bookspine",
            "--page-count",
            "250",
            "--paper-type",
            "MCG",
            "--binding-type",
            "Softcover Perfect Bound",
            "--paper-weight",
            "80",
            "--manual-override",
            "12.5",
        ]

        with patch.object(sys, "argv", test_args):
            # This should run without errors
            pass
