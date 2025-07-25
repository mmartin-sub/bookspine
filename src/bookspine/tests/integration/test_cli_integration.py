"""
CLI integration tests for the BookSpine Calculator.

These tests verify the command-line interface works correctly with
various argument combinations, error handling, and output formats.
"""

import csv
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from src.bookspine.cli import main, parse_args, validate_cli_arguments, validate_required_arguments


class TestCLIArgumentParsing:
    """Test CLI argument parsing functionality."""

    def test_basic_argument_parsing(self):
        """Test basic argument parsing."""
        test_args = [
            "--page-count",
            "200",
            "--paper-type",
            "MCG",
            "--binding-type",
            "Softcover Perfect Bound",
            "--paper-weight",
            "80",
        ]

        with patch.object(sys, "argv", ["bookspine"] + test_args):
            args = parse_args()

            assert args.page_count == 200
            assert args.paper_type == "MCG"
            assert args.binding_type == "Softcover Perfect Bound"
            assert args.paper_weight == 80
            assert args.format == "text"
            assert args.dpi == 300

    def test_pdf_argument_parsing(self):
        """Test PDF argument parsing."""
        test_args = [
            "--pdf",
            "test.pdf",
            "--paper-type",
            "MCG",
            "--binding-type",
            "Softcover Perfect Bound",
            "--paper-weight",
            "80",
        ]

        with patch.object(sys, "argv", ["bookspine"] + test_args):
            args = parse_args()

            assert args.pdf == "test.pdf"
            assert args.paper_type == "MCG"
            assert args.binding_type == "Softcover Perfect Bound"
            assert args.paper_weight == 80

    def test_printer_service_argument_parsing(self):
        """Test printer service argument parsing."""
        test_args = ["--page-count", "150", "--printer-service", "kdp", "--binding-type", "Softcover Perfect Bound"]

        with patch.object(sys, "argv", ["bookspine"] + test_args):
            args = parse_args()

            assert args.page_count == 150
            assert args.printer_service == "kdp"
            assert args.binding_type == "Softcover Perfect Bound"

    def test_output_format_argument_parsing(self):
        """Test output format argument parsing."""
        for format_type in ["text", "json", "csv"]:
            test_args = [
                "--page-count",
                "200",
                "--paper-type",
                "MCG",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
                "--output-format",
                format_type,
            ]

            with patch.object(sys, "argv", ["bookspine"] + test_args):
                args = parse_args()
                assert args.format == format_type

    def test_manual_override_argument_parsing(self):
        """Test manual override argument parsing."""
        test_args = [
            "--page-count",
            "300",
            "--paper-type",
            "MCG",
            "--binding-type",
            "Softcover Perfect Bound",
            "--paper-weight",
            "80",
            "--manual-override",
            "12.5",
        ]

        with patch.object(sys, "argv", ["bookspine"] + test_args):
            args = parse_args()

            assert args.page_count == 300
            assert args.manual_override == 12.5

    def test_dpi_argument_parsing(self):
        """Test DPI argument parsing."""
        test_args = [
            "--page-count",
            "200",
            "--paper-type",
            "MCG",
            "--binding-type",
            "Softcover Perfect Bound",
            "--paper-weight",
            "80",
            "--dpi",
            "600",
        ]

        with patch.object(sys, "argv", ["bookspine"] + test_args):
            args = parse_args()
            assert args.dpi == 600


