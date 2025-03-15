import strawberry
from typing import List
from autobyteus_server.services import server_settings_service

@strawberry.type
class ServerSetting:
    key: str
    value: str
    description: str

@strawberry.type
class Query:
    @strawberry.field
    def get_server_settings(self) -> List[ServerSetting]:
        """
        Get a list of configurable server settings.
        
        Returns:
            List[ServerSetting]: A list of server settings.
        """
        settings = server_settings_service.get_available_settings()
        return [
            ServerSetting(
                key=setting["key"],
                value=setting["value"],
                description=setting["description"]
            )
            for setting in settings
        ]
