# Developer Scripts

This directory contains helper scripts for maintaining and developing the project. They are designed to be run from the root of the repository.

## Scripts Overview

### `check_pydantic_v1.py`

*   **Purpose:** Scans the codebase for syntax related to Pydantic v1. This is useful for identifying code that needs to be updated during a migration to Pydantic v2.
*   **Usage:** Can be run directly.
    ```bash
    python scripts/check_pydantic_v1.py
    ```

### `check_shell_scripts.sh`

*   **Purpose:** Lints all shell scripts (`.sh`) in the project using `shellcheck`. This helps ensure that scripts are robust and follow best practices.
*   **Usage:** Can be run directly from the shell.
    ```bash
    bash scripts/check_shell_scripts.sh
    ```

### `download_models.py`

*   **Purpose:** Downloads and caches the `all-MiniLM-L6-v2` sentence transformer model from Hugging Face. This is a **required step** before running the test suite to avoid rate-limiting errors and performance test failures.
*   **Usage:** This script should be run via `hatch` to ensure it uses the correct environment and dependencies.
    ```bash
    hatch run download-models
    ```

### `update-stubs.py`

*   **Purpose:** A powerful tool for managing Python type stubs (`.pyi` files). It helps ensure that the project has accurate type information for its dependencies, which improves static analysis and code completion.
*   **Functionality:**
    *   Checks which project dependencies have community-provided stub packages available on PyPI (e.g., `types-requests`).
    *   For dependencies without community stubs, it automatically generates local stubs using `pyright`.
*   **Usage:** This script is run via `hatch` and has several commands:
    *   **Check for recommended stubs:**
        ```bash
        hatch run stubs-check
        ```
    *   **Generate local stubs:**
        ```bash
        hatch run stubs-generate
        ```
    *   **Generate stubs for a specific package:**
        ```bash
        hatch run stubs-generate --only <package-name>
        ```

### `config.py`

*   **Purpose:** This is not a runnable script. It is a configuration file that contains shared constants (like timeouts) used by other scripts in this directory.
