# Developer Scripts

This directory contains scripts for developers.

## Available Scripts

- `check_pydantic_v1.py`: Checks for Pydantic v1 syntax in the codebase.
- `check_shell_scripts.sh`: Checks shell scripts for common errors.
- `config.py`: Helper script for configuration management (details to be added).
- `download_models.py`: Downloads machine learning models needed for the `kte` package.
- `update-stubs.py`: A script for managing type stubs.

## Usage

These scripts are intended to be run via `hatch`. For example, to run the `download-models` script, you would use:

```bash
hatch run download-models
```
