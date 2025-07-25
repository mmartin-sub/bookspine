#!/bin/bash
# Setup development environment for Book Spine Calculator

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install package in development mode with all extras
echo "Installing package in development mode with all extras..."
pip install -e ".[dev,test,docs]"

# Install pre-commit hooks if pre-commit is available
if command -v pre-commit &> /dev/null; then
    echo "Setting up pre-commit hooks..."
    pre-commit install
fi

echo "Development environment setup complete!"
echo "To activate the virtual environment, run: source venv/bin/activate"
