from sqlalchemy import Column, String, DateTime, Integer, Boolean
from datetime import datetime
from typing import Optional
from repository_sqlalchemy import Base

class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    prompt_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # New column for versioning
    parent_id = Column(Integer, nullable=True)
    # New column to mark active prompt
    is_active = Column(Boolean, default=True, nullable=False)

    def __init__(
        self,
        name: str,
        category: str,
        prompt_text: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        parent_id: Optional[int] = None,
        is_active: bool = True
    ):
        self.name = name
        self.category = category
        self.prompt_text = prompt_text
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.parent_id = parent_id
        self.is_active = is_active

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "prompt_text": self.prompt_text,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "parent_id": self.parent_id,
            "is_active": self.is_active
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            category=data["category"],
            prompt_text=data["prompt_text"],
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
            parent_id=data.get("parent_id"),
            is_active=data.get("is_active", True)
        )
