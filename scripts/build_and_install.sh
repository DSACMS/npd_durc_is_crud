#!/bin/bash
# Script to build and install the package for testing

# Ensure we're in the project root directory
cd "$(dirname "$0")/.." || exit

# Clean up previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
echo "Building the package..."
python setup.py sdist bdist_wheel

# Install the package in development mode
echo "Installing the package in development mode..."
pip install -e .

echo "Done! The package is now installed in development mode."
echo "You can run tests with: pytest"
echo "Or use the package in your Django project."
