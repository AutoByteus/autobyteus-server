# File: autobyteus-server/autobyteus_server/api/graphql/queries/api_key_queries.py

import strawberry
from typing import Optional
from autobyteus_server.config import config

@strawberry.type
class Query:
    @strawberry.field
    def get_llm_api_key(self, model: str) -> Optional[str]:
        """
        Fetch the API key for a given LLM model.

        Args:
            model (str): The name of the LLM model.

        Returns:
            Optional[str]: The API key if found, None otherwise.
        """
        try:
            api_key = config.get_llm_api_key(model)
            return api_key if api_key else None
        except Exception as e:
            print(f"Error retrieving API key: {str(e)}")
            return None