
from typing import Dict, Type, Optional
from autobyteus.utils.singleton import SingletonMeta
from .ai_terminal_persistence_provider import AiTerminalPersistenceProvider
from .mongo_ai_terminal_provider import MongoAiTerminalProvider
from .sql_ai_terminal_provider import SqlAiTerminalProvider

class AiTerminalProviderRegistry(metaclass=SingletonMeta):
    """Registry for managing AI Terminal persistence providers."""

    def __init__(self):
        self._providers: Dict[str, Type[AiTerminalPersistenceProvider]] = {
            'mongodb': MongoAiTerminalProvider,
            'postgresql': SqlAiTerminalProvider,
            'sqlite': SqlAiTerminalProvider
        }

    def register_provider(self, name: str, provider: Type[AiTerminalPersistenceProvider]) -> None:
        """
        Register a new AI Terminal persistence provider.

        Args:
            name: Name of the provider
            provider: Provider class
        """
        self._providers[name.lower()] = provider

    def get_provider_class(self, name: str) -> Optional[Type[AiTerminalPersistenceProvider]]:
        """
        Get a provider class by name.

        Args:
            name: Name of the provider

        Returns:
            Type[AiTerminalPersistenceProvider] or None: The provider class if found
        """
        return self._providers.get(name.lower())

    def get_available_providers(self) -> list[str]:
        """Get list of available AI Terminal provider names."""
        return list(self._providers.keys())
