
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from repository_sqlalchemy import Base

class AiTerminalConversationMessage(Base):
    __tablename__ = 'ai_terminal_conversation_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('ai_terminal_conversations.id'), nullable=False)
    role = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    token_count = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)

    conversation = relationship("AiTerminalConversation", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "message": self.message,
            "timestamp": self.timestamp,
            "token_count": self.token_count,
            "cost": self.cost
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            conversation_id=data["conversation_id"],
            role=data["role"],
            message=data["message"],
            timestamp=data.get("timestamp", datetime.utcnow()),
            token_count=data.get("token_count"),
            cost=data.get("cost")
        )
