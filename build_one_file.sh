#!/bin/bash
# Exit on error
set -e

# Version information
VERSION="1.0"

# Process command line arguments
DRY_RUN=false
for arg in "$@"; do
  case $arg in
    -d|--dry-run)
    DRY_RUN=true
    shift
    ;;
  esac
done

# Start timing the build process
SECONDS=0

# This script builds a single executable file
if [ "$DRY_RUN" = true ]; then
  echo "DRY RUN MODE: Will show the Nuitka command without executing it."
  echo "==============================================================="
else
  echo "Building onefile AutoByteus Server v${VERSION} application..."
fi

# Define output directory
OUTPUT_DIR="dist"
mkdir -p $OUTPUT_DIR

# Set up dependencies (even in dry run, as we need the paths)
if [ "$DRY_RUN" = true ]; then
  echo "[DRY RUN] Would install Conda dependencies for static linking..."
else
  echo "Installing Conda dependencies for static linking..."
  conda install conda-forge::gcc
  conda install -c conda-forge libpython-static -y
  if [ $? -ne 0 ]; then
      echo "Error: Failed to install libpython-static. Ensure 'conda-forge' is added as a channel (run 'conda config --add channels conda-forge') and try again."
      exit 1
  fi
fi

if [ "$DRY_RUN" = true ]; then
  echo "[DRY RUN] Would install Python dependencies..."
else
  echo "Installing Python dependencies..."
  pip install -r requirements.txt
fi

# Find specific dependency files using the copy_dependencies_one_file.py script
echo "Locating dependency files (alembic, resources, playwright.sh, mistral_common data, anthropic tokenizer, etc.)..."
DEPENDENCY_OUTPUT=$(python copy_dependencies_one_file.py)
DEPENDENCY_ARGS=$(echo "$DEPENDENCY_OUTPUT" | grep "NUITKA_DEPENDENCY_ARGS" | cut -d'=' -f2-)

# Parse the JSON array of dependency arguments
readarray -t DEPENDENCY_ARGS_ARRAY < <(echo "$DEPENDENCY_ARGS" | python -c "import json, sys; [print(arg) for arg in json.load(sys.stdin)]")

# Build the Nuitka command
NUITKA_COMMAND="python -m nuitka \
    --follow-imports \
    --include-module=app \
    --include-package=uvicorn \
    --include-package=fastapi \
    --include-package=starlette \
    --include-package=typing_extensions \
    --include-package=strawberry \
    --include-package=watchfiles \
    --include-package=dotenv \
    --include-package=rapidfuzz \
    --include-package=pathspec \
    --include-package=repository_sqlalchemy \
    --include-package=repository_mongodb \
    --include-package=alembic \
    --include-package=watchdog \
    --include-package=multipart \
    --include-package=anthropic \
    --include-package=autobyteus \
    --include-package=mistral_common \
    --include-package=playwright"

# Add the dependency arguments
for dep_arg in "${DEPENDENCY_ARGS_ARRAY[@]}"; do
    NUITKA_COMMAND="$NUITKA_COMMAND $dep_arg"
done

# Add the remaining options
NUITKA_COMMAND="$NUITKA_COMMAND \
    --onefile \
    --output-dir=$OUTPUT_DIR \
    --output-filename=autobyteus_server \
    --assume-yes-for-downloads \
    --lto=no \
    --company-name=\"AutoByteus\" \
    --product-name=\"AutoByteus Server\" \
    --file-version=\"${VERSION}\" \
    --product-version=\"${VERSION}\" \
    autobyteus_server/app.py"

if [ "$DRY_RUN" = true ]; then
  echo "=========================================="
  echo "NUITKA COMMAND THAT WOULD BE EXECUTED:"
  echo "=========================================="
  echo "$NUITKA_COMMAND"
  echo "=========================================="
  echo "[DRY RUN] Build command displayed but not executed."
else
  echo "Starting Nuitka build process..."
  echo "Running command: $NUITKA_COMMAND"
  eval "$NUITKA_COMMAND"
  
  echo "Build complete! The executable should be in the $OUTPUT_DIR directory named 'autobyteus_server.bin' or 'autobyteus_server.exe' depending on your OS."
  echo "Note: All required resources, alembic files, playwright dependencies, mistral_common data, anthropic tokenizer, and configuration files have been packaged inside the executable."
  
  # Calculate and display the total build time in minutes
  duration=$SECONDS
  minutes=$(awk "BEGIN {printf \"%.2f\", $duration/60}")
  echo "Total build time: $minutes minutes"
fi

