
import os
import logging
from typing import Optional, List

from autobyteus_server.ai_terminal.persistence.domain.models import AiTerminalConversation, ConversationHistory
from autobyteus_server.ai_terminal.persistence.providers.ai_terminal_persistence_provider import AiTerminalPersistenceProvider
from autobyteus_server.ai_terminal.persistence.providers.ai_terminal_provider_registry import AiTerminalProviderRegistry

logger = logging.getLogger(__name__)

class AiTerminalPersistenceProxy(AiTerminalPersistenceProvider):
    """
    Proxy for AI Terminal persistence that chooses the appropriate provider
    based on environment variables or configuration.
    """

    def __init__(self):
        super().__init__()
        self._provider: Optional[AiTerminalPersistenceProvider] = None
        self._registry = AiTerminalProviderRegistry()

    @property
    def provider(self) -> AiTerminalPersistenceProvider:
        """Lazy initialization of the actual persistence provider."""
        if self._provider is None:
            self._provider = self._initialize_provider()
        return self._provider

    def _initialize_provider(self) -> AiTerminalPersistenceProvider:
        """Initialize the appropriate provider based on environment configuration."""
        provider_type = os.getenv("PERSISTENCE_PROVIDER", "mongodb").lower()
        provider_class = self._registry.get_provider_class(provider_type)
        
        if not provider_class:
            available_providers = ', '.join(self._registry.get_available_providers())
            raise ValueError(
                f"Unsupported AI Terminal persistence provider: {provider_type}. "
                f"Available providers: {available_providers}"
            )
        
        try:
            logger.info(f"Initializing AI Terminal persistence provider: {provider_type}")
            return provider_class()
        except Exception as e:
            logger.error(f"Failed to initialize {provider_type} provider: {str(e)}")
            raise

    def create_conversation(self) -> AiTerminalConversation:
        """Create a new conversation."""
        try:
            return self.provider.create_conversation()
        except Exception as e:
            logger.error(f"Failed to create conversation: {str(e)}")
            raise

    def store_message(
        self,
        conversation_id: str,
        role: str,
        message: str,
        token_count: Optional[int] = None,
        cost: Optional[float] = None
    ) -> AiTerminalConversation:
        """Store a message in a conversation."""
        try:
            return self.provider.store_message(
                conversation_id=conversation_id,
                role=role,
                message=message,
                token_count=token_count,
                cost=cost
            )
        except Exception as e:
            logger.error(f"Failed to store message: {str(e)}")
            raise

    def get_conversation_history(
        self,
        conversation_id: str
    ) -> AiTerminalConversation:
        """Get history for a specific conversation."""
        try:
            return self.provider.get_conversation_history(conversation_id)
        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            raise

    def list_conversations(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> ConversationHistory:
        """List all conversations with pagination."""
        try:
            return self.provider.list_conversations(page=page, page_size=page_size)
        except Exception as e:
            logger.error(f"Failed to list conversations: {str(e)}")
            raise
