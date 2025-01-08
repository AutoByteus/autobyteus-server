
import strawberry
from typing import Optional

@strawberry.type
class StepResponse:
    conversation_id: str
    message_chunk: str
    is_complete: bool
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    prompt_cost: Optional[float] = None
    completion_cost: Optional[float] = None
    total_cost: Optional[float] = None
