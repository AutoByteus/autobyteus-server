"""
Application utilities for AutoByteus Server.
Provides functions for consistent application management across different execution environments.
"""
import os
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Cached result of Nuitka detection
_is_nuitka = None

def is_nuitka_build() -> bool:
    """
    Detect if the application is running from a Nuitka build, especially onefile mode.
    
    This checks for Nuitka's 'onefile_' pattern in the executable path, which is consistent
    across different operating systems (Linux, macOS, Windows) when running in onefile mode.
    
    Returns:
        bool: True if running from a Nuitka build, False otherwise
    """
    global _is_nuitka
    
    # Return cached result if available
    if _is_nuitka is not None:
        return _is_nuitka
    
    # Check if executable is in a Nuitka temp directory by looking for the 'onefile_' pattern
    # This works across all operating systems supported by Nuitka
    if 'onefile_' in sys.executable:
        _is_nuitka = True
        return True
    
    _is_nuitka = False
    return False

def get_application_root() -> Path:
    """
    Get the application root directory in a way that works for all execution scenarios:
    1. When running with uvicorn directly
    2. When packaged with Nuitka (both onefile and standalone builds)
    
    Returns:
        Path: The absolute path to the application root directory
    """
    # Case 1: Running as a frozen executable (traditional freezers like PyInstaller)
    if getattr(sys, 'frozen', False):
        executable_path = Path(os.path.abspath(sys.argv[0])).resolve()
        app_root = executable_path.parent
        return app_root
    
    # Case 2: Running from a Nuitka build (especially onefile)
    if is_nuitka_build():
        # For Nuitka-built executables in onefile mode, we need to use sys.argv[0]
        # which points to the original executable, not the unpacked one
        executable_path = Path(os.path.abspath(sys.argv[0])).resolve()
        app_root = executable_path.parent
        return app_root
    
    # Case 3: Running as a Python module (development mode)
    # Using the path of this module to determine the application root
    # app_utils.py is in autobyteus-server/autobyteus_server/utils/, so we need to go up to the root folder autobyteus-server
    current_file = Path(__file__).resolve()
    app_root = current_file.parent.parent.parent
    return app_root

def get_data_directory() -> Path:
    """
    Get the data directory path, which depends on the execution mode:
    - In development mode: Uses application root
    - In frozen/built mode: Uses executable directory
    
    Returns:
        Path: The data directory path
    """
    return get_application_root() / 'data'

def get_resource_path(resource_name: str) -> Path:
    """
    Get the absolute path to a resource file.
    
    Args:
        resource_name (str): Name of the resource file
        
    Returns:
        Path: Absolute path to the resource file
    """
    resources_dir = get_application_root() / 'resources'
    return resources_dir / resource_name

def ensure_directory_exists(directory_path: Path) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path (Path): The directory path to check/create
    """
    directory_path.mkdir(parents=True, exist_ok=True)

def is_packaged_environment() -> bool:
    """
    Check if the application is running from a packaged executable.
    This includes both traditional freezers (sys.frozen) and Nuitka builds.
    
    Returns:
        bool: True if running from a packaged executable, False otherwise
    """
    return getattr(sys, 'frozen', False) or is_nuitka_build()
