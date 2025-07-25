#!/usr/bin/env python3
"""
Advanced usage examples for the BookSpine Calculator.

This example demonstrates advanced features including:
- Multiple printer service configurations
- Batch processing
- Custom output formatting
- Error handling patterns
- Performance optimization
"""

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    from src.bookspine import BookMetadata, ConfigLoader, SpineCalculator
    from src.bookspine.config.config_loader import ConfigurationError
    from src.bookspine.core.calculator import CalculationError
    from src.bookspine.models.book_metadata import ValidationError
except ImportError as e:
    print(f"Error importing bookspine: {e}")
    print("Please install bookspine: uv add bookspine")
    sys.exit(1)


def example_batch_processing():
    """Example 1: Batch processing multiple books with different configurations."""
    print("=" * 60)
    print("Example 1: Batch Processing Multiple Books")
    print("=" * 60)

    # Sample book data for batch processing
    books_data = [
        {
            "name": "Fiction Novel",
            "page_count": 350,
            "paper_type": "MCG",
            "binding_type": "Softcover Perfect Bound",
            "paper_weight": 80,
            "printer_service": "kdp",
        },
        {
            "name": "Technical Manual",
            "page_count": 120,
            "paper_type": "MCS",
            "binding_type": "Hardcover Casewrap",
            "paper_weight": 100,
            "printer_service": "ingram",
        },
        {
            "name": "Photo Book",
            "page_count": 48,
            "paper_type": "MCG",
            "binding_type": "Hardcover Linen",
            "paper_weight": 120,
            "printer_service": "blurb",
        },
    ]

    try:
        config_loader = ConfigLoader()
        calculator = SpineCalculator(config_loader)

        results = []

        for book_data in books_data:
            print(f"\nProcessing: {book_data['name']}")

            # Create metadata with proper type casting
            metadata = BookMetadata(
                page_count=int(str(book_data["page_count"])),
                paper_type=str(book_data["paper_type"]),
                binding_type=str(book_data["binding_type"]),
                paper_weight=float(str(book_data["paper_weight"])),
            )

            # Calculate spine width
            result = calculator.calculate_spine_width(metadata, printer_service=book_data["printer_service"])

            # Store results
            results.append(
                {
                    "book_name": book_data["name"],
                    "spine_width_mm": result.width_mm,
                    "spine_width_inches": result.width_inches,
                    "spine_width_pixels": result.width_pixels,
                    "printer_service": book_data["printer_service"],
                }
            )

            print(f"  Spine width: {result.width_mm:.2f} mm ({result.width_inches:.4f} inches)")

        # Save batch results to CSV
        csv_file = "batch_results.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ Batch results saved to: {csv_file}")

    except Exception as e:
        print(f"Batch processing error: {e}")


def example_custom_output_formatter():
    """Example 2: Custom output formatting for specific use cases."""
    print("\n" + "=" * 60)
    print("Example 2: Custom Output Formatting")
    print("=" * 60)

    try:
        config_loader = ConfigLoader()
        calculator = SpineCalculator(config_loader)

        # Create sample book metadata
        metadata = BookMetadata(
            page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
        )

        # Calculate with different DPI settings
        dpis = [150, 300, 600]
        results = {}

        for dpi in dpis:
            result = calculator.calculate_spine_width(metadata, dpi=dpi)
            results[dpi] = result

        # Custom formatting for different use cases
        print("📏 Print-ready measurements:")
        print(f"  Spine width: {results[300].width_mm:.2f} mm")
        print(f"  Spine width: {results[300].width_inches:.4f} inches")

        print("\n🎨 Digital design measurements:")
        for dpi, result in results.items():
            print(f"  {dpi} DPI: {result.width_pixels:.1f} pixels")

        # Create custom JSON output
        custom_output = {
            "book_info": {
                "page_count": metadata.page_count,
                "paper_type": metadata.paper_type,
                "binding_type": metadata.binding_type,
                "paper_weight": metadata.paper_weight,
            },
            "spine_measurements": {
                "metric": {"width_mm": results[300].width_mm, "width_cm": results[300].width_mm / 10},
                "imperial": {"width_inches": results[300].width_inches, "width_points": results[300].width_inches * 72},
                "digital": {
                    "150_dpi": results[150].width_pixels,
                    "300_dpi": results[300].width_pixels,
                    "600_dpi": results[600].width_pixels,
                },
            },
        }

        # Save custom output
        with open("custom_spine_data.json", "w") as f:
            json.dump(custom_output, f, indent=2)

        print(f"\n✅ Custom output saved to: custom_spine_data.json")

    except Exception as e:
        print(f"Custom formatting error: {e}")


def example_error_handling_patterns():
    """Example 3: Comprehensive error handling patterns."""
    print("\n" + "=" * 60)
    print("Example 3: Error Handling Patterns")
    print("=" * 60)

    config_loader = ConfigLoader()
    calculator = SpineCalculator(config_loader)

    # Test cases that might cause errors
    test_cases = [
        {
            "name": "Valid case",
            "metadata": BookMetadata(
                page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
            ),
            "printer_service": "kdp",
        },
        {
            "name": "Invalid paper type",
            "metadata": BookMetadata(
                page_count=200, paper_type="INVALID", binding_type="Softcover Perfect Bound", paper_weight=80
            ),
            "printer_service": "kdp",
        },
        {
            "name": "Invalid printer service",
            "metadata": BookMetadata(
                page_count=200, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
            ),
            "printer_service": "nonexistent_service",
        },
        {
            "name": "Zero page count",
            "metadata": BookMetadata(
                page_count=0, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
            ),
            "printer_service": "kdp",
        },
    ]

    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")

        try:
            result = calculator.calculate_spine_width(
                test_case["metadata"], printer_service=test_case["printer_service"]
            )
            print(f"  ✅ Success: {result.width_mm:.2f} mm")

        except ValidationError as e:
            print(f"  ❌ Validation error: {e}")
        except ConfigurationError as e:
            print(f"  ❌ Configuration error: {e}")
        except CalculationError as e:
            print(f"  ❌ Calculation error: {e}")
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")


