#!/usr/bin/env python3
"""
Basic usage example for the BookSpine Calculator.

This example demonstrates how to use the BookSpine library programmatically
to calculate book spine dimensions for various scenarios.
"""

import sys
from pathlib import Path

try:
    from src.bookspine import BookMetadata, ConfigLoader, SpineCalculator
    from src.bookspine.config.config_loader import ConfigurationError
    from src.bookspine.models.book_metadata import ValidationError
except ImportError as e:
    print(f"Error importing bookspine: {e}")
    print("Please install bookspine: uv add bookspine")
    sys.exit(1)


def example_basic_calculation():
    """Example 1: Basic spine calculation with manual parameters."""
    print("=" * 60)
    print("Example 1: Basic Spine Calculation")
    print("=" * 60)

    try:
        # Create config loader
        config_loader = ConfigLoader()

        # Create calculator
        calculator = SpineCalculator(config_loader)

        # Create book metadata
        metadata = BookMetadata(
            page_count=200,
            paper_type="MCG",
            binding_type="Softcover Perfect Bound",
            paper_weight=80,
            unit_system="metric",
        )

        # Calculate spine width
        result = calculator.calculate_spine_width(metadata)

        # Print results
        print(f"Page Count: {metadata.page_count}")
        print(f"Paper Type: {metadata.paper_type}")
        print(f"Binding Type: {metadata.binding_type}")
        print(f"Paper Weight: {metadata.paper_weight} gsm")
        print(f"Unit System: {metadata.unit_system}")
        print("\nCalculated Spine Dimensions:")
        print(f"  Width: {result.width_mm:.2f} mm")
        print(f"  Width: {result.width_inches:.4f} inches")
        print(f"  Width: {result.width_pixels:.0f} pixels at {result.dpi} DPI")

    except ValidationError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"Calculation error: {e}")


def example_printer_service():
    """Example 2: Using a printer service configuration."""
    print("\n" + "=" * 60)
    print("Example 2: Using Printer Service (KDP)")
    print("=" * 60)

    try:
        config_loader = ConfigLoader()
        calculator = SpineCalculator(config_loader)

        # Create minimal metadata (printer service provides defaults)
        metadata = BookMetadata(
            page_count=150,
            binding_type="Softcover Perfect Bound",
            unit_system="imperial",  # Use imperial for this example
        )

        # Calculate using KDP printer service
        result = calculator.calculate_spine_width(metadata, printer_service="kdp")

        print(f"Page Count: {metadata.page_count}")
        print(f"Binding Type: {metadata.binding_type}")
        print(f"Unit System: {metadata.unit_system}")
        print(f"Printer Service: kdp")
        print("\nCalculated Spine Dimensions:")
        print(f"  Width: {result.width_mm:.2f} mm")
        print(f"  Width: {result.width_inches:.4f} inches")
        print(f"  Width: {result.width_pixels:.0f} pixels at {result.dpi} DPI")

    except ConfigurationError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Calculation error: {e}")


def example_manual_override():
    """Example 3: Using manual override."""
    print("\n" + "=" * 60)
    print("Example 3: Manual Override")
    print("=" * 60)

    try:
        config_loader = ConfigLoader()
        calculator = SpineCalculator(config_loader)

        metadata = BookMetadata(
            page_count=300,
            paper_type="OFF",
            binding_type="Softcover Perfect Bound",
            paper_weight=90,
            unit_system="metric",
        )

        # Calculate with manual override
        manual_width_mm = 15.0
        result = calculator.calculate_spine_width(
            metadata,
            manual_override=manual_width_mm,
            dpi=600,  # High resolution
        )

        print(f"Page Count: {metadata.page_count}")
        print(f"Paper Type: {metadata.paper_type}")
        print(f"Binding Type: {metadata.binding_type}")
        print(f"Paper Weight: {metadata.paper_weight} gsm")
        print(f"Manual Override: {manual_width_mm} mm")
        print("\nFinal Spine Dimensions:")
        print(f"  Width: {result.width_mm:.2f} mm (manual override)")
        print(f"  Width: {result.width_inches:.4f} inches")
        print(f"  Width: {result.width_pixels:.0f} pixels at {result.dpi} DPI")

        if result.original_calculated_width_mm:
            print(f"\nOriginal calculated width: {result.original_calculated_width_mm:.2f} mm")

    except Exception as e:
        print(f"Calculation error: {e}")


def example_output_formats():
    """Example 4: Different output formats."""
    print("\n" + "=" * 60)
    print("Example 4: Output Formats")
    print("=" * 60)

    try:
        config_loader = ConfigLoader()
        calculator = SpineCalculator(config_loader)

        metadata = BookMetadata(
            page_count=100,
            paper_type="MCS",
            binding_type="Softcover Perfect Bound",
            paper_weight=70,
            unit_system="metric",
        )

        result = calculator.calculate_spine_width(metadata)

        print("JSON Output:")
        print(result.to_json(indent=2))

        print("\nCSV Output (with headers):")
        print(result.to_csv(include_headers=True))

        print("\nFormatted Summary:")
        print(result.get_formatted_summary())

    except Exception as e:
        print(f"Output formatting error: {e}")


def example_list_services():
    """Example 5: List available printer services."""
    print("\n" + "=" * 60)
    print("Example 5: Available Printer Services")
    print("=" * 60)

    try:
        config_loader = ConfigLoader()
        services = config_loader.list_available_services()

        print("Available printer services:")
        for service in services:
            print(f"  • {service}")

        print(f"\nTotal services available: {len(services)}")

    except ConfigurationError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Error listing services: {e}")


def main():
    """
    Run all examples to demonstrate BookSpine library usage.
    """
    print("BookSpine Library - Usage Examples")
    print("=" * 60)
    print("This script demonstrates various ways to use the BookSpine library")
    print("for calculating book spine dimensions programmatically.")

    try:
        example_basic_calculation()
        example_printer_service()
        example_manual_override()
        example_output_formats()
        example_list_services()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        print("\nFor CLI usage, try:")
        print("  python -m src.bookspine.cli --help")
        print("  python -m src.bookspine.cli --list-services")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
