#!/usr/bin/env bash
# Simple deployment script for AutoByteus Server
# Copies configurations from the autobyteus-server folder and the built executable

# Exit on error
set -e

# Default values
DRY_RUN=false

# Detect OS type
OS_TYPE=$(uname -s)
IS_MACOS=false
if [ "$OS_TYPE" = "Darwin" ]; then
  IS_MACOS=true
  echo "Detected macOS environment."
else
  echo "Detected Linux environment."
fi

# Function to normalize paths that works on both macOS and Linux
normalize_path() {
    local path="$1"
    
    # If the directory exists, we can use cd and pwd to get absolute path
    if [ -d "$path" ]; then
        local old_pwd=$(pwd)
        cd "$path" > /dev/null
        local abs_path=$(pwd)
        cd "$old_pwd" > /dev/null
        echo "$abs_path"
    else
        # For non-existent directories
        if [ "$IS_MACOS" = true ]; then
            # On macOS, if the directory doesn't exist, construct the absolute path
            if [[ "$path" = /* ]]; then
                # Path already absolute
                echo "$path"
            else
                # Make relative path absolute
                echo "$(pwd)/$path"
            fi
        else
            # On Linux, we can use realpath -m
            realpath -m "$path"
        fi
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -d|--dry-run)
        DRY_RUN=true
        shift # past argument
        ;;
        *)    # unknown option or target directory
        # If first positional parameter and not starting with -, treat as target dir
        if [[ $# -eq $OPTIND && ! $key == -* ]]; then
            TARGET_DIR="$key"
        fi
        shift # past argument
        ;;
    esac
done

# Banner
echo "=================================================="
echo "AutoByteus Server - Deployment"
if [ "$DRY_RUN" = true ]; then
    echo "MODE: DRY RUN (no changes will be made)"
fi
echo "=================================================="
echo "This script copies configurations and the executable to the target directory."
echo

# Get target directory from command line or prompt
if [ -z "$TARGET_DIR" ]; then
    read -p "Enter deployment target directory: " TARGET_DIR
    
    # Validate input
    if [ -z "$TARGET_DIR" ]; then
        echo "Error: Target directory is required."
        exit 1
    fi
fi

# Normalize paths
SOURCE_DIR="$(pwd)"
TARGET_DIR=$(normalize_path "$TARGET_DIR")

echo "Source directory: $SOURCE_DIR"
echo "Target directory: $TARGET_DIR"
if [ "$DRY_RUN" = true ]; then
    echo "Dry run: No changes will be made"
fi
echo

# Check if executable exists
if [ "$IS_MACOS" = true ]; then
    # On macOS, check for both .bin file and .app bundle
    EXECUTABLE_SOURCE=""
    if [ -f "$SOURCE_DIR/dist/autobyteus_server" ]; then
        EXECUTABLE_SOURCE="$SOURCE_DIR/dist/autobyteus_server"
    elif [ -f "$SOURCE_DIR/dist/autobyteus_server.bin" ]; then
        EXECUTABLE_SOURCE="$SOURCE_DIR/dist/autobyteus_server.bin"
    elif [ -d "$SOURCE_DIR/dist/autobyteus_server.app" ]; then
        echo "Found macOS app bundle at $SOURCE_DIR/dist/autobyteus_server.app"
        echo "Warning: Deploying macOS app bundles is not fully supported in this script."
        echo "It's recommended to deploy the .bin file instead."
        EXECUTABLE_SOURCE=""
    fi
else
    # On Linux, check for the standard executable
    EXECUTABLE_SOURCE="$SOURCE_DIR/dist/autobyteus_server"
    if [ ! -f "$EXECUTABLE_SOURCE" ]; then
        # Also check for .bin extension as a fallback
        EXECUTABLE_SOURCE="$SOURCE_DIR/dist/autobyteus_server.bin"
    fi
fi

if [ -z "$EXECUTABLE_SOURCE" ] || [ ! -f "$EXECUTABLE_SOURCE" ]; then
    echo "Error: Executable not found in dist directory"
    echo "Please build it first with ./build_one_file.sh"
    exit 1
fi

# Function to recursively list all files in a directory
list_files_in_dir() {
    local dir="$1"
    local prefix="$2"
    
    if [ ! -d "$dir" ]; then
        return
    fi
    
    # List all entries in the directory
    if [ "$IS_MACOS" = true ]; then
        # macOS find has different syntax
        local entries=$(find "$dir" -type f | sort)
    else
        local entries=$(find "$dir" -type f | sort)
    fi
    
    for entry in $entries; do
        # Remove source directory prefix for cleaner output
        local rel_path="${entry#$SOURCE_DIR/}"
        echo "${prefix}$rel_path"
    done
}

# Function to create directory with dry run support
create_directory() {
    local dir="$1"
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would create directory: $dir"
    else
        mkdir -p "$dir"
        echo "✓ Created: $dir"
    fi
}

# Function to copy file with dry run support
copy_file() {
    local src="$1"
    local dst="$2"
    local desc="$3"
    
    if [ ! -f "$src" ]; then
        echo "Warning: $desc not found in source directory. Skipping."
        return
    fi
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would copy file: $desc"
    else
        # Create directory if it doesn't exist
        mkdir -p "$(dirname "$dst")"
        cp -p "$src" "$dst"
        echo "✓ Copied: $desc"
    fi
}

# Function to copy directory with dry run support
copy_directory() {
    local src="$1"
    local dst="$2"
    local desc="$3"
    
    if [ ! -d "$src" ] || [ -z "$(ls -A "$src" 2>/dev/null)" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "[DRY RUN] Would create empty directory: $dst"
        else
            mkdir -p "$dst"
            echo "Warning: $desc directory not found or empty in source. Created empty directory."
        fi
        return
    fi
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would copy directory: $desc"
        echo "[DRY RUN] Files that would be copied:"
        list_files_in_dir "$src" "  - "
        echo
    else
        mkdir -p "$dst"
        cp -rp "$src"/* "$dst"/ 2>/dev/null || true
        echo "✓ Copied: $desc directory"
    fi
}

# Create target directory if it doesn't exist
if [ ! -d "$TARGET_DIR" ] && [ "$DRY_RUN" = false ]; then
    echo "Creating target directory: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create target directory. Please check permissions."
        exit 1
    fi
elif [ ! -d "$TARGET_DIR" ] && [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] Would create target directory: $TARGET_DIR"
fi

echo "Starting deployment process..."
echo

# Copy configuration files if they exist
echo "Copying configuration files..."
copy_file "$SOURCE_DIR/.env" "$TARGET_DIR/.env" ".env"
copy_file "$SOURCE_DIR/logging_config.ini" "$TARGET_DIR/logging_config.ini" "logging_config.ini"
copy_file "$SOURCE_DIR/alembic.ini" "$TARGET_DIR/alembic.ini" "alembic.ini"

# Create/copy directories
echo
echo "Creating/copying directories..."

# Create logs directory
create_directory "$TARGET_DIR/logs"

# Create data directory
create_directory "$TARGET_DIR/data"

# Copy resources directory if it exists
copy_directory "$SOURCE_DIR/resources" "$TARGET_DIR/resources" "resources"

# Copy alembic directory if it exists
copy_directory "$SOURCE_DIR/alembic" "$TARGET_DIR/alembic" "alembic"

# Copy data directory if it exists
copy_directory "$SOURCE_DIR/data" "$TARGET_DIR/data" "data"

# Copy the executable
echo
echo "Copying executable..."
if [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] Would copy executable: autobyteus_server"
    echo "[DRY RUN] Would set executable permissions on: $TARGET_DIR/autobyteus_server"
else
    cp "$EXECUTABLE_SOURCE" "$TARGET_DIR/autobyteus_server"
    chmod +x "$TARGET_DIR/autobyteus_server"
    echo "✓ Copied and set executable permissions: autobyteus_server"
fi

# Summary
echo
echo "=================================================="
if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN COMPLETED - No changes were made"
else
    echo "Deployment completed successfully!"
fi
echo "=================================================="
echo "Target directory: $TARGET_DIR"
echo
if [ "$DRY_RUN" = false ]; then
    echo "To run the server:"
    echo "  cd \"$TARGET_DIR\""
    echo "  ./autobyteus_server"
fi
echo "=================================================="
