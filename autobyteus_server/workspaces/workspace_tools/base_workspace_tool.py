"""
Module: base_workspace_tool

This module provides the base class for all workspace-specific tools.
Each tool should inherit from the `BaseWorkspaceTool` class and provide
necessary implementations.
"""
from abc import ABC, abstractmethod
from autobyteus.prompt.prompt_template import PromptTemplate
from autobyteus_server.workflow.utils.unique_id_generator import UniqueIDGenerator

from autobyteus_server.workspaces.workspace import Workspace

class BaseWorkspaceTool(ABC):
    """
    BaseWorkspaceTool is the abstract base class for all workspace-specific tools.
    Each tool should inherit from this class, provide a unique name, and implement
    the required methods.
    """
    name: str = None
    prompt_template: PromptTemplate = None

    def __init__(self, workspace: Workspace):
        """
        Constructor for BaseWorkspaceTool.

        Args:
            workspace (Workspace): The workspace associated with this tool.
        """
        self.id = UniqueIDGenerator.generate_id()
        self.workspace = workspace

    def to_dict(self) -> dict:
        """
        Converts the BaseWorkspaceTool instance to a dictionary representation.

        Returns:
            dict: Dictionary representation of the BaseWorkspaceTool instance.
        """
        return {
            "id": self.id,
            "name": self.name,
            "prompt_template": self.prompt_template.to_dict() if self.prompt_template else None
        }

    @abstractmethod
    def execute(self):
        """
        Execute the tool's main functionality. This method should be implemented by subclasses.
        
        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")