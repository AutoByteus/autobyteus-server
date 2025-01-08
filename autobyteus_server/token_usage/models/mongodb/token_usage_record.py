
from repository_mongodb import BaseModel
from bson import ObjectId
from datetime import datetime
from typing import Optional

class MongoTokenUsageRecord(BaseModel):
    __collection_name__ = "token_usage_records"

    conversation_id: str  # Renamed from step_conversation_id to conversation_id
    conversation_type: str  # New attribute to specify the type of conversation
    role: str
    token_count: int
    cost: float
    created_at: datetime

    def __init__(
        self,
        conversation_id: str,
        conversation_type: str,  # New attribute
        role: str,
        token_count: int,
        cost: float,
        created_at: Optional[datetime] = None,
        **kwargs
    ):
        super().__init__(
            conversation_id=conversation_id,
            conversation_type=conversation_type,  # Initialize new attribute
            role=role,
            token_count=token_count,
            cost=cost,
            created_at=created_at or datetime.utcnow(),
            **kwargs
        )

    def to_dict(self) -> dict:
        """Convert token usage record to dictionary representation."""
        data = {
            "conversation_id": self.conversation_id,
            "conversation_type": self.conversation_type,  # Include new attribute
            "role": self.role,
            "token_count": self.token_count,
            "cost": self.cost,
            "created_at": self.created_at
        }
        if hasattr(self, '_id') and self._id is not None:
            data["_id"] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'MongoTokenUsageRecord':
        """Create token usage record instance from dictionary."""
        return cls(
            conversation_id=data["conversation_id"],  # Updated field
            conversation_type=data["conversation_type"],  # New field
            role=data["role"],
            token_count=data["token_count"],
            cost=data["cost"],
            created_at=data.get("created_at"),
            **{k: v for k, v in data.items() if k not in {
                "_id", "conversation_id", "conversation_type", "role", "token_count", "cost", "created_at"
            }}
        )
