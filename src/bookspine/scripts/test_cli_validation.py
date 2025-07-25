#!/usr/bin/env python3
"""
Simple test script to verify CLI validation is working correctly.
"""

import subprocess  # nosec B404
import sys


def run_cli_command(args):
    """Run CLI command and return exit code and output."""
    cmd = [sys.executable, "-m", "src.bookspine.cli"] + args
    # nosec B603
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def test_validation():
    """Test various validation scenarios."""
    print("Testing CLI validation...")

    # Test 1: Invalid page count (provide required args to get to page count validation)
    print("1. Testing invalid page count...")
    exit_code, stdout, stderr = run_cli_command(
        [
            "--page-count",
            "-5",
            "--paper-type",
            "MCG",
            "--binding-type",
            "Softcover Perfect Bound",
            "--paper-weight",
            "80",
        ]
    )
    assert exit_code == 1, f"Expected exit code 1, got {exit_code}"
    assert "Page count must be positive" in stderr, f"Expected validation error, got: {stderr}"
    print("   ✓ Invalid page count validation works")

    # Test 2: Invalid paper type
    print("2. Testing invalid paper type...")
    exit_code, stdout, stderr = run_cli_command(["--page-count", "100", "--paper-type", "INVALID"])
    assert exit_code == 2, f"Expected exit code 2, got {exit_code}"
    assert "invalid choice" in stderr, f"Expected validation error, got: {stderr}"
    print("   ✓ Invalid paper type validation works")

    # Test 3: Invalid binding type
    print("3. Testing invalid binding type...")
    exit_code, stdout, stderr = run_cli_command(["--page-count", "100", "--binding-type", "Invalid Binding"])
    assert exit_code == 2, f"Expected exit code 2, got {exit_code}"
    assert "invalid choice" in stderr, f"Expected validation error, got: {stderr}"
    print("   ✓ Invalid binding type validation works")

    # Test 4: Invalid printer service
    print("4. Testing invalid printer service...")
    exit_code, stdout, stderr = run_cli_command(
        ["--page-count", "100", "--printer-service", "invalid_service", "--binding-type", "Softcover Perfect Bound"]
    )
    assert exit_code == 1, f"Expected exit code 1, got {exit_code}"
    assert "Invalid printer service" in stderr, f"Expected validation error, got: {stderr}"
    print("   ✓ Invalid printer service validation works")

    # Test 5: Missing required arguments
    print("5. Testing missing required arguments...")
    exit_code, stdout, stderr = run_cli_command(["--page-count", "100"])
    assert exit_code == 1, f"Expected exit code 1, got {exit_code}"
    assert "Missing required argument: paper type" in stderr, f"Expected validation error, got: {stderr}"
    print("   ✓ Missing required arguments validation works")

    # Test 6: Valid arguments should work
    print("6. Testing valid arguments...")
    exit_code, stdout, stderr = run_cli_command(
        [
            "--page-count",
            "100",
            "--paper-type",
            "MCG",
            "--binding-type",
            "Softcover Perfect Bound",
            "--paper-weight",
            "80",
        ]
    )
    assert exit_code == 0, f"Expected exit code 0, got {exit_code}. stderr: {stderr}"
    assert "Spine Width:" in stdout, f"Expected calculation result, got: {stdout}"
    print("   ✓ Valid arguments work correctly")

    # Test 7: List services should work
    print("7. Testing list services...")
    exit_code, stdout, stderr = run_cli_command(["--list-services"])
    assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
    assert "Available printer services:" in stdout, f"Expected services list, got: {stdout}"
    print("   ✓ List services works correctly")

    print("\n✅ All CLI validation tests passed!")


if __name__ == "__main__":
    test_validation()
