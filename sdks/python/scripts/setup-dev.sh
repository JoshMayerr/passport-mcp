#!/bin/bash
set -e

# Create and activate a virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip and install the package in editable mode with dev dependencies
python -m pip install --upgrade pip
pip install -e ".[dev]"

echo "Development environment setup complete!"
echo "To activate the virtual environment, run: source .venv/bin/activate"
