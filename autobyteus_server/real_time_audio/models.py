from dataclasses import dataclass

@dataclass
class AudioChunk:
    data: bytes
    session_id: str
    workspace_id: str
    step_id: str
    timestamp: float