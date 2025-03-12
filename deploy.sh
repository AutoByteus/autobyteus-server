#!/usr/bin/env bash
# Simple deployment script for AutoByteus Server
# Copies configurations from the autobyteus-server folder and the built executable

# Exit on error
set -e

# Default values
DRY_RUN=false
VERSION="1.0.0"  # Default version, can be overridden

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

# Function to normalize paths that works on both macOS, Linux and Windows
normalize_path() {
    local path="$1"
    
    if [ "$IS_WINDOWS" = true ]; then
        # For Windows, handle paths differently
        # First, check if the path exists
        if [ -d "$path" ]; then
            # For existing directories, use Windows-style realpath
            local old_pwd=$(pwd)
            cd "$path" > /dev/null
            local abs_path=$(pwd -W 2>/dev/null || pwd)  # Try Windows format first
            cd "$old_pwd" > /dev/null
            echo "$abs_path"
        else
            # For non-existent paths, construct manually
            if [[ "$path" == /* ]]; then
                # Convert /c/Users/... to C:/Users/...
                local drive_letter=$(echo "$path" | cut -c2)
                if [[ "$drive_letter" =~ [a-zA-Z] ]]; then
                    local rest_of_path=$(echo "$path" | cut -c4-)
                    echo "${drive_letter^^}:/$rest_of_path"
                else
                    # Not a drive path, just normalize slashes
                    echo "$path" | sed 's/\//\\/g'
                fi
            else
                # Relative path, make absolute and convert slashes
                local curr_dir=$(pwd -W 2>/dev/null || pwd)
                echo "$curr_dir/$path" | sed 's/\//\\/g'
            fi
        fi
    else
        # For macOS and Linux
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
        -v|--version)
        VERSION="$2"
        shift # past argument
        shift # past value
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
echo "AutoByteus Server - Deployment (Version $VERSION)"
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

# Define platform-specific file names
if [ "$IS_MACOS" = true ]; then
    BASE_NAME="autobyteus_server_macos-${VERSION}"
elif [ "$IS_WINDOWS" = true ]; then
    BASE_NAME="autobyteus_server_windows-${VERSION}"
else
    BASE_NAME="autobyteus_server_linux-${VERSION}"
fi

# Check if executable exists
EXECUTABLE_SOURCE=""

# Check platform-specific paths first
if [ "$IS_MACOS" = true ]; then
    # Check for macOS specific files
    if [ -f "$SOURCE_DIR/dist/$BASE_NAME" ]; then
        EXECUTABLE_SOURCE="$SOURCE_DIR/dist/$BASE_NAME"
    elif [ -f "$SOURCE_DIR/dist/$BASE_NAME.bin" ]; then
        EXECUTABLE_SOURCE="$SOURCE_DIR/dist/$BASE_NAME.bin"
    elif [ -d "$SOURCE_DIR/dist/$BASE_NAME.app" ]; then
        EXECUTABLE_SOURCE="$SOURCE_DIR/dist/$BASE_NAME.app"
        echo "Found macOS app bundle: $EXECUTABLE_SOURCE"
    fi
elif [ "$IS_WINDOWS" = true ]; then
    # Check for Windows specific files
    if [ -f "$SOURCE_DIR/dist/$BASE_NAME.exe" ]; then
        EXECUTABLE_SOURCE="$SOURCE_DIR/dist/$BASE_NAME.exe"
    fi
else
    # Check for Linux specific files
    if [ -f "$SOURCE_DIR/dist/$BASE_NAME" ]; then
        EXECUTABLE_SOURCE="$SOURCE_DIR/dist/$BASE_NAME"
    elif [ -f "$SOURCE_DIR/dist/$BASE_NAME.bin" ]; then
        EXECUTABLE_SOURCE="$SOURCE_DIR/dist/$BASE_NAME.bin"
    fi
fi

# If not found, try generic names
if [ -z "$EXECUTABLE_SOURCE" ]; then
    if [ "$IS_MACOS" = true ]; then
        if [ -f "$SOURCE_DIR/dist/autobyteus_server" ]; then
            EXECUTABLE_SOURCE="$SOURCE_DIR/dist/autobyteus_server"
        elif [ -f "$SOURCE_DIR/dist/autobyteus_server.bin" ]; then
            EXECUTABLE_SOURCE="$SOURCE_DIR/dist/autobyteus_server.bin"
        elif [ -d "$SOURCE_DIR/dist/autobyteus_server.app" ]; then
            EXECUTABLE_SOURCE="$SOURCE_DIR/dist/autobyteus_server.app"
            echo "Found macOS app bundle: $EXECUTABLE_SOURCE"
        fi
    elif [ "$IS_WINDOWS" = true ]; then
        if [ -f "$SOURCE_DIR/dist/autobyteus_server.exe" ]; then
            EXECUTABLE_SOURCE="$SOURCE_DIR/dist/autobyteus_server.exe"
        fi
    else
        if [ -f "$SOURCE_DIR/dist/autobyteus_server" ]; then
            EXECUTABLE_SOURCE="$SOURCE_DIR/dist/autobyteus_server"
        elif [ -f "$SOURCE_DIR/dist/autobyteus_server.bin" ]; then
            EXECUTABLE_SOURCE="$SOURCE_DIR/dist/autobyteus_server.bin"
        fi
    fi
fi

# Exit if no executable found
if [ -z "$EXECUTABLE_SOURCE" ]; then
    echo "Error: Executable not found in dist directory"
    echo "Please build it first with ./build_one_file.sh"
    exit 1
fi

echo "Found executable: $EXECUTABLE_SOURCE"

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
    elif [ "$IS_WINDOWS" = true ]; then
        # Windows GitBash
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
    echo "[DRY RUN] Would copy executable from: $EXECUTABLE_SOURCE"
else
    # Handle different types of executables
    if [ "$IS_MACOS" = true ] && [[ "$EXECUTABLE_SOURCE" == *.app ]]; then
        # For macOS app bundle
        echo "Copying macOS app bundle..."
        cp -R "$EXECUTABLE_SOURCE" "$TARGET_DIR/"
        TARGET_APP=$(basename "$EXECUTABLE_SOURCE")
        echo "✓ Copied app bundle to: $TARGET_DIR/$TARGET_APP"
    elif [ "$IS_WINDOWS" = true ]; then
        # For Windows executable
        EXECUTABLE_TARGET="$TARGET_DIR/autobyteus_server.exe"
        cp "$EXECUTABLE_SOURCE" "$EXECUTABLE_TARGET"
        echo "✓ Copied executable to: $EXECUTABLE_TARGET"
    else
        # For macOS/Linux executable
        EXECUTABLE_TARGET="$TARGET_DIR/autobyteus_server"
        cp "$EXECUTABLE_SOURCE" "$EXECUTABLE_TARGET"
        chmod +x "$EXECUTABLE_TARGET"
        echo "✓ Copied executable to: $EXECUTABLE_TARGET"
    fi
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
    if [ "$IS_MACOS" = true ] && [[ "$EXECUTABLE_SOURCE" == *.app ]]; then
        echo "  open $(basename "$EXECUTABLE_SOURCE")"
    elif [ "$IS_WINDOWS" = true ]; then
        echo "  .\\autobyteus_server.exe"
    else
        echo "  ./autobyteus_server"
    fi
fi
echo "=================================================="
