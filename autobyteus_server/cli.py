import sys
import os
import argparse
import uvicorn
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def get_application_root():
    """Get the application root directory, works in both development and packaged mode"""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent

def validate_packaged_environment():
    """Validate that all required files and directories exist in packaged mode"""
    app_root = get_application_root()
    required_files = [
        '.env',
        'logging_config.ini',
        'alembic.ini'
    ]
    required_dirs = [
        'logs',
        'resources',
        'alembic'
    ]
    
    missing_files = [f for f in required_files if not (app_root / f).exists()]
    missing_dirs = [d for d in required_dirs if not (app_root / d).is_dir()]
    
    if missing_files or missing_dirs:
        print("Error: Missing required files or directories:")
        if missing_files:
            print("Files:", missing_files)
        if missing_dirs:
            print("Directories:", missing_dirs)
        sys.exit(1)

def main():
    # If we're running in packaged mode, validate the environment
    if getattr(sys, 'frozen', False):
        validate_packaged_environment()
    
    parser = argparse.ArgumentParser(description='AutoByteus Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')
    
    args = parser.parse_args()
    
    # Set the working directory to the application root
    os.chdir(str(get_application_root()))
    
    uvicorn.run(
        "autobyteus_server.app:app",
        host=args.host,
        port=args.port,
        log_level="info"
    )

if __name__ == '__main__':
    main()
