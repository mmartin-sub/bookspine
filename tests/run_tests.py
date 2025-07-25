#!/usr/bin/env python3
"""
Comprehensive test runner for the BookSpine project.

This script provides multiple ways to run tests:
- All tests with coverage
- Unit tests only
- Integration tests only
- Specific test categories
- Performance tests
- Resource-based tests

Usage:
    python run_tests.py                    # Run all tests with coverage
    python run_tests.py --unit            # Run unit tests only
    python run_tests.py --integration     # Run integration tests only
    python run_tests.py --resources       # Run resource-based tests only
    python run_tests.py --performance     # Run performance tests only
    python run_tests.py --kte             # Run KTE-related tests only
    python run_tests.py --spine           # Run spine-related tests only
    python run_tests.py --quick           # Run quick tests (no performance)
    python run_tests.py --verbose         # Run with verbose output
    python run_tests.py --html            # Generate HTML coverage report
    python run_tests.py --ci              # Run in CI mode (minimal output)
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """Comprehensive test runner for the BookSpine project."""

    def __init__(self):
        # Get the project root (parent of tests directory)
        self.project_root = Path(__file__).resolve().parent.parent
        self.tests_dir = self.project_root / "tests"
        self.results_dir = self.tests_dir / "test_results"
        # Ensure the parent directory exists before creating the results directory
        self.results_dir.parent.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)

    def run_command(self, command: List[str], capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        print(f"Running: {' '.join(command)}")
        start_time = time.time()

        try:
            result = subprocess.run(command, capture_output=capture_output, text=True, cwd=self.project_root)
            end_time = time.time()
            print(f"Command completed in {end_time - start_time:.2f} seconds")
            return result
        except Exception as e:
            print(f"Error running command: {e}")
            sys.exit(1)

    def run_pytest(self, args: List[str], coverage: bool = True) -> subprocess.CompletedProcess:
        """Run pytest with the given arguments."""
        pytest_args = ["python", "-m", "pytest"]

        if coverage:
            pytest_args.extend(
                [
                    "--cov=bookspine",
                    "--cov-report=term-missing",
                    "--cov-report=html:tests/htmlcov",
                    f"--cov-config={self.project_root.absolute()}/pyproject.toml",
                ]
            )

        pytest_args.extend(args)
        return self.run_command(pytest_args)

    def run_linting(self) -> bool:
        """Run linting checks."""
        print("\n" + "=" * 60)
        print("RUNNING LINTING CHECKS")
        print("=" * 60)

        # Run ruff
        print("\n--- Running Ruff (linter) ---")
        ruff_result = self.run_command(["ruff", "check", "."])
        if ruff_result.returncode != 0:
            print("❌ Ruff found issues")
            return False

        # Run black check
        print("\n--- Running Black (code formatting) ---")
        black_result = self.run_command(["black", "--check", "--diff", "."])
        if black_result.returncode != 0:
            print("❌ Black found formatting issues")
            return False

        print("✅ All linting checks passed")
        return True

    def run_type_checking(self) -> bool:
        """Run type checking with mypy."""
        print("\n" + "=" * 60)
        print("RUNNING TYPE CHECKING")
        print("=" * 60)

        mypy_result = self.run_command(["mypy", "bookspine/"])
        if mypy_result.returncode != 0:
            print("❌ MyPy found type issues")
            return False

        print("✅ Type checking passed")
        return True

    def run_unit_tests(self, verbose: bool = False) -> bool:
        """Run unit tests."""
        print("\n" + "=" * 60)
        print("RUNNING UNIT TESTS")
        print("=" * 60)

        args = ["tests/spine/unit/", "tests/kte/unit/"]
        if verbose:
            args.append("-v")

        result = self.run_pytest(args)
        return result.returncode == 0

    def run_integration_tests(self, verbose: bool = False) -> bool:
        """Run integration tests."""
        print("\n" + "=" * 60)
        print("RUNNING INTEGRATION TESTS")
        print("=" * 60)

        args = ["tests/spine/integration/", "tests/kte/integration/"]
        if verbose:
            args.append("-v")

        result = self.run_pytest(args)
        return result.returncode == 0

    def run_spine_tests(self, verbose: bool = False) -> bool:
        """Run spine-related tests."""
        print("\n" + "=" * 60)
        print("RUNNING SPINE TESTS")
        print("=" * 60)

        args = ["tests/spine/"]
        if verbose:
            args.append("-v")

        result = self.run_pytest(args)
        return result.returncode == 0

    def run_kte_tests(self, verbose: bool = False) -> bool:
        """Run KTE-related tests."""
        print("\n" + "=" * 60)
        print("RUNNING KTE TESTS")
        print("=" * 60)

        args = ["tests/kte/"]
        if verbose:
            args.append("-v")

        result = self.run_pytest(args)
        return result.returncode == 0

    def run_resource_tests(self, verbose: bool = False) -> bool:
        """Run resource-based tests."""
        print("\n" + "=" * 60)
        print("RUNNING RESOURCE-BASED TESTS")
        print("=" * 60)

        args = ["tests/spine/unit/test_pdf_resources.py", "tests/kte/unit/test_kte_resources.py"]
        if verbose:
            args.append("-v")

        result = self.run_pytest(args)
        return result.returncode == 0

    def run_performance_tests(self, verbose: bool = False) -> bool:
        """Run performance tests."""
        print("\n" + "=" * 60)
        print("RUNNING PERFORMANCE TESTS")
        print("=" * 60)

        args = ["tests/spine/integration/test_performance.py"]
        if verbose:
            args.append("-v")

        result = self.run_pytest(args)
        return result.returncode == 0

    def run_all_tests(self, verbose: bool = False, quick: bool = False) -> bool:
        """Run all tests."""
        print("\n" + "=" * 60)
        print("RUNNING ALL TESTS")
        print("=" * 60)

        args = ["tests/"]
        if verbose:
            args.append("-v")

        if quick:
            # Exclude performance tests for quick runs
            args.extend(["-k", "not performance"])

        result = self.run_pytest(args)
        return result.returncode == 0

    def run_ci_tests(self) -> bool:
        """Run tests in CI mode (minimal output, all checks)."""
        print("\n" + "=" * 60)
        print("RUNNING CI TESTS")
        print("=" * 60)

        # Run linting
        if not self.run_linting():
            return False

        # Run type checking
        if not self.run_type_checking():
            return False

        # Run all tests with coverage
        if not self.run_all_tests(verbose=False):
            return False

        print("✅ All CI checks passed")
        return True

    def generate_html_report(self):
        """Generate HTML coverage report."""
        print("\n" + "=" * 60)
        print("GENERATING HTML COVERAGE REPORT")
        print("=" * 60)

        # Run tests with HTML coverage
        result = self.run_pytest(["tests/"], coverage=True)

        if result.returncode == 0:
            print(f"✅ HTML coverage report generated in: {self.project_root}/tests/htmlcov/")
            print("Open tests/htmlcov/index.html in your browser to view the report")
        else:
            print("❌ Failed to generate HTML coverage report")

        return result.returncode == 0

    def print_summary(self, results: dict):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        for test_type, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_type:20} {status}")

        all_passed = all(results.values())
        if all_passed:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Some tests failed!")

        return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for the BookSpine project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_tests.py                    # Run all tests with coverage
    python run_tests.py --unit            # Run unit tests only
    python run_tests.py --integration     # Run integration tests only
    python run_tests.py --resources       # Run resource-based tests only
    python run_tests.py --performance     # Run performance tests only
    python run_tests.py --kte             # Run KTE-related tests only
    python run_tests.py --spine           # Run spine-related tests only
    python run_tests.py --quick           # Run quick tests (no performance)
    python run_tests.py --verbose         # Run with verbose output
    python run_tests.py --html            # Generate HTML coverage report
    python run_tests.py --ci              # Run in CI mode (minimal output)
        """,
    )

    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--resources", action="store_true", help="Run resource-based tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--kte", action="store_true", help="Run KTE-related tests only")
    parser.add_argument("--spine", action="store_true", help="Run spine-related tests only")
    parser.add_argument("--quick", action="store_true", help="Run quick tests (exclude performance)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Run with verbose output")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--ci", action="store_true", help="Run in CI mode (all checks)")
    parser.add_argument("--lint", action="store_true", help="Run linting checks only")
    parser.add_argument("--types", action="store_true", help="Run type checking only")

    args = parser.parse_args()

    runner = TestRunner()
    results = {}

    try:
        if args.ci:
            # CI mode: run all checks
            success = runner.run_ci_tests()
            sys.exit(0 if success else 1)

        elif args.html:
            # Generate HTML report
            success = runner.generate_html_report()
            sys.exit(0 if success else 1)

        elif args.lint:
            # Linting only
            success = runner.run_linting()
            sys.exit(0 if success else 1)

        elif args.types:
            # Type checking only
            success = runner.run_type_checking()
            sys.exit(0 if success else 1)

        elif args.unit:
            # Unit tests only
            results["Unit Tests"] = runner.run_unit_tests(args.verbose)

        elif args.integration:
            # Integration tests only
            results["Integration Tests"] = runner.run_integration_tests(args.verbose)

        elif args.resources:
            # Resource-based tests only
            results["Resource Tests"] = runner.run_resource_tests(args.verbose)

        elif args.performance:
            # Performance tests only
            results["Performance Tests"] = runner.run_performance_tests(args.verbose)

        elif args.kte:
            # KTE tests only
            results["KTE Tests"] = runner.run_kte_tests(args.verbose)

        elif args.spine:
            # Spine tests only
            results["Spine Tests"] = runner.run_spine_tests(args.verbose)

        else:
            # Default: run all tests
            results["All Tests"] = runner.run_all_tests(args.verbose, args.quick)

        # Print summary and exit
        success = runner.print_summary(results)
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
