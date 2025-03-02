import strawberry
from autobyteus_server.config import config
from autobyteus.llm.llm_factory import LLMFactory

@strawberry.type
class Mutation:
    @strawberry.mutation
    def set_llm_provider_api_key(self, provider: str, api_key: str) -> str:
        """
        Set the API key for a specific LLM provider.
        Args:
            provider (str): The name of the LLM provider.
            api_key (str): The API key to set.
        Returns:
            str: A message indicating success or failure.
        """
        try:
            if not provider or not api_key:
                raise ValueError("Both provider and api_key must be provided.")
            config.set_llm_api_key(provider, api_key)
            return f"API key for provider {provider} has been set successfully."
        except ValueError as ve:
            return f"Error setting API key: {str(ve)}"
        except Exception as e:
            return f"Unexpected error setting API key: {str(e)}"

    @strawberry.mutation
    def reload_llm_models(self) -> str:
        """
        Reload all LLM models by triggering the LLMFactory reinitialization.
        This is useful when new provider API keys are configured and
        we need to discover models that might be available with the new keys.

        Returns:
            str: A message indicating success or failure.
        """
        try:
            # Call the reinitialize method on LLMFactory
            success = LLMFactory.reinitialize()
            if success:
                return "LLM models reloaded successfully."
            else:
                return "Failed to reload LLM models."
        except Exception as e:
            return f"Error reloading LLM models: {str(e)}"
