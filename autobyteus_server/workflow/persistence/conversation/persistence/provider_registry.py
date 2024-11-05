from typing import Dict, Type, Optional
from autobyteus.utils.singleton import SingletonMeta
from .provider import PersistenceProvider
from .file_based_persistence_provider import FileBasedPersistenceProvider
from .mongo_persistence_provider import MongoPersistenceProvider
from .sql_persistence_provider import SqlPersistenceProvider  # Updated import

class PersistenceProviderRegistry(metaclass=SingletonMeta):
    """Registry for managing persistence providers."""
    
    def __init__(self):
        self._providers: Dict[str, Type[PersistenceProvider]] = {
            'file': FileBasedPersistenceProvider,
            'mongodb': MongoPersistenceProvider,
            'postgresql': SqlPersistenceProvider,  # Updated to use SqlPersistenceProvider
            'sqlite': SqlPersistenceProvider        # Added SQLite support
        }

    def register_provider(self, name: str, provider: Type[PersistenceProvider]) -> None:
        """
        Register a new persistence provider.
        
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
        """Get list of available provider names."""
        return list(self._providers.keys())