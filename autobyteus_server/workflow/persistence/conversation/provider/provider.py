
from abc import ABC, abstractmethod
from typing import List, Optional
from autobyteus_server.workflow.persistence.conversation.domain.models import StepConversation

class PersistenceProvider(ABC):
    """
    Abstract base class for workflow persistence providers.
    Defines the interface that all concrete providers must implement.
    """
    
    @abstractmethod
    def create_conversation(self, step_name: str) -> StepConversation:
        """
        Create a new conversation for a given workflow step.
        
        Args:
            step_name (str): The name of the workflow step.
        
        Returns:
            StepConversation: The newly created conversation.
        """
        pass
    
    @abstractmethod
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
        Store a message within a conversation, including optional token count and cost.
        
        Args:
            step_name (str): The name of the workflow step.
            role (str): The role of the message sender (e.g., user, assistant).
            message (str): The content of the message.
            token_count (Optional[int]): The number of tokens used in the message.
            cost (Optional[float]): The cost associated with the token usage.
            original_message (Optional[str]): The original user message, if applicable.
            context_paths (Optional[List[str]]): List of context file paths, if applicable.
            conversation_id (Optional[str]): ID of the conversation to store the message in.
        
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
    ) -> StepConversation:
        """
        Retrieve paginated conversation history for a given workflow step.
        
        Args:
            step_name (str): The name of the workflow step.
            page (int): The page number to retrieve.
            page_size (int): The number of messages per page.
        
        Returns:
            StepConversation: The paginated conversation history.
        """
        pass

    @abstractmethod
    def update_last_user_message_usage(
        self,
        step_conversation_id: str,
        token_count: int,
        cost: float
    ) -> StepConversation:
        """
        Update the token count and cost for the last user message in the conversation.
        
        Args:
            step_conversation_id (str): The unique ID of the conversation.
            token_count (int): The updated token count.
            cost (float): The updated cost.

        Returns:
            StepConversation: The updated conversation with the last user message usage changed.
        """
        pass
