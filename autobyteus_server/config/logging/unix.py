import os
import sys
import logging

from autobyteus_server.config.logging.base import LoggingConfigurator

logger = logging.getLogger(__name__)

class UnixLoggingConfigurator(LoggingConfigurator):
    """Unix-based (Linux/macOS) logging configuration."""
    
    def configure_logging(self, config_path, logs_dir):
        """
        Configure logging for Unix-based systems using the standard approach.
        """
        import logging.config
        
        # Create logs directory
        os.makedirs(str(logs_dir), exist_ok=True)
        print(f"Created/verified logs directory at: {logs_dir}")
        
        # Create log file path using Path
        log_file = str(logs_dir / 'app.log')
        print(f"Unix log file path: {log_file}")
        
        try:
            # Direct configuration using string substitution
            # This is simpler and works fine on Unix systems
            logging.config.fileConfig(
                config_path,
                defaults={'log_file_path': log_file},
                disable_existing_loggers=False
            )
            print(f"Logging configured successfully with log file: {log_file}")
            logger.info(f"Logging started with file: {log_file}")
            return True
        except Exception as e:
            print(f"ERROR configuring logging: {e}")
            self._setup_basic_logging(log_file)
            return False
    
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
