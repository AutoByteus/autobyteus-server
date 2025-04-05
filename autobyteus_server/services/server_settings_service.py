import logging
from typing import Dict, List, Tuple
from autobyteus_server.config import app_config_provider
from autobyteus_server.utils.network_utils import get_local_ip

logger = logging.getLogger(__name__)

class ServerSettingDescription:
    """Class to hold information about a server setting."""
    def __init__(self, key: str, description: str):
        """
        Initialize a server setting description.
        
        Args:
            key (str): The key of the setting in the config.
            description (str): Human-readable description of the setting.
        """
        self.key = key
        self.description = description


class ServerSettingsService:
    """Service to manage server settings."""
    
    def __init__(self):
        """Initialize the server settings service."""
        self._settings_info: Dict[str, ServerSettingDescription] = {}
        self._initialize_settings()
    
    def _initialize_settings(self):
        """Initialize the available settings with their descriptions."""
        # LLM Server URL setting
        self._settings_info["AUTOBYTEUS_LLM_SERVER_URL"] = ServerSettingDescription(
            key="AUTOBYTEUS_LLM_SERVER_URL",
            description="URL of the AUTOBYTEUS LLM server"
        )
        
        # Server Host setting for proper URL generation
        self._settings_info["AUTOBYTEUS_SERVER_HOST"] = ServerSettingDescription(
            key="AUTOBYTEUS_SERVER_HOST",
            description="Host address for external services to access the server (e.g., Docker containers)"
        )
        
        # VNC Server URL setting
        self._settings_info["AUTOBYTEUS_VNC_SERVER_URL"] = ServerSettingDescription(
            key="AUTOBYTEUS_VNC_SERVER_URL",
            description="URL of the AUTOBYTEUS VNC server (e.g., ws://localhost:6080)"
        )
        
        # Add more settings here in the future
        
        logger.info(f"Initialized server settings service with {len(self._settings_info)} settings")
    
    def get_available_settings(self) -> List[Dict[str, str]]:
        """
        Get the list of available settings.
        
        Returns:
            List[Dict[str, str]]: A list of dictionaries with key, value, and description.
        """
        config = app_config_provider.config
        
        result = []
        for key, setting_info in self._settings_info.items():
            value = config.get(key, "")
            
            # For AUTOBYTEUS_SERVER_HOST, first try to detect local IP
            if key == "AUTOBYTEUS_SERVER_HOST":
                local_ip = get_local_ip()
                if local_ip:
                    # Always use the detected IP and update the config
                    value = local_ip
                    config.set(key, value)
                    logger.info(f"Detected and set server host IP: {value}")
                # If local_ip is None, keep using the value from config (environment variable)
            
            result.append({
                "key": key,
                "value": value,
                "description": setting_info.description
            })
        
        return result
    
    def update_setting(self, key: str, value: str) -> Tuple[bool, str]:
        """
        Update a server setting.
        
        Args:
            key (str): The key of the setting to update.
            value (str): The new value for the setting.
            
        Returns:
            Tuple[bool, str]: A tuple of (success, message).
        """
        # Check if the setting is allowed
        if key not in self._settings_info:
            return False, f"Setting '{key}' is not allowed to be updated."
        
        try:
            # Get the current config and update the value
            config = app_config_provider.config
            config.set(key, value)
            
            logger.info(f"Server setting '{key}' updated to '{value}'")
            return True, f"Server setting '{key}' has been updated successfully."
        except Exception as e:
            logger.error(f"Error updating server setting '{key}': {str(e)}")
            return False, f"Error updating server setting: {str(e)}"
    
    def is_valid_setting(self, key: str) -> bool:
        """
        Check if a setting key is valid.
        
        Args:
            key (str): The key to check.
            
        Returns:
            bool: True if the key is valid, False otherwise.
        """
        return key in self._settings_info


# Singleton instance for use throughout the application
server_settings_service = ServerSettingsService()
