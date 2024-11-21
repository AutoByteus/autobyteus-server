from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation, ConversationHistory

class PersistenceProvider(ABC):
    @abstractmethod
    def create_conversation(self, step_name: str) -> StepConversation:
        pass

    @abstractmethod
    def store_message(
        self,
        step_name: str,
        role: str,
        message: str,
        original_message: Optional[str] = None,
        context_paths: Optional[List[str]] = None,
        conversation_id: Optional[str] = None
    ) -> StepConversation:
        pass

    @abstractmethod
    def get_conversation_history(self, step_name: str, page: int = 1, page_size: int = 10) -> ConversationHistory:
        pass

    @abstractmethod
    def get_total_cost(
        self,
        step_name: Optional[str],
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        pass