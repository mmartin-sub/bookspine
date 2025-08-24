# Agent Instructions

This file provides instructions for AI agents working on this project.

## Project Overview

This project contains two main packages:

- `bookspine`: A tool for calculating book spine dimensions.
- `kte`: A tool for extracting keywords and themes from book content.

## Development Environment

The development environment is managed by `hatch`. To get started, run:

```bash
hatch shell
```

This will create a virtual environment and install all the necessary dependencies.

## High-Level Plan

The following plan has been approved to make the code production-grade:

1. **Update `AGENTS.md`**: Create an `AGENTS.md` file and document the plan that the user has approved. This will serve as a guide for me and any future agents working on this project.
2. **Refactor `extract_keywords`**: Analyze the `extract_keywords` function and break it down into smaller, more manageable functions. I will also add docstrings and comments where necessary.
3. **Improve Test Suite**:
    - Replace the custom `PDFTestUtils` with `fpdf2` to generate more realistic test PDFs. This will improve the robustness of the tests that rely on PDF files.
    - Add unit tests for the `cli.py` modules of both `bookspine` and `kte` to increase test coverage.
4. **Standardize Development Environment**:
    - Delete the `scripts/setup_dev.sh` script to unify the development setup around `hatch`.
    - Add a `README.md` file to the `scripts` directory to document the purpose and usage of the developer scripts.
5. **Update Documentation**: Update the `env.example` file to provide more detailed explanations of the `KTE_ENGINE` options and to mark the `infinity` engine as deprecated.
6. **Final Verification**: Run all the checks (`pyright`, `pre-commit`, and `pytest`) to ensure that all changes are correct and have not introduced any regressions.
7. **Submit**: Submit the final, production-grade code.
