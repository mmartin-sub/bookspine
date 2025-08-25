"""
Centralized configuration for test paths.

This module defines the paths for various test-related directories,
such as input samples and generated test files. It allows for easy
configuration and overriding of these paths via environment variables.
"""

import os
from pathlib import Path

# The root directory of the tests.
TESTS_ROOT_DIR = Path(__file__).parent.resolve()

# --- Input Samples ---
# The default directory for input samples used in tests.
DEFAULT_SAMPLES_DIR = TESTS_ROOT_DIR / "resources"

# The directory for input samples can be overridden by the TEST_SAMPLES_DIR env var.
# This is useful for running tests against a local collection of documents.
SAMPLES_DIR = Path(os.environ.get("TEST_SAMPLES_DIR", DEFAULT_SAMPLES_DIR))

# --- Generated Test Files ---
# The directory for files generated during tests (e.g., temporary outputs, logs).
# This directory is intended to be in .gitignore.
GENERATED_FILES_DIR = TESTS_ROOT_DIR / "generated"

# --- Debug Artifacts ---
# The directory for debug artifacts. For now, this is the same as the generated files dir.
DEBUG_ARTIFACTS_DIR = GENERATED_FILES_DIR


def ensure_test_dirs_exist():
    """
    Ensures that the directories for generated test files exist.
    This can be called from a pytest fixture in conftest.py.
    """
    GENERATED_FILES_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


# You can call this function at the end of the file if you want the directories
# to be created as soon as this module is imported.
ensure_test_dirs_exist()
