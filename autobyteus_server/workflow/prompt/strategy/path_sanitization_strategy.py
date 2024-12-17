import os
import re
from typing import Optional
from .prompt_processing_strategy import PromptProcessingStrategy
from autobyteus_server.workspaces.workspace import Workspace

class PathSanitizationStrategy(PromptProcessingStrategy):
    """Strategy for sanitizing absolute paths in prompts."""

    def process(self, prompt: str, workspace: Optional[Workspace] = None) -> str:
        """
        Process the prompt by removing absolute workspace paths.
        
        Args:
            prompt: The prompt to process
            workspace: Optional workspace instance to get the root path
            
        Returns:
            Processed prompt with sanitized paths
        """
        if not workspace or not prompt:
            return prompt
            
        workspace_path = os.path.normpath(workspace.root_path)
        
        # Escape special regex characters in workspace path
        escaped_path = re.escape(workspace_path)
        
        # Replace absolute paths with relative ones
        # Handle both forward and backward slashes
        pattern = f"{escaped_path}[/\\\\]?(.*?)(?=\\s|$)"
        processed = re.sub(pattern, r'\1', prompt)
        
        return processed