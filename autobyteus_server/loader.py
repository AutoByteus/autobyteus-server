"""
Loader module to help PyInstaller detect and package the FastAPI app correctly.
This module only serves as a build-time helper and has no runtime impact.
"""
# Import but don't execute any initialization code
from autobyteus_server.app import app as _app

def get_app():
    """Helper function for PyInstaller to detect dependencies"""
    return _app
