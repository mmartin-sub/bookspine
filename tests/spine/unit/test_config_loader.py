"""
Unit tests for ConfigLoader class.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

from src.bookspine.config.config_loader import ConfigLoader, ConfigurationError


class TestConfigLoader(unittest.TestCase):
    """Test cases for ConfigLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Create a valid test configuration
        self.valid_config = {
            "name": "test_service",
            "description": "Test printer service",
            "paper_bulk": {"MCG": 0.80, "MCS": 0.90, "ECB": 1.20, "OFF": 1.22},
            "cover_thickness": {"Softcover Perfect Bound": 0.5, "Hardcover Casewrap": 2.0, "Hardcover Linen": 3.0},
            "formulas": {"Softcover Perfect Bound": {"type": "general", "params": {}}},
        }

        # Write valid config to temp directory
        with open(os.path.join(self.temp_dir, "test_service.json"), "w") as f:
            json.dump(self.valid_config, f)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_init_with_custom_config_dir(self):
        """Test ConfigLoader initialization with custom config directory."""
        loader = ConfigLoader(config_dir=self.temp_dir)
        self.assertEqual(loader.config_dir, self.temp_dir)

    def test_init_with_nonexistent_config_dir(self):
        """Test ConfigLoader initialization with nonexistent config directory."""
        with self.assertRaises(ConfigurationError) as context:
            ConfigLoader(config_dir="/nonexistent/path")

        self.assertIn("Configuration directory does not exist", str(context.exception))

    def test_load_printer_service_config_success(self):
        """Test successful loading of printer service configuration."""
        loader = ConfigLoader(config_dir=self.temp_dir)
        config = loader.load_printer_service_config("test_service")

        self.assertEqual(config["name"], "test_service")
        self.assertEqual(config["description"], "Test printer service")
        self.assertIn("paper_bulk", config)
        self.assertIn("cover_thickness", config)

    def test_load_printer_service_config_default(self):
        """Test loading default printer service configuration."""
        # Create default.json in temp directory
        with open(os.path.join(self.temp_dir, "default.json"), "w") as f:
            default_config = self.valid_config.copy()
            default_config["name"] = "default"
            json.dump(default_config, f)

        loader = ConfigLoader(config_dir=self.temp_dir)
        config = loader.load_printer_service_config()  # No service name provided

        self.assertEqual(config["name"], "default")

    def test_load_printer_service_config_file_not_found(self):
        """Test loading nonexistent printer service configuration."""
        loader = ConfigLoader(config_dir=self.temp_dir)

        with self.assertRaises(ConfigurationError) as context:
            loader.load_printer_service_config("nonexistent")

        self.assertIn("Configuration file not found", str(context.exception))

    def test_load_printer_service_config_invalid_json(self):
        """Test loading printer service configuration with invalid JSON."""
        # Create invalid JSON file
        invalid_json_file = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_json_file, "w") as f:
            f.write("{ invalid json }")

        loader = ConfigLoader(config_dir=self.temp_dir)

        with self.assertRaises(ConfigurationError) as context:
            loader.load_printer_service_config("invalid")

        self.assertIn("Invalid JSON", str(context.exception))

    def test_validate_config_missing_required_field(self):
        """Test configuration validation with missing required field."""
        loader = ConfigLoader(config_dir=self.temp_dir)

        # Create config missing required field
        invalid_config = self.valid_config.copy()
        del invalid_config["paper_bulk"]

        with self.assertRaises(ConfigurationError) as context:
            loader._validate_config(invalid_config, "test")

        self.assertIn("Missing required field 'paper_bulk'", str(context.exception))

    def test_validate_config_invalid_paper_bulk_type(self):
        """Test configuration validation with invalid paper_bulk type."""
        loader = ConfigLoader(config_dir=self.temp_dir)

        # Create config with invalid paper_bulk type
        invalid_config = self.valid_config.copy()
        invalid_config["paper_bulk"] = "not a dict"

        with self.assertRaises(ConfigurationError) as context:
            loader._validate_config(invalid_config, "test")

        self.assertIn("'paper_bulk' must be a dictionary", str(context.exception))

    def test_validate_config_missing_paper_type(self):
        """Test configuration validation with missing paper type."""
        loader = ConfigLoader(config_dir=self.temp_dir)

        # Create config missing paper type
        invalid_config = self.valid_config.copy()
        del invalid_config["paper_bulk"]["MCG"]

        with self.assertRaises(ConfigurationError) as context:
            loader._validate_config(invalid_config, "test")

        self.assertIn("Missing paper type 'MCG'", str(context.exception))

    def test_validate_config_invalid_paper_bulk_value(self):
        """Test configuration validation with invalid paper bulk value."""
        loader = ConfigLoader(config_dir=self.temp_dir)

        # Create config with invalid paper bulk value
        invalid_config = self.valid_config.copy()
        invalid_config["paper_bulk"]["MCG"] = -0.5

        with self.assertRaises(ConfigurationError) as context:
            loader._validate_config(invalid_config, "test")

        self.assertIn("Paper bulk value for 'MCG' must be a positive number", str(context.exception))

    def test_validate_config_invalid_cover_thickness_type(self):
        """Test configuration validation with invalid cover_thickness type."""
        loader = ConfigLoader(config_dir=self.temp_dir)

        # Create config with invalid cover_thickness type
        invalid_config = self.valid_config.copy()
        invalid_config["cover_thickness"] = "not a dict"

        with self.assertRaises(ConfigurationError) as context:
            loader._validate_config(invalid_config, "test")

        self.assertIn("'cover_thickness' must be a dictionary", str(context.exception))

    def test_validate_config_invalid_cover_thickness_value(self):
        """Test configuration validation with invalid cover thickness value."""
        loader = ConfigLoader(config_dir=self.temp_dir)

        # Create config with invalid cover thickness value
        invalid_config = self.valid_config.copy()
        invalid_config["cover_thickness"]["Softcover Perfect Bound"] = -1.0

        with self.assertRaises(ConfigurationError) as context:
            loader._validate_config(invalid_config, "test")

        self.assertIn(
            "Cover thickness value for 'Softcover Perfect Bound' must be a non-negative number", str(context.exception)
        )

    def test_validate_config_invalid_formulas_type(self):
        """Test configuration validation with invalid formulas type."""
        loader = ConfigLoader(config_dir=self.temp_dir)

        # Create config with invalid formulas type
        invalid_config = self.valid_config.copy()
        invalid_config["formulas"] = "not a dict"

        with self.assertRaises(ConfigurationError) as context:
            loader._validate_config(invalid_config, "test")

        self.assertIn("'formulas' must be a dictionary", str(context.exception))

    def test_validate_config_missing_formula_type(self):
        """Test configuration validation with missing formula type."""
        loader = ConfigLoader(config_dir=self.temp_dir)

        # Create config with missing formula type
        invalid_config = self.valid_config.copy()
        invalid_config["formulas"]["Softcover Perfect Bound"] = {"params": {}}

        with self.assertRaises(ConfigurationError) as context:
            loader._validate_config(invalid_config, "test")

        self.assertIn(
            "Formula configuration for 'Softcover Perfect Bound' missing 'type' field", str(context.exception)
        )

    def test_validate_config_missing_formula_params(self):
        """Test configuration validation with missing formula params."""
        loader = ConfigLoader(config_dir=self.temp_dir)

        # Create config with missing formula params
        invalid_config = self.valid_config.copy()
        invalid_config["formulas"]["Softcover Perfect Bound"] = {"type": "general"}

        with self.assertRaises(ConfigurationError) as context:
            loader._validate_config(invalid_config, "test")

        self.assertIn(
            "Formula configuration for 'Softcover Perfect Bound' missing 'params' field", str(context.exception)
        )

    def test_list_available_services(self):
        """Test listing available printer services."""
        # Create additional service files
        service_names = ["service_a", "service_b", "service_c"]
        for name in service_names:
            config = self.valid_config.copy()
            config["name"] = name
            with open(os.path.join(self.temp_dir, f"{name}.json"), "w") as f:
                json.dump(config, f)

        loader = ConfigLoader(config_dir=self.temp_dir)
        services = loader.list_available_services()

        # Should include test_service from setUp and the new services
        expected_services = sorted(["test_service"] + service_names)
        self.assertEqual(services, expected_services)

    def test_list_available_services_empty_directory(self):
        """Test listing available services in empty directory."""
        empty_dir = tempfile.mkdtemp()
        try:
            loader = ConfigLoader(config_dir=empty_dir)
            services = loader.list_available_services()
            self.assertEqual(services, [])
        finally:
            import shutil

            shutil.rmtree(empty_dir)

    def test_list_available_services_io_error(self):
        """Test listing available services with IO error."""
        loader = ConfigLoader(config_dir=self.temp_dir)

        with self.assertRaises(ConfigurationError) as context:
            with patch("os.listdir", side_effect=OSError("Permission denied")):
                loader.list_available_services()

        self.assertIn("Error accessing configuration directory", str(context.exception))


if __name__ == "__main__":
    unittest.main()
