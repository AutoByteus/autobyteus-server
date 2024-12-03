from repository_mongodb import BaseModel
from bson import ObjectId
from datetime import datetime
from typing import List, Dict, Optional

class Message:
    def __init__(
        self,
        role: str,
        message: str,
        timestamp: datetime = None,
        original_message: Optional[str] = None,
        context_paths: Optional[List[str]] = None,
        cost: float = 0.0  # Added cost attribute
    ):
        self.role = role
        self.message = message
        self.timestamp = timestamp or datetime.utcnow()
        self.original_message = original_message
        self.context_paths = context_paths or []
        self.cost = cost

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "message": self.message,
            "timestamp": self.timestamp,
            "original_message": self.original_message,
            "context_paths": self.context_paths,
            "cost": self.cost  # Include cost
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
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
            original_message=data.get("original_message"),
            context_paths=data.get("context_paths", []),
            cost=data.get("cost", 0.0)  # Get cost from data or default to 0.0
        )

class StepConversation(BaseModel):
    __collection_name__ = "step_conversations"

    step_name: str
    created_at: datetime
    messages: List[Dict]

    def __init__(
        self,
        step_name: str,
        created_at: datetime = None,
        messages: List[Dict] = None,
        **kwargs
    ):
        super().__init__(
            step_name=step_name,
            created_at=created_at or datetime.utcnow(),
            messages=messages or [],
            **kwargs
        )

    def add_message(self, role: str, message: str, original_message: Optional[str] = None, context_paths: Optional[List[str]] = None, cost: float = 0.0) -> Message:
        new_message = Message(role=role, message=message, original_message=original_message, context_paths=context_paths, cost=cost)
        message_dict = new_message.to_dict()
        self.messages.append(message_dict)
        return new_message

    def get_messages(self, skip: int = 0, limit: Optional[int] = None) -> List[Dict]:
        paginated_messages = self.messages[skip:skip + limit] if limit else self.messages[skip:]
        return paginated_messages

    def to_dict(self) -> dict:
        data = {
            "step_name": self.step_name,
            "created_at": self.created_at,
            "messages": self.messages,
            "total_cost": self.total_cost
        }
        if hasattr(self, '_id') and self._id is not None:
            data["_id"] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'StepConversation':
        messages_data = data.get("messages", [])
        messages = [Message.from_dict(msg) for msg in messages_data]
        messages_dicts = [msg.to_dict() for msg in messages]
        
        conversation = cls(
            step_name=data.get("step_name"),
            created_at=data.get("created_at"),
            messages=messages_dicts,
            **{k: v for k, v in data.items() if k not in {"_id", "step_name", "created_at", "messages"}}
        )
        if "_id" in data:
            conversation._id = data["_id"]
        return conversation