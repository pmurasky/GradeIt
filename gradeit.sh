#!/bin/bash
# Convenience script to run GradeIt using the virtual environment

# Ensure we are in the project root
cd "$(dirname "$0")"

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Please run setup first."
    exit 1
fi

# Run the CLI module
PYTHONPATH=src .venv/bin/python -m gradeit.cli "$@"
