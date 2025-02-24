
import os
import logging
from typing import List, Optional, Type
from autobyteus_server.workflow.persistence.conversation.provider.provider import PersistenceProvider
from autobyteus_server.workflow.persistence.conversation.provider.provider_registry import PersistenceProviderRegistry
from autobyteus_server.workflow.persistence.conversation.provider.mongo_persistence_provider import MongoPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.provider.sql_persistence_provider import SqlPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation, ConversationHistory

logger = logging.getLogger(__name__)

class PersistenceProxy(PersistenceProvider):
    """
    Proxy for workflow step conversation persistence that handles provider selection and initialization.
    This is the main interface that users should interact with.
    """
    
    def __init__(self):
        """Initialize the persistence proxy."""
        self._provider: Optional[PersistenceProvider] = None
        self._registry = PersistenceProviderRegistry()

    @property
    def provider(self) -> PersistenceProvider:
        """
        Lazy initialization of the actual provider.
        
        Returns:
            PersistenceProvider: The configured persistence provider
            
        Raises:
            ValueError: If the configured provider is not supported
        """
        if self._provider is None:
            self._provider = self._initialize_provider()
        return self._provider

    def _initialize_provider(self) -> PersistenceProvider:
        """
        Initialize the appropriate provider based on environment configuration.
        
        Returns:
            PersistenceProvider: Initialized provider instance
            
        Raises:
            ValueError: If the configured provider is not supported
        """
        provider_type = os.getenv('PERSISTENCE_PROVIDER', 'sqlite').lower()
        provider_class = self._registry.get_provider_class(provider_type)
        
        if not provider_class:
            available_providers = ', '.join(self._registry.get_available_providers())
            raise ValueError(
                f"Unsupported persistence provider: {provider_type}. "
                f"Available providers: {available_providers}"
            )
        
        try:
            return provider_class()
        except Exception as e:
            logger.error(f"Failed to initialize {provider_type} provider: {str(e)}")
            raise

    def create_conversation(self, step_name: str, llm_model: Optional[str] = None) -> StepConversation:
        """
        Create a new empty conversation for the step with optional llm_model.
        
        Args:
            step_name: Name of the workflow step
            llm_model: Optional LLM model for the conversation
            
        Returns:
            StepConversation: Newly created conversation
        """
        try:
            return self.provider.create_conversation(step_name, llm_model)
        except Exception as e:
            logger.error(f"Error creating step conversation: {str(e)}")
            raise

    def store_message(
        self, 
        step_name: str, 
        role: str, 
        message: str,
        token_count: Optional[int] = None,
        cost: Optional[float] = None,
        original_message: Optional[str] = None,
        context_paths: Optional[List[str]] = None,
        conversation_id: Optional[str] = None
    ) -> StepConversation:
        """
        Store a workflow step conversation message using the configured provider.
        
        Args:
            step_name: Name of the workflow step
            role: Role of the message sender
            message: Content of the message
            token_count: Optional number of tokens used in the message
            cost: Optional cost associated with the token usage
            original_message: The original user message, if applicable
            context_paths: List of context file paths, if applicable
            conversation_id: ID of the conversation to store the message in
            
        Returns:
            StepConversation: The updated conversation
            
        Raises:
            ValueError: If token_count is negative or cost is negative
            Exception: If there's an error storing the message
        """
        try:
            if token_count is not None and token_count < 0:
                raise ValueError("token_count cannot be negative")
            if cost is not None and cost < 0:
                raise ValueError("cost cannot be negative")
                
            return self.provider.store_message(
                step_name,
                role,
                message,
                token_count,
                cost,
                original_message,
                context_paths,
                conversation_id
            )
        except Exception as e:
            logger.error(f"Error storing step conversation: {str(e)}")
            raise

    def get_conversation_history(
        self,
        step_name: str,
        page: int = 1,
        page_size: int = 10
    ) -> ConversationHistory:
        """
        Retrieve workflow step conversation history using the configured provider.
        
        Args:
            step_name: Name of the workflow step
            page: Page number (1-based)
            page_size: Number of messages per page
            
        Returns:
            ConversationHistory: Paginated conversation history
        """
        try:
            return self.provider.get_conversation_history(step_name, page, page_size)
        except Exception as e:
            logger.error(f"Error retrieving step conversation history: {str(e)}")
            raise

    def update_last_user_message_usage(
        self,
        step_conversation_id: str,
        token_count: int,
        cost: float
    ) -> StepConversation:
        """
        Update the token count and cost for the last user message in the conversation.
        
        Args:
            step_conversation_id: The unique ID of the conversation
            token_count: The updated token count
            cost: The updated cost

        Returns:
            StepConversation: The updated conversation
        """
        try:
            if token_count < 0:
                raise ValueError("token_count cannot be negative")
            if cost < 0:
                raise ValueError("cost cannot be negative")

            return self.provider.update_last_user_message_usage(step_conversation_id, token_count, cost)
        except Exception as e:
            logger.error(f"Error updating last user message usage: {str(e)}")
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
