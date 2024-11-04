from repository_mongodb import BaseModel
from bson import ObjectId
from datetime import datetime
from typing import List, Dict, Optional

class Message:
    """Embedded message schema for conversations."""
    
    def __init__(
        self,
        role: str,
        message: str,
        timestamp: datetime = None,
        original_message: Optional[str] = None,  # Keep original_message in DB model
        context_paths: Optional[List[str]] = None
    ):
        self.role = role
        self.message = message
        self.timestamp = timestamp or datetime.utcnow()
        self.original_message = original_message
        self.context_paths = context_paths or []

    def to_dict(self) -> dict:
        """Convert message to dictionary representation."""
        return {
            "role": self.role,
            "message": self.message,
            "timestamp": self.timestamp,
            "original_message": self.original_message,  # Keep original_message in DB model
            "context_paths": self.context_paths
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Create message instance from dictionary."""
        return cls(
            role=data["role"],
            message=data["message"],
            timestamp=data["timestamp"],
            original_message=data.get("original_message"),  # Keep original_message in DB model
            context_paths=data.get("context_paths", [])
        )

class StepConversation(BaseModel):
    __collection_name__ = "step_conversations"

    step_conversation_id: ObjectId
    step_name: str
    created_at: datetime
    messages: List[Dict]  # List of Message dictionaries

    def __init__(
        self,
        step_name: str,
        step_conversation_id: ObjectId = None,
        created_at: datetime = None,
        messages: List[Dict] = None,
        **kwargs
    ):
        """
        Initialize a new StepConversation with embedded messages.

        Args:
            step_name (str): Name of the step
            step_conversation_id (ObjectId, optional): Unique identifier
            created_at (datetime, optional): Creation timestamp
            messages (List[Dict], optional): List of message dictionaries
        """
        super().__init__(
            step_conversation_id=step_conversation_id or ObjectId(),
            step_name=step_name,
            created_at=created_at or datetime.utcnow(),
            messages=messages or [],
            **kwargs
        )

    def add_message(self, role: str, message: str, original_message: Optional[str] = None, context_paths: Optional[List[str]] = None) -> Message:
        """
        Add a new message to the conversation.

        Args:
            role (str): Role of the message sender
            message (str): Message content
            original_message (Optional[str]): The original user message, if applicable  # Use original_message in domain model
            context_paths (Optional[List[str]]): List of context file paths, if applicable

        Returns:
            Message: The newly created message
        """
        new_message = Message(role=role, message=message, original_message=original_message, context_paths=context_paths)  # Use original_message
        message_dict = new_message.to_dict()
        self.messages.append(message_dict)
        return new_message

    def get_messages(self, skip: int = 0, limit: Optional[int] = None) -> List[Message]:
        """
        Get messages with pagination support.

        Args:
            skip (int): Number of messages to skip
            limit (Optional[int]): Maximum number of messages to return

        Returns:
            List[Message]: List of messages
        """
        paginated_messages = self.messages[skip:skip + limit] if limit else self.messages[skip:]
        return [Message.from_dict(msg) for msg in paginated_messages]

    def to_dict(self) -> dict:
        """Convert conversation to dictionary representation."""
        return {
            "step_conversation_id": self.step_conversation_id,
            "step_name": self.step_name,
            "created_at": self.created_at,
            "messages": self.messages
        }