from typing import Dict, Type, Optional
from autobyteus.utils.singleton import SingletonMeta
from .provider import PersistenceProvider
from .mongodb_persistence_provider import MongoPersistenceProvider
from .sql_persistence_provider import SqlPersistenceProvider  # Updated import

class TokenUsageProviderRegistry(metaclass=SingletonMeta):
    """Registry for managing token usage persistence providers."""

    def __init__(self):
        self._providers: Dict[str, Type[PersistenceProvider]] = {
            'mongodb': MongoPersistenceProvider,
            'postgresql': SqlPersistenceProvider,  # Assuming PostgreSQL and SQLite use the same provider
            'sqlite': SqlPersistenceProvider
        }

    def register_provider(self, name: str, provider: Type[PersistenceProvider]) -> None:
        """
        Register a new token usage persistence provider.

        Args:
            name: Name of the provider
            provider: Provider class
        """
        self._providers[name.lower()] = provider

    def get_provider_class(self, name: str) -> Optional[Type[PersistenceProvider]]:
        """
        Get a provider class by name.

        Args:
            name: Name of the provider

        Returns:
            Type[PersistenceProvider] or None: The provider class if found
        """
        return self._providers.get(name.lower())

    def get_available_providers(self) -> list[str]:
        """Get list of available token usage provider names."""
        return list(self._providers.keys())