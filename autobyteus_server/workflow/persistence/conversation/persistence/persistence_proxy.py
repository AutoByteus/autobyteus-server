import os
import logging
from typing import List, Optional, Type
from datetime import datetime
from .provider import PersistenceProvider
from .provider_registry import PersistenceProviderRegistry
from .file_based_persistence_provider import FileBasedPersistenceProvider
from .mongo_persistence_provider import MongoPersistenceProvider
from .sql_persistence_provider import SqlPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation, ConversationHistory

logger = logging.getLogger(__name__)

class PersistenceProxy(PersistenceProvider):
    def __init__(self):
        self._provider: Optional[PersistenceProvider] = None
        self._registry = PersistenceProviderRegistry()

    @property
    def provider(self) -> PersistenceProvider:
        if self._provider is None:
            self._provider = self._initialize_provider()
        return self._provider

    def _initialize_provider(self) -> PersistenceProvider:
        provider_type = os.getenv('PERSISTENCE_PROVIDER', 'file').lower()
        provider_class = self._registry.get_provider_class(provider_type)

        if not provider_class:
            available_providers = ', '.join(self._registry.get_available_providers())
            raise ValueError(
                f"Unsupported persistence provider: {provider_type}. "
                f"Available providers: {available_providers}"
            )

        try:
            provider = provider_class()
            if not hasattr(provider, 'get_total_cost'):
                logger.warning(f"{provider_type} provider does not implement get_total_cost method")
                def default_get_total_cost(step_name: Optional[str], start_date: datetime, end_date: datetime) -> float:
                    logger.warning("Using default implementation of get_total_cost which returns 0.0")
                    return 0.0
                provider.get_total_cost = default_get_total_cost
            return provider
        except Exception as e:
            logger.error(f"Failed to initialize {provider_type} provider: {str(e)}")
            if provider_type != 'file':
                logger.info("Falling back to file-based persistence provider")
                return FileBasedPersistenceProvider()
            raise

    def create_conversation(self, step_name: str) -> StepConversation:
        try:
            return self.provider.create_conversation(step_name)
        except Exception as e:
            logger.error(f"Error creating step conversation: {str(e)}")
            raise

    def store_message(
        self,
        step_name: str,
        role: str,
        message: str,
        original_message: Optional[str] = None,
        context_paths: Optional[List[str]] = None,
        conversation_id: Optional[str] = None,
        cost: float = 0.0  # Added cost parameter
    ) -> StepConversation:
        try:
            return self.provider.store_message(
                step_name, role, message, original_message, context_paths, conversation_id, cost=cost  # Pass cost
            )
        except Exception as e:
            logger.error(f"Error storing step conversation: {str(e)}")
            raise

    def get_conversation_history(self, step_name: str, page: int = 1, page_size: int = 10) -> ConversationHistory:
        try:
            return self.provider.get_conversation_history(step_name, page, page_size)
        except Exception as e:
            logger.error(f"Error retrieving step conversation history: {str(e)}")
            raise

    def get_total_cost(
        self,
        step_name: Optional[str],
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        try:
            return self.provider.get_total_cost(step_name, start_date, end_date)
        except Exception as e:
            logger.error(f"Error retrieving total cost: {str(e)}")
            raise

    def register_provider(self, name: str, provider_class: Type[PersistenceProvider]) -> None:
        """
        Register a new persistence provider.

        Args:
            name: Name of the provider
            provider_class: Provider class
        """
        self._registry.register_provider(name, provider_class)
        # Reset provider instance if we're changing the registry
        self._provider = None