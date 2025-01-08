
import strawberry
from typing import List, Optional
from datetime import datetime

@strawberry.type
class Message:
    """GraphQL type mirroring the domain Message model"""
    message_id: Optional[str]
    role: str
    message: str
    timestamp: str
    context_paths: Optional[List[str]]
    original_message: Optional[str]
    token_count: Optional[int]
    cost: Optional[float]

@strawberry.type
class StepConversation:
    """GraphQL type mirroring the domain StepConversation model"""
    step_conversation_id: str
    step_name: str
    created_at: str
    messages: List[Message]

@strawberry.type
class ConversationHistory:
    """GraphQL type mirroring the domain ConversationHistory model"""
    conversations: List[StepConversation]
    total_conversations: int
    total_pages: int
    current_page: int
