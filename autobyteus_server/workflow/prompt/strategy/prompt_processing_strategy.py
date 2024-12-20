from abc import ABC, abstractmethod
from typing import Optional
from autobyteus_server.workspaces.workspace import Workspace

class PromptProcessingStrategy(ABC):
    """Base class for prompt processing strategies."""
    
    @abstractmethod
    def process(self, prompt: str, workspace: Optional[Workspace] = None) -> str:
        """Process the prompt according to the strategy."""
        pass