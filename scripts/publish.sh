#!/bin/bash
# Script to publish the package to PyPI

# Ensure we're in the project root directory
cd "$(dirname "$0")/.." || exit

# Clean up previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
echo "Building the package..."
python setup.py sdist bdist_wheel

# Check the package
echo "Checking the package with twine..."
twine check dist/*

# Ask for confirmation before publishing
read -p "Do you want to publish to PyPI? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Publishing to PyPI..."
    twine upload dist/*
    echo "Package published successfully!"
else
    echo "Publishing cancelled."
fi
