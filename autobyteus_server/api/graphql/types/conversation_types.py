import strawberry
from typing import List, Optional
from datetime import datetime

@strawberry.type
class Message:
    """GraphQL type mirroring the domain Message model"""
    message_id: Optional[str]
    role: str
    message: str  # Changed from content to message
    timestamp: str
    context_paths: Optional[List[str]]  # Included context_paths
    original_message: Optional[str]      # Changed from original_content to original_message

@strawberry.type
class StepConversation:
    """GraphQL type mirroring the domain StepConversation model"""
    step_conversation_id: str
    step_name: str
    created_at: str
    messages: List[Message]
    total_cost: float  # Added total_cost field

@strawberry.type
class ConversationHistory:
    """GraphQL type mirroring the domain ConversationHistory model"""
    conversations: List[StepConversation]
    total_conversations: int
    total_pages: int
    current_page: int