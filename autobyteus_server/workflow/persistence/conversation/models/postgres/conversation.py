from sqlalchemy import Column, Integer, String, DateTime, func, Index
from sqlalchemy.orm import relationship
from repository_sqlalchemy import Base
from datetime import datetime
import uuid

class StepConversation(Base):
    __tablename__ = "step_conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    step_conversation_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    step_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("StepConversationMessage", back_populates="step_conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_step_conversations_name', 'step_name'),
        Index('idx_step_conversations_uuid', 'step_conversation_id'),
    )