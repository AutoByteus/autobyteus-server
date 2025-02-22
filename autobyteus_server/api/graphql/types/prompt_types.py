import strawberry
from datetime import datetime
from typing import Optional

@strawberry.type
class Prompt:
    id: str
    name: str
    category: str
    prompt_text: str
    created_at: datetime
    updated_at: datetime
    parent_prompt_id: Optional[str] = None

@strawberry.input
class CreatePromptInput:
    name: str
    category: str
    prompt_text: str

@strawberry.input
class UpdatePromptInput:
    id: str
    new_prompt_text: str

@strawberry.input
class MarkActivePromptInput:
    id: str
