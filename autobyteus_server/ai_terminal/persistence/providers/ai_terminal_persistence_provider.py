from abc import ABC, abstractmethod
from typing import List
from autobyteus_server.ai_terminal.persistence.domain.models import AiTerminalConversation

class AiTerminalPersistenceProvider(ABC):
    """
    Abstract base provider for AI Terminal conversation persistence.
    Orchestrates domain models, using repository classes under the hood.
    """

    @abstractmethod
    def create_conversation(self) -> AiTerminalConversation:
        """
        Create a new AI Terminal conversation and return the domain model representing it.
        """
        pass

    @abstractmethod
    def store_message(self, conversation_id: str, role: str, message: str) -> AiTerminalConversation:
        """
        Store a message in the specified AI Terminal conversation and return the updated domain model.
        """
        pass

    @abstractmethod
    def get_conversation_history(self, conversation_id: str) -> AiTerminalConversation:
        """
        Retrieve all messages for a specific conversation, returning the domain model representation.
        """
        pass

    @abstractmethod
    def list_conversations(self, page: int = 1, page_size: int = 10) -> List[AiTerminalConversation]:
        """
        List all conversations with optional pagination, returning them as domain models.
        """
        pass