def example_performance_optimization():
    """Example 4: Performance optimization for large-scale processing."""
    print("\n" + "=" * 60)
    print("Example 4: Performance Optimization")
    print("=" * 60)

    import time

    try:
        config_loader = ConfigLoader()
        calculator = SpineCalculator(config_loader)

        # Generate large dataset
        test_data = []
        for i in range(100):
            test_data.append(
                {
                    "page_count": 100 + (i * 10),
                    "paper_type": "MCG",
                    "binding_type": "Softcover Perfect Bound",
                    "paper_weight": 80 + (i % 3) * 20,
                }
            )

        print(f"Processing {len(test_data)} calculations...")

        # Time the processing
        start_time = time.time()

        results = []
        for i, data in enumerate(test_data):
            # Cast dictionary values to proper types
            metadata = BookMetadata(
                page_count=int(str(data["page_count"])),
                paper_type=str(data["paper_type"]),
                binding_type=str(data["binding_type"]),
                paper_weight=float(str(data["paper_weight"])),
            )
            result = calculator.calculate_spine_width(metadata)
            results.append({"index": i, "page_count": data["page_count"], "spine_width_mm": result.width_mm})

            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{len(test_data)} calculations...")

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"\n✅ Processing completed in {processing_time:.2f} seconds")
        print(f"   Average time per calculation: {processing_time / len(test_data) * 1000:.2f} ms")

        # Save performance results
        performance_data = {
            "total_calculations": len(test_data),
            "processing_time_seconds": processing_time,
            "average_time_per_calculation_ms": processing_time / len(test_data) * 1000,
            "results": results,
        }

        with open("performance_results.json", "w") as f:
            json.dump(performance_data, f, indent=2)

        print(f"✅ Performance data saved to: performance_results.json")

    except Exception as e:
        print(f"Performance test error: {e}")


def example_printer_service_comparison():
    """Example 5: Compare calculations across different printer services."""
    print("\n" + "=" * 60)
    print("Example 5: Printer Service Comparison")
    print("=" * 60)

    try:
        config_loader = ConfigLoader()
        calculator = SpineCalculator(config_loader)

        # Get available services
        services = config_loader.list_available_services()
        print(f"Available printer services: {', '.join(services)}")

        # Test book configuration
        metadata = BookMetadata(
            page_count=300, paper_type="MCG", binding_type="Softcover Perfect Bound", paper_weight=80
        )

        print(f"\nComparing spine calculations for {metadata.page_count} pages:")
        print(f"Paper: {metadata.paper_type}, Binding: {metadata.binding_type}, Weight: {metadata.paper_weight} gsm")
        print("\n" + "-" * 80)
        print(f"{'Service':<20} {'Width (mm)':<12} {'Width (in)':<12} {'Width (px)':<12}")
        print("-" * 80)

        comparison_results = []

        for service in services:
            try:
                result = calculator.calculate_spine_width(metadata, printer_service=service)

                print(
                    f"{service:<20} {result.width_mm:<12.2f} {result.width_inches:<12.4f} {result.width_pixels:<12.1f}"
                )

                comparison_results.append(
                    {
                        "service": service,
                        "width_mm": result.width_mm,
                        "width_inches": result.width_inches,
                        "width_pixels": result.width_pixels,
                    }
                )

            except Exception as e:
                print(f"{service:<20} {'ERROR':<12} {'ERROR':<12} {'ERROR':<12}")
                print(f"  Error: {e}")

        # Save comparison results
        with open("printer_service_comparison.json", "w") as f:
            json.dump(
                {
                    "book_configuration": {
                        "page_count": metadata.page_count,
                        "paper_type": metadata.paper_type,
                        "binding_type": metadata.binding_type,
                        "paper_weight": metadata.paper_weight,
                    },
                    "comparison_results": comparison_results,
                },
                f,
                indent=2,
            )

        print(f"\n✅ Comparison results saved to: printer_service_comparison.json")

    except Exception as e:
        print(f"Printer service comparison error: {e}")


def main():
    """
    Run all advanced examples to demonstrate BookSpine library capabilities.
    """
    print("BookSpine Library - Advanced Usage Examples")
    print("=" * 60)
    print("This script demonstrates advanced features and patterns for using")
    print("the BookSpine library in production environments.")

    try:
        example_batch_processing()
        example_custom_output_formatter()
        example_error_handling_patterns()
        example_performance_optimization()
        example_printer_service_comparison()

        print("\n" + "=" * 60)
        print("🎉 All advanced examples completed successfully!")
        print("=" * 60)
        print("\nGenerated files:")
        print("  - batch_results.csv")
        print("  - custom_spine_data.json")
        print("  - performance_results.json")
        print("  - printer_service_comparison.json")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
