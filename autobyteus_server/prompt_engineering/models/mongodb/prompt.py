from repository_mongodb import BaseModel
from bson import ObjectId
from datetime import datetime
from typing import Optional

class Prompt(BaseModel):
    __collection_name__ = "prompts"

    name: str
    category: str
    prompt_text: str
    created_at: datetime
    updated_at: datetime
    # New field for versioning
    parent_id: Optional[str] = None
    # New attribute for active prompt marking
    is_active: bool = True

    def __init__(
        self,
        name: str,
        category: str,
        prompt_text: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        parent_id: Optional[str] = None,
        is_active: bool = True,
        **kwargs
    ):
        super().__init__(
            name=name,
            category=category,
            prompt_text=prompt_text,
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow(),
            parent_id=parent_id,
            is_active=is_active,
            **kwargs
        )
        self.parent_id = parent_id
        self.is_active = is_active

    def to_dict(self) -> dict:
        data = {
            "name": self.name,
            "category": self.category,
            "prompt_text": self.prompt_text,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "parent_id": self.parent_id,
            "is_active": self.is_active
        }
        if hasattr(self, '_id') and self._id is not None:
            data["_id"] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Prompt':
        prompt = cls(
            name=data["name"],
            category=data["category"],
            prompt_text=data["prompt_text"],
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
            parent_id=data.get("parent_id"),
            is_active=data.get("is_active", True)
        )
        if "_id" in data:
            prompt._id = data["_id"]
        return prompt
