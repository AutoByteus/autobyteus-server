import os
import sys
import tempfile
import logging

from autobyteus_server.config.logging.base import LoggingConfigurator

logger = logging.getLogger(__name__)

class WindowsLoggingConfigurator(LoggingConfigurator):
    """Windows-specific logging configuration with workarounds for path handling."""
    
    def configure_logging(self, config_path, logs_dir):
        """
        Configure logging for Windows using a temporary modified config file
        to avoid escape sequence interpretation issues.
        """
        import logging.config
        
        # Create logs directory
        logs_dir_str = str(logs_dir)
        os.makedirs(logs_dir_str, exist_ok=True)
        print(f"Created/verified logs directory at: {logs_dir}")
        
        # Create log file path using os.path.join for Windows-safe path handling
        log_file = os.path.join(logs_dir_str, "app.log")
        print(f"Windows log file path: {log_file}")
        
        # Test if we can write to the log file
        try:
            with open(log_file, 'a') as test_file:
                test_file.write("Log file test\n")
            print(f"Successfully wrote to log file: {log_file}")
        except Exception as file_e:
            print(f"ERROR writing to log file: {file_e}")
            # Use fallback location
            log_file = os.path.join(os.getcwd(), "autobyteus_app.log")
            print(f"Using fallback log file: {log_file}")
            with open(log_file, 'a') as test_file:
                test_file.write("Log file test\n")
        
        # Create a temporary modified config file with hardcoded path
        # This is the Windows-specific workaround
        temp_config = self._create_modified_logging_config(config_path, log_file)
        
        try:
            print(f"Using modified logging config from: {temp_config}")
            logging.config.fileConfig(
                temp_config,
                disable_existing_loggers=False
            )
            # Clean up the temporary file
            try:
                os.unlink(temp_config)
            except:
                print(f"Note: Could not delete temporary config file: {temp_config}")
                
            print(f"Logging configured successfully with log file: {log_file}")
            logger.info(f"Logging started with file: {log_file}")
            return True
        except Exception as e:
            print(f"ERROR configuring logging: {e}")
            self._setup_basic_logging(log_file)
            return False

    def _create_modified_logging_config(self, config_path, log_file_path):
        """
        Create a modified logging configuration file with the log path hardcoded.
        This avoids issues with string interpolation of paths on Windows.
        
        Args:
            config_path (Path): Path to the original logging config file
            log_file_path (str): The log file path to hardcode
            
        Returns:
            str: Path to the temporary logging config file
        """
        print(f"Creating modified logging config with hardcoded path: {log_file_path}")
        
        if not os.path.exists(config_path):
            print(f"Original logging config not found at {config_path}")
            return None
        
        # Create a temporary file for the modified config
        fd, temp_path = tempfile.mkstemp(suffix='.ini', prefix='logging_config_')
        os.close(fd)
        
        # Escape backslashes for Python string literals
        log_file_path = log_file_path.replace('\\', '\\\\')
        
        # Read the original config
        with open(config_path, 'r') as file:
            content = file.read()
        
        # Replace the dynamic path with a hardcoded one
        modified_content = content.replace('args=("%(log_file_path)s"', f'args=("{log_file_path}"')
        
        # Write the modified config
        with open(temp_path, 'w') as file:
            file.write(modified_content)
        
        print(f"Created temporary config file at: {temp_path}")
        return temp_path
    
    def _setup_basic_logging(self, log_file):
        """Set up basic logging as a fallback."""
        import logging
        
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            print(f"Set up basic logging with file: {log_file}")
        except Exception as fallback_e:
            print(f"ERROR with fallback logging: {fallback_e}")
            # Console-only as last resort
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler(sys.stdout)]
            )
            print("Using console-only logging")
