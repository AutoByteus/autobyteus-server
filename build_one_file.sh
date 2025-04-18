#!/usr/bin/env bash
# Exit on error
set -e

# Version information
VERSION="1.0.0"

# Process command line arguments
DRY_RUN=false
CUSTOM_TEMPDIR="{CACHE_DIR}/autobyteus"  # Default to platform-specific cache directory with a subdirectory

# Show help information
show_help() {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  -d, --dry-run             Show the Nuitka command without executing it"
  echo "  --tempdir=<path>          Specify a custom directory for extracted files"
  echo "                            (default: '{CACHE_DIR}/autobyteus', e.g., ~/.cache/autobyteus on Linux)"
  echo "  -h, --help                Show this help message"
  echo
  echo "Examples:"
  echo "  $0 --tempdir={TEMP}/{PID}  Use system temp with unique process ID"
  echo "  $0 --tempdir={CACHE_DIR}/custom_path  Use cache dir with custom subdirectory"
}

# Parse command line arguments
for arg in "$@"; do
  case $arg in
    -h|--help)
    show_help
    exit 0
    ;;
    -d|--dry-run)
    DRY_RUN=true
    shift
    ;;
    --tempdir=*)
    CUSTOM_TEMPDIR="${arg#*=}"
    shift
    ;;
  esac
done

# Start timing the build process
SECONDS=0

# Detect OS type
OS_TYPE=$(uname -s)
IS_MACOS=false
IS_WINDOWS=false

if [ "$OS_TYPE" = "Darwin" ]; then
  IS_MACOS=true
  echo "Detected macOS environment."
elif [[ "$OS_TYPE" == MINGW* ]] || [[ "$OS_TYPE" == MSYS* ]] || [[ "$OS_TYPE" == CYGWIN* ]]; then
  IS_WINDOWS=true
  echo "Detected Windows environment."
else
  echo "Detected Linux environment."
fi

# Function to normalize paths for Windows Git Bash
normalize_path() {
  local path="$1"
  
  if [ "$IS_WINDOWS" = true ]; then
    # For Windows, convert path separators and ensure proper format for Python/Nuitka
    path=$(echo "$path" | sed 's/\//\\/g')
    echo "\"$path\""
  else
    # For Linux/macOS, return as is but with quotes for safety
    echo "\"$path\""
  fi
}

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

# Define platform-specific output file names
if [ "$IS_MACOS" = true ]; then
  OUTPUT_FILENAME="autobyteus_server-macos-${VERSION}"
  FINAL_FILENAME="autobyteus_server-macos-${VERSION}"
elif [ "$IS_WINDOWS" = true ]; then
  OUTPUT_FILENAME="autobyteus_server-windows-${VERSION}"
  FINAL_FILENAME="autobyteus_server-windows-${VERSION}.exe"
else
  OUTPUT_FILENAME="autobyteus_server-linux-${VERSION}"
  FINAL_FILENAME="autobyteus_server-linux-${VERSION}"
fi

echo "Using output filename: $OUTPUT_FILENAME"

# Set up dependencies - only needed for Linux builds
if [ "$DRY_RUN" = true ]; then
  if [ "$IS_MACOS" = false ] && [ "$IS_WINDOWS" = false ]; then
    echo "[DRY RUN] Would install Conda dependencies for static linking on Linux..."
  else
    echo "[DRY RUN] Skipping Conda dependencies installation (not needed on macOS/Windows)..."
  fi
else
  if [ "$IS_MACOS" = false ] && [ "$IS_WINDOWS" = false ]; then
    echo "Installing Conda dependencies for static linking on Linux..."
    conda install conda-forge::gcc
    conda install -c conda-forge libpython-static -y
    if [ $? -ne 0 ]; then
      echo "Error: Failed to install libpython-static. Ensure 'conda-forge' is added as a channel (run 'conda config --add channels conda-forge') and try again."
      exit 1
    fi
  else
    echo "Skipping Conda dependencies installation (not needed on macOS/Windows)..."
  fi
fi

if [ "$DRY_RUN" = true ]; then
  echo "[DRY RUN] Would install Python dependencies..."
else
  echo "Installing Python dependencies..."
  pip install -r requirements.txt
fi

# Find specific dependency files using the copy_dependencies_one_file.py script
echo "Locating dependency files (playwright.sh, mistral_common data, anthropic tokenizer, etc.)..."

# Run the Python script to generate dependencies and write them to a file
echo "Running Python script to find dependencies..."
python copy_dependencies_one_file.py

# Initialize dependency array
DEPENDENCY_ARGS_ARRAY=()

