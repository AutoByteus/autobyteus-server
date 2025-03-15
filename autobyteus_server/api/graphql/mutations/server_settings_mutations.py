import strawberry
import logging
from autobyteus_server.services import server_settings_service

logger = logging.getLogger(__name__)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def update_server_setting(self, key: str, value: str) -> str:
        """
        Update a server setting in the configuration.
        
        Args:
            key (str): The key of the setting to update.
            value (str): The new value for the setting.
            
        Returns:
            str: A message indicating success or failure.
        """
        success, message = server_settings_service.update_setting(key, value)
        return message
