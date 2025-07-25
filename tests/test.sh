#!/bin/bash

# Quick test runner for BookSpine project
# Usage: ./tests/test.sh [option]
# Options:
#   all        - Run all tests (default)
#   unit       - Run unit tests only
#   integration - Run integration tests only
#   resources  - Run resource-based tests only
#   kte        - Run KTE tests only
#   spine      - Run spine tests only
#   quick      - Run quick tests (no performance)
#   ci         - Run CI mode (all checks)
#   lint       - Run linting only
#   types      - Run type checking only

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to run a command and check its exit status
run_command() {
    local cmd="$1"
    local description="$2"

    print_status "Running: $description"
    echo "Command: $cmd"

    if eval "$cmd"; then
        print_success "$description completed successfully"
        return 0
    else
        print_error "$description failed"
        return 1
    fi
}

# Function to check if we're in a virtual environment
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "Not in a virtual environment. Consider activating one."
    else
        print_status "Using virtual environment: $VIRTUAL_ENV"
    fi
}

# Function to install dependencies if needed
install_deps() {
    if command -v uv &> /dev/null; then
        print_status "Installing dependencies with uv..."
        uv sync --dev
    else
        print_warning "uv not found. Please install uv or use pip."
    fi
}

# Main function
main() {
    local option="${1:-all}"

    echo "=========================================="
    echo "BookSpine Test Runner"
    echo "=========================================="

    check_venv

    case $option in
        "all")
            print_status "Running all tests..."
            run_command "python run_tests.py" "All tests"
            ;;
        "unit")
            print_status "Running unit tests..."
            run_command "python run_tests.py --unit --verbose" "Unit tests"
            ;;
        "integration")
            print_status "Running integration tests..."
            run_command "python run_tests.py --integration --verbose" "Integration tests"
            ;;
        "resources")
            print_status "Running resource-based tests..."
            run_command "python run_tests.py --resources --verbose" "Resource tests"
            ;;
        "kte")
            print_status "Running KTE tests..."
            run_command "python run_tests.py --kte --verbose" "KTE tests"
            ;;
        "spine")
            print_status "Running spine tests..."
            run_command "python run_tests.py --spine --verbose" "Spine tests"
            ;;
        "quick")
            print_status "Running quick tests (no performance)..."
            run_command "python run_tests.py --quick --verbose" "Quick tests"
            ;;
        "ci")
            print_status "Running CI mode (all checks)..."
            run_command "python run_tests.py --ci" "CI checks"
            ;;
        "lint")
            print_status "Running linting checks..."
            run_command "python run_tests.py --lint" "Linting"
            ;;
        "types")
            print_status "Running type checking..."
            run_command "python run_tests.py --types" "Type checking"
            ;;
        "install")
            print_status "Installing dependencies..."
            install_deps
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [option]"
            echo ""
            echo "Options:"
            echo "  all        - Run all tests (default)"
            echo "  unit       - Run unit tests only"
            echo "  integration - Run integration tests only"
            echo "  resources  - Run resource-based tests only"
            echo "  kte        - Run KTE tests only"
            echo "  spine      - Run spine tests only"
            echo "  quick      - Run quick tests (no performance)"
            echo "  ci         - Run CI mode (all checks)"
            echo "  lint       - Run linting only"
            echo "  types      - Run type checking only"
            echo "  install    - Install dependencies"
            echo "  help       - Show this help"
            ;;
        *)
            print_error "Unknown option: $option"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
