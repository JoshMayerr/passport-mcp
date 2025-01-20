#!/bin/bash
set -e

# Ensure we're in the correct directory
cd "$(dirname "$0")/.."

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m pip install --upgrade build
python -m build

# Upload to PyPI
python -m pip install --upgrade twine
python -m twine upload dist/*
