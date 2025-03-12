import logging.config
import os
from pathlib import Path
import sys
from autobyteus_server.utils.app_utils import get_application_root

def configure_logger():
    """Configure logging using the logging configuration file"""
    app_root = get_application_root()
    config_path = app_root / 'logging_config.ini'
    
    if not os.path.exists(config_path):
        # Fallback to basic configuration if file not found
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.warning(f"Logging config file not found at {config_path}. Using basic configuration.")
        return

    # Create logs directory if it doesn't exist
    logs_dir = app_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Create the full log file path using os.path.join for correct platform handling
    log_file = os.path.join(str(logs_dir), 'app.log')
    
    # Print debug information
    print(f"Application root: {app_root}")
    print(f"Logs directory: {logs_dir}")
    print(f"Log file path: {log_file}")

    try:
        # Use the absolute path directly instead of string interpolation
        logging.config.fileConfig(
            config_path,
            defaults={'log_file_path': log_file},
            disable_existing_loggers=False
        )
        logging.info("Logging configured successfully")
    except Exception as e:
        # Fallback to basic configuration if there's an error
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.warning(f"Error configuring logging: {e}. Using basic configuration.")
