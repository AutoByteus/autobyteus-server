# File: autobyteus-server/autobyteus_server/api/graphql/mutations/api_key_mutations.py

import strawberry
from autobyteus_server.config import config

@strawberry.type
class Mutation:
    @strawberry.mutation
    def set_llm_api_key(self, model: str, api_key: str) -> str:
        """
        Set the API key for a specific LLM model.

        Args:
            model (str): The name of the LLM model.
            api_key (str): The API key to set.

        Returns:
            str: A message indicating success or failure.
        """
        try:
            if not model or not api_key:
                raise ValueError("Both model and api_key must be provided.")
            config.set_llm_api_key(model, api_key)
            return f"API key for model {model} has been set successfully."
        except ValueError as ve:
            return f"Error setting API key: {str(ve)}"
        except Exception as e:
            return f"Unexpected error setting API key: {str(e)}"