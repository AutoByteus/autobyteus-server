import logging.config
import os
from pathlib import Path
import sys


def get_application_root():
    """Get the application root directory, works in both development and packaged mode"""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent.parent


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

    # Modify the log file path to be relative to the application root
    logging.config.fileConfig(
        config_path,
        defaults={'log_dir': str(app_root)},
        disable_existing_loggers=False
    )
