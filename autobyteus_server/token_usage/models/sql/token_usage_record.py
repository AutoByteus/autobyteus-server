
from sqlalchemy import Column, String, DateTime, Integer, Float
from datetime import datetime
import uuid
from repository_sqlalchemy import Base

class TokenUsageRecord(Base):
    __tablename__ = 'token_usage_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usage_record_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), nullable=False)  # Renamed from step_conversation_id
    conversation_type = Column(String, nullable=False)   # New attribute to specify the type of conversation
    role = Column(String, nullable=False)
    token_count = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert token usage record to dictionary representation."""
        return {
            "usage_record_id": self.usage_record_id,
            "conversation_id": self.conversation_id,  # Updated field
            "conversation_type": self.conversation_type,  # New field
            "role": self.role,
            "token_count": self.token_count,
            "cost": self.cost,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create TokenUsageRecord instance from dictionary."""
        record = cls(
            usage_record_id=data.get("usage_record_id", str(uuid.uuid4())),
            conversation_id=data["conversation_id"],  # Updated field
            conversation_type=data["conversation_type"],  # New field
            role=data["role"],
            token_count=data["token_count"],
            cost=data["cost"],
            created_at=data.get("created_at", datetime.utcnow())
        )
        return record
