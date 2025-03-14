from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, TypeVar, Generic

@dataclass
class Message:
    """
    Domain model representing a conversation message.
    Provides a persistence-agnostic representation of messages.
    """
    role: str
    message: str
    timestamp: datetime
    message_id: Optional[str] = None
    original_message: Optional[str] = None
    context_paths: Optional[List[str]] = None
    token_count: Optional[int] = None
    cost: Optional[float] = None

@dataclass
class StepConversation:
    """
    Domain model representing a complete step conversation with all its messages.
    Provides a persistence-agnostic representation of conversations.
    """
    step_conversation_id: str
    step_name: str
    created_at: datetime
    messages: List[Message]
    llm_model: Optional[str] = None  # Added field for LLM model

T = TypeVar('T')

@dataclass
class PaginatedResult(Generic[T]):
    """
    Generic domain model for paginated results.
    """
    items: List[T]
    total_items: int
    total_pages: int
    current_page: int

@dataclass
class ConversationHistory:
    """
    Domain model representing paginated conversation history.
    """
    conversations: List[StepConversation]
    total_conversations: int
    total_pages: int
    current_page: int
