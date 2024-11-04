from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from repository_sqlalchemy import Base
from datetime import datetime

class StepConversationMessage(Base):
    __tablename__ = "step_conversation_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    step_conversation_id = Column(Integer, ForeignKey('step_conversations.id'), nullable=False)
    role = Column(String(50), nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    original_message = Column(String, nullable=True)  # New field
    context_paths = Column(String, nullable=True)      # New field, stored as JSON string
    
    step_conversation = relationship("StepConversation", back_populates="messages")

    __table_args__ = (
        Index('idx_step_conversation_messages_conversation_id_timestamp', 'step_conversation_id', 'timestamp'),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "step_conversation_id": self.step_conversation_id,
            "role": self.role,
            "message": self.message,
            "timestamp": self.timestamp,
            "original_message": self.original_message,
            "context_paths": self.context_paths
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'StepConversationMessage':
        return cls(
            id=data.get("id"),
            step_conversation_id=data.get("step_conversation_id"),
            role=data.get("role"),
            message=data.get("message"),
            timestamp=data.get("timestamp"),
            original_message=data.get("original_message"),
            context_paths=data.get("context_paths")
        )