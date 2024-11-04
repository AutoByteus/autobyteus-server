from abc import ABC, abstractmethod
from typing import List, Optional
from autobyteus_server.workflow.persistence.conversation.domain.models import StepConversation, ConversationHistory

class PersistenceProvider(ABC):
    @abstractmethod
    def create_conversation(self, step_name: str) -> StepConversation:
        """Create a new empty conversation for the step."""
        pass

    @abstractmethod
    def store_message(
        self, 
        step_name: str, 
        role: str, 
        message: str, 
        original_message: Optional[str] = None,  # Use original_message in domain model
        context_paths: Optional[List[str]] = None,
        conversation_id: Optional[str] = None  # New parameter
    ) -> StepConversation:
        """
        Store a message in the specified conversation.
        
        Args:
            step_name: Name of the workflow step.
            role: Role of the message sender.
            message: Content of the message.
            original_message: The original user message, if applicable.  # Updated docstring
            context_paths: List of context file paths, if applicable.
            conversation_id: ID of the conversation to store the message in.
        
        Returns:
            StepConversation: The updated conversation.
        """
        pass

    @abstractmethod
    def get_conversation_history(
        self, 
        step_name: str, 
        page: int = 1, 
        page_size: int = 10
    ) -> ConversationHistory:
        """
        Retrieve paginated conversations by step name.
        Returns ConversationHistory containing paginated results.
        """
        pass