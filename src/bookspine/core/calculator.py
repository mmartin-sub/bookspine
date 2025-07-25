"""
Core calculation logic for book spine dimensions.

This module provides the main calculation engine for determining book spine widths
based on various parameters such as page count, paper type, binding type, and
paper weight. It supports multiple calculation formulas and printer service
configurations.
"""

from ..models.spine_result import SpineResult
from .unit_converter import UnitConverter


class CalculationError(Exception):
    """
    Exception raised when spine width calculation fails.

    This exception is raised when there are errors in the calculation process,
    such as invalid input parameters, missing configuration data, or calculation
    errors.
    """

    pass


class SpineCalculator:
    """
    Calculator for book spine dimensions.

    This class provides methods to calculate book spine widths using various
    formulas and printer service configurations. It supports different calculation
    methods including general formulas, pages-per-inch formulas, and fixed range
    formulas.

    Attributes:
        config_loader: The configuration loader instance used to load printer
            service configurations.
    """

    def __init__(self, config_loader):
        """
        Initialize the spine calculator.

        Args:
            config_loader: Configuration loader instance that provides access to
                printer service configurations.

        Raises:
            TypeError: If config_loader is None or invalid.
        """
        if config_loader is None:
            raise TypeError("config_loader cannot be None")
        self.config_loader = config_loader

    def calculate_spine_width(self, book_metadata, printer_service=None, manual_override=None, dpi=300):
        """
        Calculate spine width based on book metadata and printer service config.

        This method performs the main spine width calculation using the provided
        book metadata and optional printer service configuration. It supports
        manual overrides and provides results in multiple units (mm, inches, pixels).

        Args:
            book_metadata: Book metadata object containing page count, paper type,
                binding type, paper weight, and unit system preferences.
            printer_service: Name of printer service to use for calculation
                parameters. If None, uses the default service.
            manual_override: Manual override value in mm. If provided, this value
                will be used instead of the calculated value.
            dpi: DPI (dots per inch) for pixel conversion calculations.
                Default is 300 DPI.

        Returns:
            SpineResult: Calculation result object containing spine width in
                multiple units and calculation metadata.

        Raises:
            CalculationError: If page count is not positive, DPI is not positive,
                manual override is negative, or calculation fails.
            ValidationError: If book metadata validation fails.
            ConfigurationError: If printer service configuration cannot be loaded.
        """
        # Validate inputs
        if book_metadata.page_count <= 0:
            raise CalculationError("Page count must be positive")

        if dpi <= 0:
            raise CalculationError("DPI must be positive")

        # Load printer service configuration
        config = self.config_loader.load_printer_service_config(printer_service)

        # Calculate spine width based on configuration
        calculated_width_mm = self._calculate_width_mm(book_metadata, config)

        # Handle manual override
        if manual_override is not None:
            if manual_override < 0:
                raise CalculationError("Manual override value must be non-negative")
            original_width_mm = calculated_width_mm
            width_mm = manual_override
            manual_override_applied = True
        else:
            width_mm = calculated_width_mm
            original_width_mm = None
            manual_override_applied = False

        # Convert to all units
        width_inches = UnitConverter.mm_to_inches(width_mm)
        width_pixels = UnitConverter.mm_to_pixels(width_mm, dpi)

        return SpineResult(
            width_mm=width_mm,
            width_inches=width_inches,
            width_pixels=width_pixels,
            dpi=dpi,
            book_metadata=book_metadata,
            printer_service=printer_service,
            manual_override_applied=manual_override_applied,
            original_calculated_width_mm=original_width_mm,
        )

    def _calculate_width_mm(self, book_metadata, config):
        """
        Calculate spine width in millimeters based on book metadata and config.

        This method determines the appropriate calculation formula based on the
        binding type and applies it to calculate the spine width in millimeters.

        Args:
            book_metadata: Book metadata object containing page count, paper type,
                binding type, and paper weight.
            config: Printer service configuration dictionary containing formula
                definitions and parameters.

        Returns:
            float: Spine width in millimeters.

        Raises:
            CalculationError: If binding type is missing, no formula configuration
                is found for the binding type, or calculation fails.
        """
        binding_type = book_metadata.binding_type
        if not binding_type:
            raise CalculationError("Binding type is required for calculation")

        # Get formula configuration for the binding type
        formulas = config.get("formulas", {})
        formula_config = formulas.get(binding_type)

        if not formula_config:
            raise CalculationError(f"No formula configuration found for binding type: {binding_type}")

        formula_type = formula_config.get("type")
        formula_params = formula_config.get("params", {})

        # Apply the appropriate formula based on type
        if formula_type == "general":
            return self._calculate_general_formula(book_metadata, config)
        elif formula_type == "pages_per_inch":
            return self._calculate_pages_per_inch_formula(book_metadata, formula_params)
        elif formula_type == "fixed_ranges":
            return self._calculate_fixed_ranges_formula(book_metadata, formula_params)
        else:
            raise CalculationError(f"Unknown formula type: {formula_type}")

    def _calculate_general_formula(self, book_metadata, config):
        """
        Calculate spine width using the general formula.

        The general formula calculates spine width based on page count, paper weight,
        paper bulk factor, and cover thickness. This is the most commonly used
        formula for spine calculations.

        Args:
            book_metadata: Book metadata object containing page count, paper type,
                paper weight, and binding type.
            config: Printer service configuration containing paper bulk and cover
                thickness parameters.

        Returns:
            float: Spine width in millimeters.

        Raises:
            CalculationError: If required parameters are missing or invalid.
        """
        page_count = book_metadata.page_count
        paper_type = book_metadata.paper_type
        paper_weight = book_metadata.paper_weight
        binding_type = book_metadata.binding_type

        if not paper_type:
            raise CalculationError("Paper type is required for general formula")

        if paper_weight is None or paper_weight <= 0:
            raise CalculationError("Paper weight is required and must be positive for general formula")

        # Get paper bulk factor
        paper_bulk = config.get("paper_bulk", {})
        bulk_factor = paper_bulk.get(paper_type)

        if bulk_factor is None:
            raise CalculationError(f"No paper bulk factor found for paper type: {paper_type}")

        # Get cover thickness
        cover_thickness = config.get("cover_thickness", {})
        thickness = cover_thickness.get(binding_type)

        if thickness is None:
            raise CalculationError(f"No cover thickness found for binding type: {binding_type}")

        # Calculate spine width: (paper_weight * bulk_factor * (page_count/2)) / 1000 + (2 * cover_thickness)
        spine_width = (paper_weight * bulk_factor * (page_count / 2)) / 1000 + (2 * thickness)

        return spine_width

    def _calculate_pages_per_inch_formula(self, book_metadata, formula_params):
        """
        Calculate spine width using pages-per-inch formula.

        This formula calculates spine width based on a fixed pages-per-inch ratio
        plus a base thickness. It's commonly used for specific binding types that
        have consistent thickness ratios.

        Args:
            book_metadata: Book metadata object containing page count.
            formula_params: Formula parameters containing pages_per_inch ratio and
                base_thickness.

        Returns:
            float: Spine width in millimeters.

        Raises:
            CalculationError: If pages_per_inch parameter is missing or invalid.
        """
        page_count = book_metadata.page_count
        pages_per_inch = formula_params.get("pages_per_inch")
        base_thickness = formula_params.get("base_thickness", 0.0)

        if pages_per_inch is None or pages_per_inch <= 0:
            raise CalculationError("pages_per_inch parameter is required and must be positive")

        # Calculate spine width in inches: (page_count / pages_per_inch) + base_thickness
        spine_width_inches = (page_count / pages_per_inch) + base_thickness
        spine_width_mm = UnitConverter.inches_to_mm(spine_width_inches)

        return spine_width_mm

    def _calculate_fixed_ranges_formula(self, book_metadata, formula_params):
        """
        Calculate spine width using fixed ranges formula.

        This formula uses predefined page count ranges with fixed spine widths.
        It's commonly used for binding types that have standardized spine widths
        for specific page count ranges.

        Args:
            book_metadata: Book metadata object containing page count.
            formula_params: Formula parameters containing range definitions.

        Returns:
            float: Spine width in millimeters.

        Raises:
            CalculationError: If no matching range is found for the page count.
        """
        page_count = book_metadata.page_count
        ranges = formula_params.get("ranges", [])

        if not ranges:
            raise CalculationError("No ranges defined in fixed ranges formula")

        # Find the matching range for the page count
        for range_def in ranges:
            min_pages = range_def.get("min_pages", 0)
            max_pages = range_def.get("max_pages", float("inf"))
            width_inches = range_def.get("width_inches")

            if width_inches is None:
                continue

            if min_pages <= page_count <= max_pages:
                # Convert inches to mm
                return UnitConverter.inches_to_mm(width_inches)

        raise CalculationError(f"No matching range found for page count: {page_count}")

    def get_supported_binding_types(self, printer_service=None):
        """
        Get list of supported binding types for a printer service.

        Args:
            printer_service: Name of printer service. If None, uses default service.

        Returns:
            list: List of supported binding type names.
        """
        try:
            config = self.config_loader.load_printer_service_config(printer_service)
            formulas = config.get("formulas", {})
            return list(formulas.keys())
        except Exception:
            return []

    def get_supported_paper_types(self, printer_service=None):
        """
        Get list of supported paper types for a printer service.

        Args:
            printer_service: Name of printer service. If None, uses default service.

        Returns:
            list: List of supported paper type names.
        """
        try:
            config = self.config_loader.load_printer_service_config(printer_service)
            paper_bulk = config.get("paper_bulk", {})
            return list(paper_bulk.keys())
        except Exception:
            return []