class TestCLIValidation:
    """Test CLI validation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        from src.bookspine.config.config_loader import ConfigLoader

        self.config_loader = ConfigLoader()

    def test_validate_required_arguments_success(self):
        """Test successful validation of required arguments."""
        # Mock args object
        args = MagicMock()
        args.pdf = None
        args.page_count = 200
        args.paper_type = "MCG"
        args.binding_type = "Softcover Perfect Bound"

        error = validate_required_arguments(args)
        assert error is None

    def test_validate_required_arguments_missing_input(self):
        """Test validation failure when no input is provided."""
        args = MagicMock()
        args.pdf = None
        args.page_count = None
        args.paper_type = "MCG"
        args.binding_type = "Softcover Perfect Bound"

        error = validate_required_arguments(args)
        assert error is not None
        assert "Missing required argument: page count" in error

    def test_validate_required_arguments_conflicting_input(self):
        """Test validation failure when both PDF and page count are provided."""
        args = MagicMock()
        args.pdf = "test.pdf"
        args.page_count = 200
        args.paper_type = "MCG"
        args.binding_type = "Softcover Perfect Bound"

        error = validate_required_arguments(args)
        assert error is not None
        assert "Conflicting inputs" in error

    def test_validate_required_arguments_missing_specs(self):
        """Test validation failure when required specifications are missing."""
        args = MagicMock()
        args.pdf = None
        args.page_count = 200
        args.paper_type = None
        args.binding_type = None
        args.printer_service = None  # Explicitly set to None

        error = validate_required_arguments(args)
        assert error is not None
        assert "Missing required argument: paper type" in error

    def test_validate_cli_arguments_success(self):
        """Test successful validation of CLI arguments."""
        args = MagicMock()
        args.pdf = None
        args.page_count = 200
        args.paper_type = "MCG"
        args.binding_type = "Softcover Perfect Bound"
        args.paper_weight = 80
        args.printer_service = None
        args.format = "text"

        error = validate_cli_arguments(args, self.config_loader)
        assert error is None

    def test_validate_cli_arguments_invalid_page_count(self):
        """Test validation failure with invalid page count."""
        args = MagicMock()
        args.pdf = None
        args.page_count = 0
        args.paper_type = "MCG"
        args.binding_type = "Softcover Perfect Bound"
        args.paper_weight = 80
        args.printer_service = None
        args.format = "text"

        error = validate_cli_arguments(args, self.config_loader)
        assert error is not None
        assert "Page count must be positive" in error

    def test_validate_cli_arguments_invalid_paper_type(self):
        """Test validation failure with invalid paper type."""
        args = MagicMock()
        args.pdf = None
        args.page_count = 200
        args.paper_type = "INVALID"
        args.binding_type = "Softcover Perfect Bound"
        args.paper_weight = 80
        args.printer_service = None
        args.format = "text"

        error = validate_cli_arguments(args, self.config_loader)
        assert error is not None
        assert "Invalid paper type" in error

    def test_validate_cli_arguments_invalid_binding_type(self):
        """Test validation failure with invalid binding type."""
        args = MagicMock()
        args.pdf = None
        args.page_count = 200
        args.paper_type = "MCG"
        args.binding_type = "INVALID"
        args.paper_weight = 80
        args.printer_service = None
        args.format = "text"

        error = validate_cli_arguments(args, self.config_loader)
        assert error is not None
        assert "Invalid binding type" in error

    def test_validate_cli_arguments_invalid_dpi(self):
        """Test validation failure with invalid DPI."""
        args = MagicMock()
        args.pdf = None
        args.page_count = 200
        args.paper_type = "MCG"
        args.binding_type = "Softcover Perfect Bound"
        args.paper_weight = 80
        args.printer_service = None
        args.dpi = 0
        args.manual_override = None
        args.format = "text"

        error = validate_cli_arguments(args, self.config_loader)
        assert error is not None
        assert "DPI must be positive" in error


class TestCLIExecution:
    """Test CLI execution with various scenarios."""

    def test_cli_basic_execution(self):
        """Test basic CLI execution."""
        # Test with basic arguments
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.bookspine.cli",
                "--page-count",
                "200",
                "--paper-type",
                "MCG",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
            ],
            capture_output=True,
            text=True,
        )

        # Should exit successfully
        assert result.returncode == 0
        assert "Spine Width" in result.stdout or "width_mm" in result.stdout

    def test_cli_json_output(self):
        """Test CLI execution with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.bookspine.cli",
                "--page-count",
                "200",
                "--paper-type",
                "MCG",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        # Parse JSON output
        try:
            json_data = json.loads(result.stdout)
            assert "width_mm" in json_data
            assert "width_inches" in json_data
            assert "width_pixels" in json_data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")

    def test_cli_csv_output(self):
        """Test CLI execution with CSV output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.bookspine.cli",
                "--page-count",
                "200",
                "--paper-type",
                "MCG",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
                "--format",
                "csv",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "," in result.stdout  # Should contain CSV format

    def test_cli_file_output(self):
        """Test CLI execution with file output."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
            output_file = tmp_file.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.bookspine.cli",
                    "--page-count",
                    "200",
                    "--paper-type",
                    "MCG",
                    "--binding-type",
                    "Softcover Perfect Bound",
                    "--paper-weight",
                    "80",
                    "--output-format",
                    "json",
                    "--output-file",
                    output_file,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

            # Check that file was created and contains valid JSON
            assert os.path.exists(output_file)
            with open(output_file) as f:
                json_data = json.load(f)
                assert "width_mm" in json_data

        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_cli_manual_override(self):
        """Test CLI execution with manual override."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.bookspine.cli",
                "--page-count",
                "200",
                "--paper-type",
                "MCG",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
                "--manual-override",
                "12.5",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "12.5" in result.stdout or "12.50" in result.stdout

    def test_cli_printer_service(self):
        """Test CLI execution with printer service."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.bookspine.cli",
                "--page-count",
                "200",
                "--printer-service",
                "default",
                "--paper-type",
                "MCG",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_cli_list_services(self):
        """Test CLI list services functionality."""
        result = subprocess.run(
            [sys.executable, "-m", "src.bookspine.cli", "--list-services"], capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "Available printer services" in result.stdout

    def test_cli_help(self):
        """Test CLI help functionality."""
        result = subprocess.run([sys.executable, "-m", "src.bookspine.cli", "--help"], capture_output=True, text=True)

        assert result.returncode == 0
        assert "Calculate book spine dimensions" in result.stdout


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_cli_missing_required_arguments(self):
        """Test CLI error handling with missing required arguments."""
        result = subprocess.run(
            [sys.executable, "-m", "src.bookspine.cli", "--page-count", "200"], capture_output=True, text=True
        )

        assert result.returncode == 1
        assert "Missing required argument: paper type" in result.stderr

    def test_cli_invalid_page_count(self):
        """Test CLI error handling with invalid page count."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.bookspine.cli",
                "--page-count",
                "0",
                "--paper-type",
                "MCG",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "Page count must be positive" in result.stderr

    def test_cli_invalid_paper_type(self):
        """Test CLI error handling with invalid paper type."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.bookspine.cli",
                "--page-count",
                "200",
                "--paper-type",
                "INVALID",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 2  # argparse validation error
        assert "invalid choice" in result.stderr

    def test_cli_invalid_binding_type(self):
        """Test CLI error handling with invalid binding type."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.bookspine.cli",
                "--page-count",
                "200",
                "--paper-type",
                "MCG",
                "--binding-type",
                "INVALID",
                "--paper-weight",
                "80",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 2  # argparse validation error
        assert "invalid choice" in result.stderr

    def test_cli_invalid_dpi(self):
        """Test CLI error handling with invalid DPI."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.bookspine.cli",
                "--page-count",
                "200",
                "--paper-type",
                "MCG",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
                "--dpi",
                "0",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "DPI must be positive" in result.stderr

    def test_cli_invalid_output_format(self):
        """Test CLI error handling with invalid output format."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.bookspine.cli",
                "--page-count",
                "200",
                "--paper-type",
                "MCG",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
                "--output-format",
                "INVALID",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 2
        assert "invalid choice" in result.stderr.lower()


class TestCLIExitCodes:
    """Test CLI exit codes."""

    def test_cli_success_exit_code(self):
        """Test CLI success exit code."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.bookspine.cli",
                "--page-count",
                "200",
                "--paper-type",
                "MCG",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_cli_error_exit_code(self):
        """Test CLI error exit code."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.bookspine.cli",
                "--page-count",
                "0",
                "--paper-type",
                "MCG",
                "--binding-type",
                "Softcover Perfect Bound",
                "--paper-weight",
                "80",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1

    def test_cli_help_exit_code(self):
        """Test CLI help exit code."""
        result = subprocess.run([sys.executable, "-m", "src.bookspine.cli", "--help"], capture_output=True, text=True)

        assert result.returncode == 0

    def test_cli_list_services_exit_code(self):
        """Test CLI list services exit code."""
        result = subprocess.run(
            [sys.executable, "-m", "src.bookspine.cli", "--list-services"], capture_output=True, text=True
        )

        assert result.returncode == 0
