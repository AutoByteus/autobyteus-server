from datetime import datetime
from typing import Optional

class CostEntry:
    def __init__(
        self,
        role: str,
        step_name: str,
        cost: float,
        timestamp: datetime,
        conversation_id: Optional[str] = None,
        message_id: Optional[str] = None,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.role = role
        self.step_name = step_name
        self.cost = cost
        self.timestamp = timestamp
        self.conversation_id = conversation_id
        self.message_id = message_id

    def to_dict(self):
        data = {
            "role": self.role,
            "step_name": self.step_name,
            "cost": self.cost,
            "timestamp": self.timestamp,
            "conversation_id": self.conversation_id,
            "message_id": self.message_id
        }
        if self._id:
            data["_id"] = self._id
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            role=data["role"],
            step_name=data["step_name"],
            cost=data["cost"],
            timestamp=data["timestamp"],
            conversation_id=data.get("conversation_id"),
            message_id=data.get("message_id"),
            _id=str(data.get("_id"))
        )