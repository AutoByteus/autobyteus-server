from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from repository_sqlalchemy import Base

class CostEntry(Base):
    __tablename__ = 'cost_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String, nullable=False)
    cost = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    conversation_id = Column(Integer, ForeignKey('step_conversations.id'), nullable=True)
    message_id = Column(Integer, ForeignKey('step_conversation_messages.id'), nullable=True)

    conversation = relationship("StepConversation", back_populates="cost_entries")
    message = relationship("StepConversationMessage", back_populates="cost_entry")