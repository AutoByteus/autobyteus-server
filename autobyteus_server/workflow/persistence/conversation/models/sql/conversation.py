from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from repository_sqlalchemy import Base

class StepConversation(Base):
    __tablename__ = 'step_conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    step_conversation_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    step_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    messages = relationship("StepConversationMessage", back_populates="conversation", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "step_conversation_id": self.step_conversation_id,
            "step_name": self.step_name,
            "created_at": self.created_at,
            "messages": [message.to_dict() for message in self.messages]
        }

    @classmethod
    def from_dict(cls, data):
        conversation = cls(
            step_conversation_id=data["step_conversation_id"],
            step_name=data["step_name"],
            created_at=data["created_at"]
        )
        # Messages can be added separately
        return conversation