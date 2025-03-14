import logging
from typing import Optional
from autobyteus_server.config.app_config import AppConfig

logger = logging.getLogger(__name__)

class AppConfigProvider():
    """
    AppConfigProvider is a class that provides access to the global AppConfig instance.
    It only handles creation and access to the AppConfig instance, not initialization.
    """
    _instance: Optional[AppConfig] = None
    
    @classmethod
    def get_config(cls) -> AppConfig:
        """
        Get the AppConfig instance. If not created, creates it.
        
        Returns:
            AppConfig: The AppConfig instance.
        """
        if cls._instance is None:
            # Removed intermediate logging to reduce noise.
            cls._instance = AppConfig()
        return cls._instance
    
    @property
    def config(self) -> AppConfig:
        """
        Property that provides access to the AppConfig instance.
        If the AppConfig is not created, it will be created automatically.
        
        Returns:
            AppConfig: The AppConfig instance.
        """
        return self.get_config()

# Create a singleton instance of AppConfigProvider that will be used by clients
app_config_provider = AppConfigProvider()
