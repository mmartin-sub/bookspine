import importlib.util

import pytest

OPTIONAL_MODULES = ["keybert", "sentence_transformers"]


def pytest_runtest_setup(item):
    if "optional" in item.keywords:
        for module in OPTIONAL_MODULES:
            if importlib.util.find_spec(module) is None:
                pytest.skip(f"Skipping optional test, missing dependency: {module}")
