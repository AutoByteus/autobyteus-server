import strawberry
from typing import Optional, List
from autobyteus_server.config import app_config_provider
from autobyteus.llm.llm_factory import LLMFactory

@strawberry.type
class Query:
    @strawberry.field
    def get_llm_provider_api_key(self, provider: str) -> Optional[str]:
        """
        Fetch the API key for a given LLM provider.

        Args:
            provider (str): The name of the LLM provider.

        Returns:
            Optional[str]: The API key if found, None otherwise.
        """
        try:
            api_key = app_config_provider.config.get_llm_api_key(provider)
            return api_key if api_key else None
        except Exception as e:
            print(f"Error retrieving API key: {str(e)}")
            return None

    @strawberry.field
    def available_models(self) -> List[str]:
        """
        Get all available LLM models.

        Returns:
            List[str]: List of available model names.
        """
        return LLMFactory.get_all_models()

    @strawberry.field
    def available_providers(self) -> List[str]:
        """
        Get all available LLM providers.

        Returns:
            List[str]: List of available provider names.
        """
        return [provider.name for provider in LLMFactory.get_all_providers()]