# Simple direct file approach - read the dependency arguments from the file
DEPENDENCY_FILE="nuitka_dependencies.txt"
if [ -f "$DEPENDENCY_FILE" ]; then
    echo "Reading dependency arguments from $DEPENDENCY_FILE..."
    
    # Debug: Show the content of the dependency file
    echo "Debug: Contents of $DEPENDENCY_FILE:"
    cat "$DEPENDENCY_FILE"
    echo "End of $DEPENDENCY_FILE contents"
    
    # Read the file line by line
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip empty lines
        if [ -n "$line" ]; then
            echo "Debug: Adding argument: $line"
            DEPENDENCY_ARGS_ARRAY+=("$line")
        fi
    done < "$DEPENDENCY_FILE"
else
    echo "Warning: Dependency file $DEPENDENCY_FILE not found."
fi

# Debug output to see what was captured
echo "Found ${#DEPENDENCY_ARGS_ARRAY[@]} dependency arguments."
if [ ${#DEPENDENCY_ARGS_ARRAY[@]} -gt 0 ]; then
    echo "Debug: First argument: ${DEPENDENCY_ARGS_ARRAY[0]}"
    echo "Debug: Last argument: ${DEPENDENCY_ARGS_ARRAY[${#DEPENDENCY_ARGS_ARRAY[@]}-1]}"
fi

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
    --include-package=netifaces \
    --include-package=playwright"

# Add the dependency arguments
for dep_arg in "${DEPENDENCY_ARGS_ARRAY[@]}"; do
    NUITKA_COMMAND="$NUITKA_COMMAND $dep_arg"
done

# Add macOS-specific options when running on macOS
if [ "$IS_MACOS" = true ]; then
  echo "Adding macOS-specific build options..."
  NUITKA_COMMAND="$NUITKA_COMMAND --macos-create-app-bundle"
fi

# Add Windows-specific options when running on Windows
if [ "$IS_WINDOWS" = true ]; then
  echo "Adding Windows-specific build options..."
fi

# Add custom tempdir specification if provided
echo "Using extraction directory: $CUSTOM_TEMPDIR"
NUITKA_COMMAND="$NUITKA_COMMAND --onefile-tempdir-spec=\"$CUSTOM_TEMPDIR\""

# Add the remaining options
NUITKA_COMMAND="$NUITKA_COMMAND \
    --onefile \
    --output-dir=$OUTPUT_DIR \
    --output-filename=$OUTPUT_FILENAME \
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
  
  # Determine the likely executable path based on platform
  if [ "$IS_MACOS" = true ]; then
    if [ -d "$OUTPUT_DIR/$OUTPUT_FILENAME.app" ]; then
      BUILT_FILE="$OUTPUT_DIR/$OUTPUT_FILENAME.app"
      echo "Found built macOS app bundle: $BUILT_FILE"
    else
      BUILT_FILE="$OUTPUT_DIR/$OUTPUT_FILENAME.bin"
      echo "Found built macOS executable: $BUILT_FILE"
    fi
  elif [ "$IS_WINDOWS" = true ]; then
    BUILT_FILE="$OUTPUT_DIR/$OUTPUT_FILENAME.exe"
    echo "Found built Windows executable: $BUILT_FILE"
  else
    if [ -f "$OUTPUT_DIR/$OUTPUT_FILENAME.bin" ]; then
      BUILT_FILE="$OUTPUT_DIR/$OUTPUT_FILENAME.bin"
    else
      BUILT_FILE="$OUTPUT_DIR/$OUTPUT_FILENAME"
    fi
    echo "Found built Linux executable: $BUILT_FILE"
  fi
  
  echo "Build complete! The executable has been built."
  
  echo "Extraction directory set to: $CUSTOM_TEMPDIR"
  if [[ "$CUSTOM_TEMPDIR" == "{CACHE_DIR}/autobyteus" ]]; then
    echo "The application will extract to the platform-specific cache directory with 'autobyteus' subdirectory:"
    echo "  - Windows: %LOCALAPPDATA%\\autobyteus (e.g., C:\\Users\\<Username>\\AppData\\Local\\autobyteus)"
    echo "  - Linux: ~/.cache/autobyteus"
    echo "  - macOS: ~/Library/Caches/autobyteus"
  elif [[ "$CUSTOM_TEMPDIR" == *"{TEMP}"* ]]; then
    echo "The application will extract to the system temporary directory (location varies by OS)."
    if [[ "$CUSTOM_TEMPDIR" == *"{PID}"* ]]; then
      echo "Files will be cleaned up automatically when the application exits."
    fi
  fi
  
  echo "Note: The executable contains Playwright dependencies, mistral_common data, and anthropic tokenizer."
  echo "Make sure to have the following files in the same directory where you run the executable:"
  echo "  - .env (environment configuration)"
  echo "  - logging_config.ini (logging configuration)"
  echo "  - alembic.ini (database migration configuration)"
  echo "  - download/ (directory for application downloads like plantuml.jar)"
  echo "  - alembic/ (directory for database migrations)"
  
  # Calculate and display the total build time in minutes
  duration=$SECONDS
  minutes=$(awk "BEGIN {printf \"%.2f\", $duration/60}")
  echo "Total build time: $minutes minutes"
fi
