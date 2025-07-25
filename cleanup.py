#!/usr/bin/env python3
"""
Cleanup script for the book-analyse project.
Removes old files, temporary files, and generated artifacts.
"""

import argparse
import os
import shutil
from pathlib import Path


class CleanupTool:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def cleanup_python_cache(self):
        """Remove Python cache files."""
        print("🧹 Cleaning Python cache files...")

        # Remove __pycache__ directories
        for pycache in self.project_root.rglob("__pycache__"):
            if pycache.is_dir():
                shutil.rmtree(pycache)
                print(f"  Removed: {pycache}")

        # Remove .pyc files
        for pyc_file in self.project_root.rglob("*.pyc"):
            pyc_file.unlink()
            print(f"  Removed: {pyc_file}")

    def cleanup_test_artifacts(self):
        """Remove test artifacts and temporary files."""
        print("🧹 Cleaning test artifacts...")

        # Remove .pytest_cache
        pytest_cache = self.project_root / ".pytest_cache"
        if pytest_cache.exists():
            shutil.rmtree(pytest_cache)
            print(f"  Removed: {pytest_cache}")

        # Remove coverage reports (optional)
        htmlcov = self.project_root / "tests" / "htmlcov"
        if htmlcov.exists():
            shutil.rmtree(htmlcov)
            print(f"  Removed: {htmlcov}")

        # Remove .coverage file
        coverage_file = self.project_root / ".coverage"
        if coverage_file.exists():
            coverage_file.unlink()
            print(f"  Removed: {coverage_file}")

    def cleanup_build_artifacts(self):
        """Remove build artifacts."""
        print("🧹 Cleaning build artifacts...")

        # Remove dist directory
        dist_dir = self.project_root / "dist"
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
            print(f"  Removed: {dist_dir}")

        # Remove build directory
        build_dir = self.project_root / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)
            print(f"  Removed: {build_dir}")

        # Remove *.egg-info directories
        for egg_info in self.project_root.glob("*.egg-info"):
            if egg_info.is_dir():
                shutil.rmtree(egg_info)
                print(f"  Removed: {egg_info}")

    def cleanup_temp_files(self):
        """Remove temporary files."""
        print("🧹 Cleaning temporary files...")

        # Remove temporary test files
        temp_files = [
            "test_input.txt",
            "test_output.json",
            "temp_*.txt",
            "temp_*.json",
            "temp_*.md",
        ]

        for pattern in temp_files:
            for temp_file in self.project_root.glob(pattern):
                if temp_file.exists():
                    temp_file.unlink()
                    print(f"  Removed: {temp_file}")

    def cleanup_ide_files(self):
        """Remove IDE-specific files."""
        print("🧹 Cleaning IDE files...")

        # Remove .vscode directory
        vscode_dir = self.project_root / ".vscode"
        if vscode_dir.exists():
            shutil.rmtree(vscode_dir)
            print(f"  Removed: {vscode_dir}")

        # Remove .idea directory
        idea_dir = self.project_root / ".idea"
        if idea_dir.exists():
            shutil.rmtree(idea_dir)
            print(f"  Removed: {idea_dir}")

    def cleanup_all(self):
        """Run all cleanup operations."""
        print("🚀 Starting cleanup process...")
        print(f"Project root: {self.project_root}")
        print()

        self.cleanup_python_cache()
        print()

        self.cleanup_test_artifacts()
        print()

        self.cleanup_build_artifacts()
        print()

        self.cleanup_temp_files()
        print()

        self.cleanup_ide_files()
        print()

        print("✅ Cleanup completed successfully!")


def main():
    parser = argparse.ArgumentParser(description="Cleanup tool for book-analyse project")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent,
        help="Project root directory (default: script directory)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be cleaned without actually removing files"
    )

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be removed")
        print()

    cleanup = CleanupTool(args.project_root)
    cleanup.cleanup_all()


if __name__ == "__main__":
    main()
