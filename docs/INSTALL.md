# Installation

This document provides instructions for installing the BookSpine project, both for end-users and for developers who want to contribute to the project.

## User Installation

For end-users who want to use the `bookspine` and `kte` command-line tools, you can install the project using `pip`.

### Prerequisites

- Python 3.9 or higher

### Installation Options

The project offers different installation options depending on your needs:

-   **Default installation (recommended):** This installs the project with support for remote keyword extraction using the Hugging Face Inference API or a local Docker container. This is a lightweight installation that does not require `torch` or `sentence-transformers`.
    ```bash
    pip install bookspine
    ```

-   **Installation with local models:** If you want to run the keyword extraction models locally, you can install the `local-models` extra. This will install `torch` and `sentence-transformers`.
    ```bash
    pip install "bookspine[local-models]"
    ```

### Installation from Source

If you have downloaded the project source code, you can install it using `pip`:

-   **Default installation:**
    ```bash
    pip install .
    ```

-   **With local models:**
    ```bash
    pip install ".[local-models]"
    ```

## Developer Installation

For developers who want to set up a development environment to work on the project, we use `hatch` for environment and dependency management. The development environment includes all dependencies, including those for local models.

### Prerequisites

- Python 3.9 or higher
- `hatch` installed. If you don't have `hatch`, you can install it with:
  ```bash
  pip install hatch
  ```

### Setup Steps

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd bookspine
    ```

2.  **Create the development environment:**
    `hatch` will automatically create a virtual environment, install all dependencies (including development and test dependencies), and install the `bookspine` and `kte` packages in editable mode.
    ```bash
    hatch env create
    ```

3.  **Activate the environment:**
    To activate the virtual environment and use the installed tools, run:
    ```bash
    hatch shell
    ```
    You are now in the project's development environment.

4.  **Running tests:**
    To run the test suite, you can use the `test-cov` script defined in `pyproject.toml`:
    ```bash
    hatch run test-cov
    ```

5.  **Running linters and formatters:**
    You can run the linters and formatters using `hatch`:
    ```bash
    hatch run lint
    hatch run style
    hatch run typing
    ```
