from typing import List, Optional
from .strategy.prompt_processing_strategy import PromptProcessingStrategy
from autobyteus_server.workspaces.workspace import Workspace

class PromptProcessor:
    """Manages and applies prompt processing strategies."""
    
    def __init__(self, strategies: Optional[List[PromptProcessingStrategy]] = None):
        """
        Initialize with list of strategies.
        
        Args:
            strategies: Optional list of PromptProcessingStrategy instances
        """
        self.strategies = strategies or []
        
    def add_strategy(self, strategy: PromptProcessingStrategy) -> None:
        """Add a new processing strategy."""
        self.strategies.append(strategy)
        
    def process(self, prompt: str, workspace: Optional[Workspace] = None) -> str:
        """
        Process prompt through all registered strategies.
        
        Args:
            prompt: The prompt to process
            workspace: Optional workspace instance passed to strategies
            
        Returns:
            Processed prompt
        """
        result = prompt
        for strategy in self.strategies:
            result = strategy.process(result, workspace)
        return result