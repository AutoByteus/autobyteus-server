import logging

logger = logging.getLogger(__name__)

class LoggingConfigurator:
    """Base class for platform-specific logging configuration."""
    
    def __init__(self, app_config):
        self.app_config = app_config
    
    def configure_logging(self, config_path, logs_dir):
        """Configure logging using the provided configuration file and logs directory."""
        raise NotImplementedError("This method must be implemented by subclasses")
