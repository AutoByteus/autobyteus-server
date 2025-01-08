
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class TokenUsageRecord:
    """
    Domain model to record usage cost and token count for each message
    independently of the conversation, so cost isn't lost if the conversation is deleted.
    
    Attributes:
        token_usage_record_id (Optional[str]): Unique identifier for the token usage record.
        conversation_id (str): The ID of the conversation associated with this usage record.
        conversation_type (str): The type of conversation (e.g., WORKFLOW, AI_TERMINAL).
        role (str): The role of the message sender (e.g., user, assistant).
        token_count (int): The number of tokens used in the message.
        cost (float): The cost associated with the token usage.
        created_at (datetime): Timestamp when the usage record was created.
    """
    conversation_id: str  # Renamed from step_conversation_id to conversation_id
    conversation_type: str  # New attribute to specify the type of conversation
    role: str
    token_count: int
    cost: float
    created_at: datetime
    token_usage_record_id: Optional[str] = None
