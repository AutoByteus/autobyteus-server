#!/usr/bin/env bash
# Exit on error
set -e

# Version information
VERSION="1.0.0"

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

# Define platform-specific output file names according to niuzhirui-server conventions
if [ "$IS_MACOS" = true ]; then
  OUTPUT_FILENAME="llm_server_macos-${VERSION}"
  FINAL_FILENAME="llm_server_macos-${VERSION}"
elif [ "$IS_WINDOWS" = true ]; then
  OUTPUT_FILENAME="llm_server_windows-${VERSION}"
  FINAL_FILENAME="llm_server_windows-${VERSION}.exe"
else
  OUTPUT_FILENAME="llm_server_linux-${VERSION}"
  FINAL_FILENAME="llm_server_linux-${VERSION}"
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

# For Windows Git Bash, we need to run the Python script differently to handle paths correctly
if [ "$IS_WINDOWS" = true ]; then
  # Create a temporary script to fix path handling on Windows
  cat > fix_paths.py << 'EOF'
import json
import os
import sys

# Read the output from the original script
dependency_output = sys.stdin.read()

# Find the NUITKA_DEPENDENCY_ARGS line
for line in dependency_output.splitlines():
    if line.startswith("NUITKA_DEPENDENCY_ARGS="):
        # Extract the JSON array
        args_json = line[len("NUITKA_DEPENDENCY_ARGS="):]
        
        # Parse the JSON
        args_array = json.loads(args_json)
        
        # Fix each path
        fixed_args = []
        for arg in args_array:
            # Replace all backslashes with forward slashes for Nuitka
            arg = arg.replace('\\', '/')
            # Fix paths where separators were completely stripped
            arg = arg.replace('C:', 'C:/')
            fixed_args.append(arg)
        
        # Output the fixed args
        print(f"NUITKA_DEPENDENCY_ARGS={json.dumps(fixed_args)}")
        break
    else:
        print(line)
EOF

  DEPENDENCY_OUTPUT=$(python copy_dependencies_one_file.py | python fix_paths.py)
else
  DEPENDENCY_OUTPUT=$(python copy_dependencies_one_file.py)
fi

DEPENDENCY_ARGS=$(echo "$DEPENDENCY_OUTPUT" | grep "NUITKA_DEPENDENCY_ARGS" | cut -d'=' -f2-)

# Parse the JSON array of dependency arguments
if [ "$IS_WINDOWS" = true ]; then
  # On Windows Git Bash, use a different approach to handle the array
  readarray -t DEPENDENCY_ARGS_ARRAY < <(echo "$DEPENDENCY_ARGS" | python -c "import json, sys; [print(arg.replace('\"', '\\\"')) for arg in json.load(sys.stdin)]")
else
  readarray -t DEPENDENCY_ARGS_ARRAY < <(echo "$DEPENDENCY_ARGS" | python -c "import json, sys; [print(arg) for arg in json.load(sys.stdin)]")
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
  echo "[DRY RUN] Would copy built file to niuzhirui-server_dev for download."
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
  
  # Create niuzhirui-server_dev/resources/llm_server directory if it doesn't exist
  NIUZHIRUI_DIR="../niuzhirui-server_dev/resources/llm_server"
  mkdir -p "$NIUZHIRUI_DIR"
  
  # Copy the built file to niuzhirui-server_dev
  echo "Copying built file to $NIUZHIRUI_DIR/$FINAL_FILENAME for download..."
  
  if [[ "$BUILT_FILE" == *.app ]]; then
    # For macOS app bundle, create a zip archive
    echo "Creating zip archive of macOS app bundle..."
    (cd "$OUTPUT_DIR" && zip -r "${OUTPUT_FILENAME}.zip" "$(basename "$BUILT_FILE")")
    cp "$OUTPUT_DIR/${OUTPUT_FILENAME}.zip" "$NIUZHIRUI_DIR/$FINAL_FILENAME.zip"
    echo "Created and copied: $NIUZHIRUI_DIR/$FINAL_FILENAME.zip"
  else
    # For regular executables
    cp "$BUILT_FILE" "$NIUZHIRUI_DIR/$FINAL_FILENAME"
    echo "Copied: $NIUZHIRUI_DIR/$FINAL_FILENAME"
  fi
  
  # Create config file for the download
  CONFIG_FILE="$NIUZHIRUI_DIR/$FINAL_FILENAME.config.json"
  echo "{" > "$CONFIG_FILE"
  echo "  \"distribution_channel\": \"all\"," >> "$CONFIG_FILE"
  echo "  \"description\": \"AutoByteus Server $VERSION for $([ "$IS_MACOS" = true ] && echo "macOS" || [ "$IS_WINDOWS" = true ] && echo "Windows" || echo "Linux")\"" >> "$CONFIG_FILE"
  echo "}" >> "$CONFIG_FILE"
  echo "Created config file: $CONFIG_FILE"
  
  echo "Build complete! The executable has been built and copied to the niuzhirui-server_dev directory."
  echo "Note: The executable contains Playwright dependencies, mistral_common data, and anthropic tokenizer."
  echo "Make sure to have the following files in the same directory where you run the executable:"
  echo "  - .env (environment configuration)"
  echo "  - logging_config.ini (logging configuration)"
  echo "  - alembic.ini (database migration configuration)"
  echo "  - resources/ (directory for application resources)"
  echo "  - alembic/ (directory for database migrations)"
  
  # Calculate and display the total build time in minutes
  duration=$SECONDS
  minutes=$(awk "BEGIN {printf \"%.2f\", $duration/60}")
  echo "Total build time: $minutes minutes"
fi
