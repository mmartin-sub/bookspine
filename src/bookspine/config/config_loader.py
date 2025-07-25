"""
Configuration loading logic for printer service configurations.

This module provides functionality for loading and validating printer service
configurations from JSON files. It supports loading configurations for different
printer services and provides validation to ensure configuration files are
properly formatted.
"""

import json
import os
from typing import Any, Dict, List, Optional


class ConfigurationError(Exception):
    """
    Exception raised when configuration loading or validation fails.

    This exception is raised when there are errors in loading configuration
    files, invalid JSON format, missing required fields, or other configuration
    related issues.
    """

    pass


class ConfigLoader:
    """
    Loader for printer service configurations.

    This class provides methods to load and validate printer service configurations
    from JSON files. It supports loading configurations for different printer
    services and provides validation to ensure configuration files are properly
    formatted.

    Attributes:
        config_dir: Directory containing printer service configuration files.
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration loader.

        Args:
            config_dir: Directory containing printer service configurations.
                If None, uses the default configuration directory within the
                package.

        Raises:
            ConfigurationError: If the configuration directory does not exist.
        """
        self.config_dir = config_dir or self._get_default_config_dir()
        if not os.path.exists(self.config_dir):
            raise ConfigurationError(f"Configuration directory does not exist: {self.config_dir}")

    def _get_default_config_dir(self) -> str:
        """
        Get the default configuration directory.

        Returns:
            str: Path to the default configuration directory within the package.
        """
        # Use the printer_services directory in the package
        return os.path.join(os.path.dirname(__file__), "printer_services")

    def load_printer_service_config(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Load printer service configuration.

        This method loads a printer service configuration from a JSON file and
        validates its format. The configuration contains paper bulk factors,
        cover thickness values, and formula definitions for different binding types.

        Args:
            service_name: Name of printer service to load. If None, loads the
                "default" service configuration.

        Returns:
            dict: Printer service configuration containing paper bulk factors,
                cover thickness values, and formula definitions.

        Raises:
            ConfigurationError: If the configuration file is not found, contains
                invalid JSON, or fails validation.
        """
        if service_name is None:
            service_name = "default"

        config_file = os.path.join(self.config_dir, f"{service_name}.json")

        if not os.path.exists(config_file):
            raise ConfigurationError(f"Configuration file not found: {config_file}")

        try:
            with open(config_file, encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file {config_file}: {e}")
        except OSError as e:
            raise ConfigurationError(f"Error reading configuration file {config_file}: {e}")

        # Validate the configuration
        self._validate_config(config, service_name)

        return config  # type: ignore[no-any-return]

    def _validate_config(self, config: Dict, service_name: str) -> None:
        """
        Validate printer service configuration format.

        This method validates that a configuration dictionary contains all required
        fields and that the values are in the expected format.

        Args:
            config: Configuration dictionary to validate.
            service_name: Name of the service being validated.

        Raises:
            ConfigurationError: If the configuration is missing required fields
                or contains invalid values.
        """
        required_fields = ["name", "description", "paper_bulk", "cover_thickness"]

        for field in required_fields:
            if field not in config:
                raise ConfigurationError(
                    f"Missing required field '{field}' in configuration for service '{service_name}'"
                )

        # Validate paper_bulk section
        if not isinstance(config["paper_bulk"], dict):
            raise ConfigurationError(f"'paper_bulk' must be a dictionary in configuration for service '{service_name}'")

        required_paper_types = ["MCG", "MCS", "ECB", "OFF"]
        for paper_type in required_paper_types:
            if paper_type not in config["paper_bulk"]:
                raise ConfigurationError(
                    f"Missing paper type '{paper_type}' in paper_bulk for service '{service_name}'"
                )

            bulk_value = config["paper_bulk"][paper_type]
            if not isinstance(bulk_value, (int, float)) or bulk_value <= 0:
                raise ConfigurationError(
                    f"Paper bulk value for '{paper_type}' must be a positive number in service '{service_name}'"
                )

        # Validate cover_thickness section
        if not isinstance(config["cover_thickness"], dict):
            raise ConfigurationError(
                f"'cover_thickness' must be a dictionary in configuration for service '{service_name}'"
            )

        required_binding_types = ["Softcover Perfect Bound", "Hardcover Casewrap", "Hardcover Linen"]
        for binding_type in required_binding_types:
            if binding_type not in config["cover_thickness"]:
                raise ConfigurationError(
                    f"Missing binding type '{binding_type}' in cover_thickness for service '{service_name}'"
                )

            thickness_value = config["cover_thickness"][binding_type]
            if not isinstance(thickness_value, (int, float)) or thickness_value < 0:
                raise ConfigurationError(
                    f"Cover thickness value for '{binding_type}' must be a non-negative "
                    f"number in service '{service_name}'"
                )

        # Validate formulas section (optional but if present, must be valid)
        if "formulas" in config:
            if not isinstance(config["formulas"], dict):
                raise ConfigurationError(
                    f"'formulas' must be a dictionary in configuration for service '{service_name}'"
                )

            for binding_type, formula_config in config["formulas"].items():
                if not isinstance(formula_config, dict):
                    raise ConfigurationError(
                        f"Formula configuration for '{binding_type}' must be a dictionary in service '{service_name}'"
                    )

                if "type" not in formula_config:
                    raise ConfigurationError(
                        f"Formula configuration for '{binding_type}' missing 'type' field in service '{service_name}'"
                    )

                if "params" not in formula_config:
                    raise ConfigurationError(
                        f"Formula configuration for '{binding_type}' missing 'params' field in service '{service_name}'"
                    )

                formula_type = formula_config["type"]
                if formula_type not in ["general", "pages_per_inch", "fixed_ranges"]:
                    raise ConfigurationError(
                        f"Unknown formula type '{formula_type}' for binding type "
                        f"'{binding_type}' in service '{service_name}'"
                    )

    def validate_service(self, service_name: str) -> None:
        """
        Validate that a printer service exists and has valid configuration.

        This method checks if a printer service configuration exists and validates
        that it contains all required fields and proper data types.

        Args:
            service_name: Name of the printer service to validate.

        Raises:
            ConfigurationError: If the service doesn't exist or has invalid configuration.
        """
        try:
            config = self.load_printer_service_config(service_name)
            self._validate_config(config, service_name)
        except ConfigurationError:
            # Re-raise with more specific error message
            raise ConfigurationError(f"Invalid printer service: {service_name}")

    def list_available_services(self) -> List[str]:
        """
        List all available printer services.

        This method scans the configuration directory and returns a list of all
        available printer service names based on the JSON files present.

        Returns:
            list: List of available printer service names (without .json extension).

        Raises:
            ConfigurationError: If the configuration directory cannot be accessed.
        """
        try:
            services = []
            for filename in os.listdir(self.config_dir):
                if filename.endswith(".json"):
                    service_name = filename[:-5]  # Remove .json extension
                    services.append(service_name)
            return sorted(services)
        except OSError as e:
            raise ConfigurationError(f"Error accessing configuration directory {self.config_dir}: {e}")
