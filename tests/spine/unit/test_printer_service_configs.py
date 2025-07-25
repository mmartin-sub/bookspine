"""
Unit tests for printer service configuration files.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

import pytest

from src.bookspine.config.config_loader import ConfigLoader, ConfigurationError


class TestPrinterServiceConfigs(unittest.TestCase):
    """Test cases for printer service configuration files."""

    def setUp(self):
        """Set up test fixtures."""
        self.config_loader = ConfigLoader()
        self.config_dir = self.config_loader.config_dir

    def test_default_config_exists_and_valid(self):
        """Test that default.json exists and is valid."""
        config_file = os.path.join(self.config_dir, "default.json")
        self.assertTrue(os.path.exists(config_file), "default.json should exist")

        # Test loading and validation
        config = self.config_loader.load_printer_service_config("default")
        self.assertEqual(config["name"], "default")
        self.assertIn("description", config)
        self.assertIn("paper_bulk", config)
        self.assertIn("cover_thickness", config)

    def test_lulu_config_exists_and_valid(self):
        """Test that lulu.json exists and is valid."""
        config_file = os.path.join(self.config_dir, "lulu.json")
        self.assertTrue(os.path.exists(config_file), "lulu.json should exist")

        # Test loading and validation
        config = self.config_loader.load_printer_service_config("lulu")
        self.assertEqual(config["name"], "lulu")
        self.assertIn("description", config)
        self.assertIn("paper_bulk", config)
        self.assertIn("cover_thickness", config)
        self.assertIn("formulas", config)

    def test_kdp_config_exists_and_valid(self):
        """Test that kdp.json exists and is valid."""
        config_file = os.path.join(self.config_dir, "kdp.json")
        self.assertTrue(os.path.exists(config_file), "kdp.json should exist")

        # Test loading and validation
        config = self.config_loader.load_printer_service_config("kdp")
        self.assertEqual(config["name"], "kdp")
        self.assertIn("description", config)
        self.assertIn("paper_bulk", config)
        self.assertIn("cover_thickness", config)
        self.assertIn("formulas", config)

    def test_all_configs_have_required_paper_types(self):
        """Test that all configurations have required paper types."""
        required_paper_types = ["MCG", "MCS", "ECB", "OFF"]
        services = self.config_loader.list_available_services()

        for service_name in services:
            config = self.config_loader.load_printer_service_config(service_name)
            paper_bulk = config["paper_bulk"]

            for paper_type in required_paper_types:
                self.assertIn(paper_type, paper_bulk, f"Service '{service_name}' missing paper type '{paper_type}'")
                self.assertIsInstance(
                    paper_bulk[paper_type],
                    (int, float),
                    f"Paper bulk for '{paper_type}' in '{service_name}' must be numeric",
                )
                self.assertGreater(
                    paper_bulk[paper_type], 0, f"Paper bulk for '{paper_type}' in '{service_name}' must be positive"
                )

    def test_all_configs_have_valid_cover_thickness(self):
        """Test that all configurations have valid cover thickness values."""
        services = self.config_loader.list_available_services()

        for service_name in services:
            config = self.config_loader.load_printer_service_config(service_name)
            cover_thickness = config["cover_thickness"]

            self.assertIsInstance(cover_thickness, dict, f"Cover thickness in '{service_name}' must be a dictionary")

            for binding_type, thickness in cover_thickness.items():
                self.assertIsInstance(
                    thickness, (int, float), f"Cover thickness for '{binding_type}' in '{service_name}' must be numeric"
                )
                self.assertGreaterEqual(
                    thickness, 0, f"Cover thickness for '{binding_type}' in '{service_name}' must be non-negative"
                )

    def test_config_files_are_valid_json(self):
        """Test that all configuration files contain valid JSON."""
        config_files = [f for f in os.listdir(self.config_dir) if f.endswith(".json")]

        for config_file in config_files:
            file_path = os.path.join(self.config_dir, config_file)

            with self.subTest(config_file=config_file):
                try:
                    with open(file_path, encoding="utf-8") as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON in {config_file}: {e}")

    def test_lulu_specific_configuration(self):
        """Test Lulu-specific configuration details."""
        config = self.config_loader.load_printer_service_config("lulu")

        # Check that Lulu has the expected formula configuration
        self.assertIn("formulas", config)
        formulas = config["formulas"]

        # Check Softcover Perfect Bound formula
        self.assertIn("Softcover Perfect Bound", formulas)
        softcover_formula = formulas["Softcover Perfect Bound"]
        self.assertEqual(softcover_formula["type"], "pages_per_inch")
        self.assertIn("params", softcover_formula)
        self.assertIn("pages_per_inch", softcover_formula["params"])
        self.assertIn("base_thickness", softcover_formula["params"])

    def test_kdp_specific_configuration(self):
        """Test KDP-specific configuration details."""
        config = self.config_loader.load_printer_service_config("kdp")

        # Check that KDP has the expected formula configuration
        self.assertIn("formulas", config)
        formulas = config["formulas"]

        # Check Softcover Perfect Bound formula (different from Lulu)
        self.assertIn("Softcover Perfect Bound", formulas)
        softcover_formula = formulas["Softcover Perfect Bound"]
        self.assertEqual(softcover_formula["type"], "pages_per_inch")
        self.assertEqual(softcover_formula["params"]["pages_per_inch"], 460)

        # Check Hardcover Casewrap formula with ranges
        self.assertIn("Hardcover Casewrap", formulas)
        hardcover_formula = formulas["Hardcover Casewrap"]
        self.assertEqual(hardcover_formula["type"], "fixed_ranges")
        self.assertIn("ranges", hardcover_formula["params"])

        ranges = hardcover_formula["params"]["ranges"]
        self.assertIsInstance(ranges, list)
        self.assertGreater(len(ranges), 0)

        # Validate range structure
        for range_item in ranges:
            self.assertIn("min_pages", range_item)
            self.assertIn("max_pages", range_item)
            self.assertIn("width_inches", range_item)

    def test_list_services_includes_all_configs(self):
        """Test that list_available_services includes all configuration files."""
        services = self.config_loader.list_available_services()

        # Should include at least default, lulu, and kdp
        expected_services = ["default", "lulu", "kdp"]
        for expected_service in expected_services:
            self.assertIn(
                expected_service, services, f"Service '{expected_service}' should be in available services list"
            )


if __name__ == "__main__":
    unittest.main()
