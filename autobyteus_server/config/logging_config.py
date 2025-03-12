import logging
import logging.config
import os
from pathlib import Path
import sys
from autobyteus_server.utils.app_utils import get_application_root

def configure_logger():
    """Configure logging using the logging configuration file"""
    app_root = get_application_root()
    config_path = app_root / 'logging_config.ini'
    
    # Create logs directory if it doesn't exist
    logs_dir = app_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Calculate the absolute path for the log file using proper path handling
    log_file_path = str(logs_dir / 'app.log')
    
    # Debug information to help troubleshoot path issues
    print(f"Application root: {app_root}")
    print(f"Logs directory: {logs_dir}")
    print(f"Log file path: {log_file_path}")
    
    if not os.path.exists(config_path):
        # Fallback to basic configuration if file not found
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.warning(f"Logging config file not found at {config_path}. Using basic configuration.")
        return

    try:
        # Use ConfigParser to read the config file first
        import configparser
        config = configparser.ConfigParser()
        config.read(config_path)
        
        # If the fileHandler section exists, modify its args to use the correct path
        if 'handler_fileHandler' in config.sections():
            # Replace the args with the correct log file path
            config['handler_fileHandler']['args'] = f"('{log_file_path}', 'a')"
            
            # Write the updated config to a temporary file
            temp_config_path = app_root / 'temp_logging_config.ini'
            with open(temp_config_path, 'w') as temp_file:
                config.write(temp_file)
            
            # Use the temp config file for logging configuration
            logging.config.fileConfig(
                temp_config_path,
                disable_existing_loggers=False
            )
            
            # Clean up the temporary file
            os.remove(temp_config_path)
        else:
            # If the section doesn't exist, use the original file with defaults
            logging.config.fileConfig(
                config_path,
                defaults={'log_dir': str(app_root)},
                disable_existing_loggers=False
            )
    except Exception as e:
        # If anything goes wrong, fall back to basic configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.warning(f"Error configuring logging: {e}. Using basic configuration.")
