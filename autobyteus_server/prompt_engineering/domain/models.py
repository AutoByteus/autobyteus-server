from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Prompt:
    name: str
    category: str
    prompt_text: str
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Field for versioning: links to the parent prompt (if any)
    parent_id: Optional[str] = None
    # New attribute to mark the active (effective) prompt
    is_active: bool = True
