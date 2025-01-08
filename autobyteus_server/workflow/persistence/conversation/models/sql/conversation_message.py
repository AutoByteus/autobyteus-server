
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from repository_sqlalchemy import Base

class StepConversationMessage(Base):
    __tablename__ = 'step_conversation_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    step_conversation_id = Column(Integer, ForeignKey('step_conversations.id'), nullable=False)
    role = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    original_message = Column(Text, nullable=True)
    context_paths = Column(Text, nullable=True)  # JSON serialized list
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # New fields for usage/cost
    token_count = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)

    conversation = relationship("StepConversation", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "step_conversation_id": self.step_conversation_id,
            "role": self.role,
            "message": self.message,
            "original_message": self.original_message,
            "context_paths": self.context_paths,
            "timestamp": self.timestamp,
            "token_count": self.token_count,
            "cost": self.cost
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            step_conversation_id=data["step_conversation_id"],
            role=data["role"],
            message=data["message"],
            original_message=data.get("original_message"),
            context_paths=data.get("context_paths"),
            timestamp=data["timestamp"],
            token_count=data.get("token_count"),
            cost=data.get("cost")
        )
