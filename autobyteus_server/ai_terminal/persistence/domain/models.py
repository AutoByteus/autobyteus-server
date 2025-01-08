
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class AiTerminalMessage:
    """
    Domain model representing a message in the AI Terminal conversation.
    Provides a persistence-agnostic representation of a message.
    """
    role: str
    message: str
    timestamp: datetime
    message_id: Optional[str] = None
    token_count: Optional[int] = None
    cost: Optional[float] = None

@dataclass
class AiTerminalConversation:
    """
    Domain model representing an entire AI Terminal conversation.
    Provides a persistence-agnostic representation of a conversation.
    """
    conversation_id: str
    created_at: datetime
    messages: List[AiTerminalMessage]

@dataclass
class ConversationHistory:
    """
    Domain model representing paginated conversation history.
    """
    conversations: List[AiTerminalConversation]
    total_conversations: int
    total_pages: int
    current_page: int
