#!/usr/bin/env bash
# Exit on error
set -e

# Version information
VERSION="1.0.0"

# Parse command line arguments
DRY_RUN=false
for arg in "$@"; do
  case $arg in
    -d|--dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      # Unknown option
      ;;
  esac
done

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
    # First, convert to Windows path format with backslashes
    path=$(echo "$path" | sed 's/\//\\/g')
    # Then ensure proper quoting
    echo "\"$path\""
  else
    # For Linux/macOS, return as is but with quotes for safety
    echo "\"$path\""
  fi
}

# Start timing the build process
SECONDS=0

# Define platform-specific output file names according to niuzhirui-server conventions
if [ "$IS_MACOS" = true ]; then
  BUILD_NAME="llm_server_macos-${VERSION}"
  FINAL_FILENAME="llm_server_macos-${VERSION}"
elif [ "$IS_WINDOWS" = true ]; then
  BUILD_NAME="llm_server_windows-${VERSION}"
  FINAL_FILENAME="llm_server_windows-${VERSION}.exe"
else
  BUILD_NAME="llm_server_linux-${VERSION}"
  FINAL_FILENAME="llm_server_linux-${VERSION}"
fi

# This script builds a standalone directory application instead of a single compressed file.
# Benefits:
# - Faster build time (no compression)
# - Faster startup time (no extraction needed at runtime)
# - Easier debugging (files are accessible)
# - Easier to update individual components

echo "Building standalone AutoByteus Server v${VERSION} (directory-based)..."
echo "Using build name: $BUILD_NAME"
if [ "$DRY_RUN" = true ]; then
  echo "DRY RUN MODE: Will show commands without executing them."
  echo "==============================================================="
fi

# Create output directory if it doesn't exist
OUTPUT_DIR="dist/$BUILD_NAME"
if [ "$DRY_RUN" = true ]; then
  echo "[DRY RUN] Would create directory: $OUTPUT_DIR"
else
  mkdir -p $OUTPUT_DIR
fi

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
echo "Locating dependency files (alembic, resources, playwright.sh, mistral_common data, anthropic tokenizer, etc.)..."

# Process dependency output
DEPENDENCY_ARGS_ARRAY=()

if [ "$IS_WINDOWS" = true ]; then
  # For Windows, use a temporary file approach which is more compatible with Git Bash
  TEMP_FILE="temp_dependencies.txt"
  python copy_dependencies_one_file.py > "$TEMP_FILE"
  
  CAPTURE=false
  while IFS= read -r line; do
    if [[ "$line" == "NUITKA_DEPENDENCY_ARGS_START" ]]; then
      CAPTURE=true
      continue
    elif [[ "$line" == "NUITKA_DEPENDENCY_ARGS_END" ]]; then
      CAPTURE=false
      continue
    fi
    
    if [ "$CAPTURE" = true ]; then
      DEPENDENCY_ARGS_ARRAY+=("$line")
    fi
  done < "$TEMP_FILE"
  
  # Clean up temporary file
  rm "$TEMP_FILE"
else
  # For Linux/macOS, use the JSON format (original approach)
  DEPENDENCY_OUTPUT=$(python copy_dependencies_one_file.py)
  DEPENDENCY_ARGS=$(echo "$DEPENDENCY_OUTPUT" | grep "NUITKA_DEPENDENCY_ARGS" | cut -d'=' -f2-)
  
  # Parse the JSON array
  readarray -t DEPENDENCY_ARGS_ARRAY < <(echo "$DEPENDENCY_ARGS" | python -c "import json, sys; [print(arg) for arg in json.load(sys.stdin)]")
fi

# Debug output to see what was captured
echo "Found ${#DEPENDENCY_ARGS_ARRAY[@]} dependency arguments."

# Build the Nuitka command
NUITKA_COMMAND="python -m nuitka \
    --standalone \
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

# Add macOS-specific options when running on macOS
if [ "$IS_MACOS" = true ]; then
  echo "Adding macOS-specific build options..."
  NUITKA_COMMAND="$NUITKA_COMMAND --macos-create-app-bundle"
fi

