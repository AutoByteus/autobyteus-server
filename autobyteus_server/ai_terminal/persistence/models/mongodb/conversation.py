
from repository_mongodb import BaseModel
from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId


class Message:
    """Embedded message schema for AI Terminal conversations."""
    
    def __init__(
        self,
        role: str,
        message: str,
        timestamp: datetime = None,
        token_count: Optional[int] = None,
        cost: Optional[float] = None
    ):
        self.role = role
        self.message = message
        self.timestamp = timestamp or datetime.utcnow()
        self.token_count = token_count
        self.cost = cost

    def to_dict(self) -> dict:
        """Convert message to dictionary representation."""
        return {
            "role": self.role,
            "message": self.message,
            "timestamp": self.timestamp,
            "token_count": self.token_count,
            "cost": self.cost
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Create message instance from dictionary."""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            from dateutil import parser
            timestamp = parser.isoparse(timestamp)
        elif not isinstance(timestamp, datetime):
            raise ValueError("Invalid timestamp format in message data.")
        
        return cls(
            role=data["role"],
            message=data["message"],
            timestamp=timestamp,
            token_count=data.get("token_count"),
            cost=data.get("cost")
        )


class AiTerminalConversation(BaseModel):
    """MongoDB model for AI Terminal conversations."""
    
    __collection_name__ = "ai_terminal_conversations"

    def __init__(
        self,
        conversation_id: str,
        created_at: datetime = None,
        messages: List[Dict] = None,
        **kwargs
    ):
        super().__init__(
            conversation_id=conversation_id,
            created_at=created_at or datetime.utcnow(),
            messages=messages or [],
            **kwargs
        )

    def add_message(
        self,
        role: str,
        message: str,
        token_count: Optional[int] = None,
        cost: Optional[float] = None
    ) -> Message:
        """Add a new message to the conversation."""
        new_message = Message(
            role=role,
            message=message,
            token_count=token_count,
            cost=cost
        )
        message_dict = new_message.to_dict()
        self.messages.append(message_dict)
        return new_message

    def get_messages(self, skip: int = 0, limit: Optional[int] = None) -> List[Dict]:
        """Get messages with pagination support."""
        paginated_messages = self.messages[skip:skip + limit] if limit else self.messages[skip:]
        return paginated_messages

    def to_dict(self) -> dict:
        """Convert conversation to dictionary representation."""
        data = {
            "conversation_id": self.conversation_id,
            "created_at": self.created_at,
            "messages": self.messages
        }
        if hasattr(self, '_id') and self._id is not None:
            data["_id"] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'AiTerminalConversation':
        """Create conversation instance from dictionary."""
        messages_data = data.get("messages", [])
        messages = [Message.from_dict(msg) for msg in messages_data]
        messages_dicts = [msg.to_dict() for msg in messages]
        
        conversation = cls(
            conversation_id=data.get("conversation_id"),
            created_at=data.get("created_at"),
            messages=messages_dicts,
            **{k: v for k, v in data.items() if k not in {"_id", "conversation_id", "created_at", "messages"}}
        )
        if "_id" in data:
            conversation._id = data["_id"]
        return conversation
