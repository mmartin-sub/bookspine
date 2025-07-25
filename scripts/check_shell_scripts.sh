#!/bin/bash

# Simple shell script checker
# This script checks shell scripts for basic syntax and common issues

set -e

echo "Checking shell scripts..."

# Check if bash is available
if ! command -v bash &> /dev/null; then
    echo "ERROR: bash is not available"
    exit 1
fi

# Check the test.sh script
if [ -f "tests/test.sh" ]; then
    echo "Checking tests/test.sh..."

    # Check if the script is executable
    if [ ! -x "tests/test.sh" ]; then
        echo "WARNING: tests/test.sh is not executable"
        chmod +x tests/test.sh
    fi

    # Check for basic syntax errors
    if bash -n tests/test.sh; then
        echo "✅ tests/test.sh syntax is valid"
    else
        echo "❌ tests/test.sh has syntax errors"
        exit 1
    fi

    # Check for common issues
    echo "Checking for common shell script issues..."

    # Check for proper shebang
    if ! head -1 tests/test.sh | grep -q "^#!/bin/bash"; then
        echo "WARNING: tests/test.sh should start with #!/bin/bash"
    fi

    # Check for set -e
    if ! grep -q "set -e" tests/test.sh; then
        echo "WARNING: tests/test.sh should use 'set -e' for error handling"
    fi

    # Check for proper function definitions
    if grep -q "^[[:space:]]*function " tests/test.sh; then
        echo "WARNING: Consider using 'func_name()' instead of 'function func_name'"
    fi

    # Check for proper quoting
    if grep -q '\$[A-Za-z_][A-Za-z0-9_]*[^"]' tests/test.sh; then
        echo "WARNING: Consider quoting variables in tests/test.sh"
    fi

    echo "✅ Basic shell script checks completed"
else
    echo "ERROR: tests/test.sh not found"
    exit 1
fi

echo "Shell script validation completed successfully!"