# Add Windows-specific options when running on Windows
if [ "$IS_WINDOWS" = true ]; then
  echo "Adding Windows-specific build options..."
  # Windows doesn't need special flags like macOS, but we might add them in the future
fi

# Add the remaining options
NUITKA_COMMAND="$NUITKA_COMMAND \
    --output-dir=$OUTPUT_DIR \
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
fi

# Copy application dependencies
if [ "$DRY_RUN" = true ]; then
  echo "[DRY RUN] Would copy application dependencies to the app.dist directory..."
else
  echo "Copying application dependencies to the app.dist directory..."
  python copy_dependencies_standalone.py "$OUTPUT_DIR" "$VERSION"
  if [ $? -ne 0 ]; then
      echo "Error: Failed to copy required dependencies."
      exit 1
  fi
fi

# Create a zip file of the application
if [ "$DRY_RUN" = true ]; then
  echo "[DRY RUN] Would create zip file of the application..."
else
  echo "Creating zip file of the application..."
  
  # Create niuzhirui-server_dev/resources/llm_server directory if it doesn't exist
  NIUZHIRUI_DIR="../niuzhirui-server_dev/resources/llm_server"
  mkdir -p "$NIUZHIRUI_DIR"
  
  ZIP_FILE="$NIUZHIRUI_DIR/$FINAL_FILENAME.zip"

  # Remove previous zip file if it exists
  if [ -f "$ZIP_FILE" ]; then
      echo "Removing previous zip file..."
      rm "$ZIP_FILE"
  fi

  # Create the zip file
  echo "Creating zip file at $ZIP_FILE..."
  cd dist
  zip -r "$ZIP_FILE" $(basename $OUTPUT_DIR)/app.dist
  cd ..

  # Verify the zip file was created
  if [ -f "$ZIP_FILE" ]; then
      echo "Successfully created $ZIP_FILE"
      echo "File size: $(du -h $ZIP_FILE | cut -f1)"
      
      # Create config file for the download
      CONFIG_FILE="$ZIP_FILE.config.json"
      echo "{" > "$CONFIG_FILE"
      echo "  \"distribution_channel\": \"all\"," >> "$CONFIG_FILE"
      echo "  \"description\": \"AutoByteus Server $VERSION Standalone for $([ "$IS_MACOS" = true ] && echo "macOS" || [ "$IS_WINDOWS" = true ] && echo "Windows" || echo "Linux")\"" >> "$CONFIG_FILE"
      echo "}" >> "$CONFIG_FILE"
      echo "Created config file: $CONFIG_FILE"
  else
      echo "Error: Failed to create zip file"
      exit 1
  fi
fi

if [ "$DRY_RUN" = true ]; then
  echo "[DRY RUN] Build process complete (simulation only)"
  echo "[DRY RUN] To execute the actual build, run without the --dry-run flag"
else
  # Determine the correct directory name based on platform
  if [ "$IS_MACOS" = true ]; then
    echo "Build complete! The standalone application is in: $OUTPUT_DIR/app.dist (or as an .app bundle)"
    echo "A zip file has been created at $ZIP_FILE for distribution"
    echo "To run the application, execute the app bundle or: $OUTPUT_DIR/app.dist/app"
  elif [ "$IS_WINDOWS" = true ]; then
    echo "Build complete! The standalone application is in: $OUTPUT_DIR/app.dist"
    echo "A zip file has been created at $ZIP_FILE for distribution"
    echo "To run the application, execute: $OUTPUT_DIR/app.dist/app.exe"
  else
    echo "Build complete! The standalone application is in: $OUTPUT_DIR/app.dist"
    echo "A zip file has been created at $ZIP_FILE for distribution"
    echo "To run the application, execute: $OUTPUT_DIR/app.dist/app"
  fi
  echo "Configuration files, alembic migrations, playwright dependencies, mistral_common data, anthropic tokenizer, and required resources have been included with the executable."
fi

# Calculate and display the total build time in minutes
duration=$SECONDS
minutes=$(awk "BEGIN {printf \"%.2f\", $duration/60}")
echo "Total build time: $minutes minutes"
