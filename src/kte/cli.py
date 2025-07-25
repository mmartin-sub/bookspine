"""
Command-line interface for the Keyword Theme Extraction (KTE) tool.

This module provides a command-line interface for extracting keywords and themes
from book content using KeyBERT, with special emphasis on multi-word phrases
and header content.
"""

import argparse
import sys
from typing import Optional

from .core.extractor import extract_keywords
from .core.output_handler import OutputHandler
from .models.extraction_options import ExtractionOptions


def validate_cli_arguments(args) -> Optional[str]:
    """
    Validate command-line arguments and return error message if validation fails.

    Args:
        args: Parsed command-line arguments object containing all user inputs.

    Returns:
        Optional[str]: Error message if validation fails, None if validation passes.
    """
    # Validate input source
    if not args.file and not args.text:
        return "Error: Either --file or --text must be provided"

    if args.file and args.text:
        return "Error: Cannot specify both --file and --text"

    # Validate max_keywords
    if args.max_keywords <= 0:
        return f"Max keywords must be positive, got: {args.max_keywords}"

    if args.max_keywords > 100:
        return f"Max keywords seems too high: {args.max_keywords}. Recommended range is 1-50."

    # Validate min_relevance
    if args.min_relevance < 0.0 or args.min_relevance > 1.0:
        return f"Min relevance must be between 0.0 and 1.0, got: {args.min_relevance}"

    # Validate header_weight_factor
    if args.header_weight_factor < 0.0:
        return f"Header weight factor must be non-negative, got: {args.header_weight_factor}"

    if args.header_weight_factor > 10.0:
        return f"Header weight factor seems too high: {args.header_weight_factor}. Recommended range is 0.0-5.0."

    return None


def parse_args():
    """
    Parse command-line arguments for the KTE CLI.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Keyword Theme Extraction (KTE) - Extract keywords and themes from book content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kte --file document.pdf --max-keywords 10
  kte --text "Your text content here" --format json
  kte --file book.pdf --min-relevance 0.3 --header-weight-factor 2.0
        """,
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file", "-f", help="Path to input file (PDF, TXT, MD, etc.)")
    input_group.add_argument("--text", "-t", help="Input text content directly")

    # Extraction options
    parser.add_argument(
        "--max-keywords", "-k", type=int, default=10, help="Maximum number of keywords to extract (default: 10)"
    )
    parser.add_argument(
        "--min-relevance",
        "-r",
        type=float,
        default=0.1,
        help="Minimum relevance score for keywords (0.0-1.0, default: 0.1)",
    )
    parser.add_argument(
        "--header-weight-factor", "-w", type=float, default=1.5, help="Weight factor for header content (default: 1.5)"
    )
    parser.add_argument(
        "--no-prefer-phrases", action="store_true", help="Don't prefer multi-word phrases over single words"
    )

    # Output options
    parser.add_argument(
        "--format", "-o", choices=["text", "json"], default="text", help="Output format (default: text)"
    )
    parser.add_argument("--output-file", "-O", help="Output file path (if not specified, prints to stdout)")

    # Verbosity
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    return parser.parse_args()


def main():
    """
    Main entry point for the KTE CLI.

    This function orchestrates the keyword extraction workflow, including
    argument parsing, validation, extraction, and output formatting.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    try:
        # Parse command-line arguments
        args = parse_args()

        # Validate arguments
        error_msg = validate_cli_arguments(args)
        if error_msg:
            print(error_msg, file=sys.stderr)
            return 1

        # Prepare input source
        input_source = args.text if args.text else args.file

        # Prepare options
        options = {
            "max_keywords": args.max_keywords,
            "min_relevance": args.min_relevance,
            "header_weight_factor": args.header_weight_factor,
            "prefer_phrases": not args.no_prefer_phrases,
            "language": "english",
        }

        if args.verbose:
            print(f"Extracting keywords from: {input_source}")
            print(f"Options: {options}")

        # Extract keywords
        result = extract_keywords(input_source, options, args.output_file)

        # Format output
        if args.format == "json":
            output = result.to_json()
        else:
            output_handler = OutputHandler()
            output = output_handler.format_console_output(result)

        # Output to file or stdout
        if args.output_file:
            with open(args.output_file, "w") as f:
                f.write(output)
            if args.verbose:
                print(f"Results written to: {args.output_file}")
        else:
            print(output)

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
