"""
Unit conversion utilities for book spine calculations.

This module provides comprehensive unit conversion capabilities for book spine
calculations, supporting conversions between millimeters, inches, and pixels
at various DPI settings. It includes precision handling and formatting
utilities for clear display of measurement values.
"""


class UnitConverter:
    """
    Converter for different units used in book spine calculations.

    This class provides static methods for converting between different units
    commonly used in book spine calculations: millimeters, inches, and pixels.
    It includes precision handling and formatting utilities for clear display
    of measurement values.

    The converter uses standard conversion factors and supports various DPI
    settings for pixel conversions, making it suitable for both print and
    digital applications.

    Attributes:
        MM_PER_INCH (float): Conversion factor from millimeters to inches (25.4).
        DEFAULT_DPI (int): Default DPI setting for pixel conversions (300).
    """

    # Conversion constants
    MM_PER_INCH = 25.4
    DEFAULT_DPI = 300

    @staticmethod
    def mm_to_inches(mm):
        """
        Convert millimeters to inches.

        This method converts a measurement from millimeters to inches using
        the standard conversion factor of 25.4 mm per inch.

        Args:
            mm (float): Value in millimeters to convert.

        Returns:
            float: Value in inches, rounded to 4 decimal places for precision.

        Raises:
            ValueError: If the input value is None.
        """
        if mm is None:
            raise ValueError("Input value cannot be None")
        return round(mm / UnitConverter.MM_PER_INCH, 4)

    @staticmethod
    def inches_to_mm(inches):
        """
        Convert inches to millimeters.

        This method converts a measurement from inches to millimeters using
        the standard conversion factor of 25.4 mm per inch.

        Args:
            inches (float): Value in inches to convert.

        Returns:
            float: Value in millimeters, rounded to 2 decimal places for precision.

        Raises:
            ValueError: If the input value is None.
        """
        if inches is None:
            raise ValueError("Input value cannot be None")
        return round(inches * UnitConverter.MM_PER_INCH, 2)

    @staticmethod
    def mm_to_pixels(mm, dpi=None):
        """
        Convert millimeters to pixels at specified DPI.

        This method converts a measurement from millimeters to pixels using
        the formula: pixels = (mm / 25.4) * DPI. This is commonly used
        for converting print measurements to digital pixel values.

        Args:
            mm (float): Value in millimeters to convert.
            dpi (int, optional): Dots per inch for the conversion. Defaults to 300.

        Returns:
            float: Value in pixels, rounded to 2 decimal places for precision.

        Raises:
            ValueError: If the input value is None or DPI is not positive.
        """
        if mm is None:
            raise ValueError("Input value cannot be None")
        if dpi is None:
            dpi = UnitConverter.DEFAULT_DPI
        if dpi <= 0:
            raise ValueError("DPI must be positive")
        return round((mm / UnitConverter.MM_PER_INCH) * dpi, 2)

    @staticmethod
    def inches_to_pixels(inches, dpi=None):
        """
        Convert inches to pixels at specified DPI.

        This method converts a measurement from inches to pixels using
        the formula: pixels = inches * DPI. This is commonly used for
        converting print measurements to digital pixel values.

        Args:
            inches (float): Value in inches to convert.
            dpi (int, optional): Dots per inch for the conversion. Defaults to 300.

        Returns:
            float: Value in pixels, rounded to 2 decimal places for precision.

        Raises:
            ValueError: If the input value is None or DPI is not positive.
        """
        if inches is None:
            raise ValueError("Input value cannot be None")
        if dpi is None:
            dpi = UnitConverter.DEFAULT_DPI
        if dpi <= 0:
            raise ValueError("DPI must be positive")
        return round(inches * dpi, 2)

    @staticmethod
    def pixels_to_mm(pixels, dpi=None):
        """
        Convert pixels to millimeters at specified DPI.

        This method converts a measurement from pixels to millimeters using
        the formula: mm = (pixels / DPI) * 25.4. This is commonly used
        for converting digital pixel values to print measurements.

        Args:
            pixels (float): Value in pixels to convert.
            dpi (int, optional): Dots per inch for the conversion. Defaults to 300.

        Returns:
            float: Value in millimeters, rounded to 2 decimal places for precision.

        Raises:
            ValueError: If the input value is None or DPI is not positive.
        """
        if pixels is None:
            raise ValueError("Input value cannot be None")
        if dpi is None:
            dpi = UnitConverter.DEFAULT_DPI
        if dpi <= 0:
            raise ValueError("DPI must be positive")
        return round((pixels / dpi) * UnitConverter.MM_PER_INCH, 2)

    @staticmethod
    def pixels_to_inches(pixels, dpi=None):
        """
        Convert pixels to inches at specified DPI.

        This method converts a measurement from pixels to inches using
        the formula: inches = pixels / DPI. This is commonly used for
        converting digital pixel values to print measurements.

        Args:
            pixels (float): Value in pixels to convert.
            dpi (int, optional): Dots per inch for the conversion. Defaults to 300.

        Returns:
            float: Value in inches, rounded to 4 decimal places for precision.

        Raises:
            ValueError: If the input value is None or DPI is not positive.
        """
        if pixels is None:
            raise ValueError("Input value cannot be None")
        if dpi is None:
            dpi = UnitConverter.DEFAULT_DPI
        if dpi <= 0:
            raise ValueError("DPI must be positive")
        return round(pixels / dpi, 4)

    @staticmethod
    def convert_to_all_units(value, source_unit, dpi=None):
        """
        Convert a value to all supported units (mm, inches, pixels).

        This method converts a single value from any supported unit to all
        other supported units. This is useful for providing comprehensive
        measurement information in multiple formats.

        Args:
            value (float): The value to convert from the source unit.
            source_unit (str): Source unit ('mm', 'inches', 'pixels').
            dpi (int, optional): DPI for pixel conversions. Defaults to 300.

        Returns:
            dict: Dictionary with keys 'mm', 'inches', 'pixels' containing
                converted values in each unit.

        Raises:
            ValueError: If the input value is None or the source unit is not supported.
        """
        if value is None:
            raise ValueError("Input value cannot be None")
        if dpi is None:
            dpi = UnitConverter.DEFAULT_DPI

        source_unit = source_unit.lower()

        if source_unit == "mm":
            mm_value = value
            inches_value = UnitConverter.mm_to_inches(value)
            pixels_value = UnitConverter.mm_to_pixels(value, dpi)
        elif source_unit == "inches":
            mm_value = UnitConverter.inches_to_mm(value)
            inches_value = value
            pixels_value = UnitConverter.inches_to_pixels(value, dpi)
        elif source_unit == "pixels":
            mm_value = UnitConverter.pixels_to_mm(value, dpi)
            inches_value = UnitConverter.pixels_to_inches(value, dpi)
            pixels_value = value
        else:
            raise ValueError(f"Unsupported source unit: {source_unit}. Supported units: 'mm', 'inches', 'pixels'")

        return {"mm": mm_value, "inches": inches_value, "pixels": pixels_value}

    @staticmethod
    def format_with_units(value, unit, precision=None):
        """
        Format a value with appropriate unit labels for clear display.

        This method formats a numeric value with appropriate unit labels
        for clear and consistent display. It automatically determines
        appropriate precision based on the unit type if not specified.

        Args:
            value (float): The value to format.
            unit (str): The unit ('mm', 'inches', 'pixels').
            precision (int, optional): Number of decimal places. If None,
                precision is automatically determined based on the unit.

        Returns:
            str: Formatted string with value and unit label, or "N/A" if
                the value is None.

        Example:
            >>> UnitConverter.format_with_units(12.5, "mm")
            "12.50 mm"
            >>> UnitConverter.format_with_units(0.5, "inches")
            "0.5000 in"
            >>> UnitConverter.format_with_units(150, "pixels")
            "150.00 px"
        """
        if value is None:
            return "N/A"

        unit = unit.lower()

        # Auto-determine precision based on unit if not specified
        if precision is None:
            if unit == "mm":
                precision = 2
            elif unit == "inches":
                precision = 4
            elif unit == "pixels":
                precision = 2
            else:
                precision = 2

        # Format the value
        formatted_value = f"{value:.{precision}f}"

        # Add appropriate unit label
        if unit == "mm":
            return f"{formatted_value} mm"
        elif unit == "inches":
            return f"{formatted_value} in"
        elif unit == "pixels":
            return f"{formatted_value} px"
        else:
            return f"{formatted_value} {unit}"
