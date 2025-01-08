
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from repository_sqlalchemy import Base

class AiTerminalConversation(Base):
    __tablename__ = 'ai_terminal_conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    messages = relationship("AiTerminalConversationMessage", back_populates="conversation", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "created_at": self.created_at,
            "messages": [message.to_dict() for message in self.messages]
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            conversation_id=data.get("conversation_id"),
            created_at=data.get("created_at", datetime.utcnow())
        )
