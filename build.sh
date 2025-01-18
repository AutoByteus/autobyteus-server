#!/bin/bash
# Install PyInstaller
pip install pyinstaller

# Clean previous builds
rm -rf build dist

# Build the executable
pyinstaller autobyteus.spec

echo "Build complete! Executable is in the dist directory."
