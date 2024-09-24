# autobyteus_server/workspaces/workspace_registry.py
"""
This module provides a registry for storing workspaces.

Workspaces are stored in a dictionary, with the root path of a workspace as the key, 
and the corresponding Workspace object as the value.
"""

from typing import Dict, Optional
from autobyteus.utils.singleton import SingletonMeta

from autobyteus_server.workspaces.workspace import Workspace


class WorkspaceRegistry(metaclass=SingletonMeta):
    """
    A registry to store workspaces.

    Attributes:
        workspaces (Dict[str, Workspace]): A dictionary mapping workspace root paths to 
            their corresponding Workspace.
    """

    def __init__(self):
        """
        Initialize WorkspaceRegistry.
        """
        self.workspaces: Dict[str, Workspace] = {}

    def add_workspace(self, workspace_root_path: str, workspace: Workspace) -> None:
        """
        Adds a workspace to the registry.

        Args:
            workspace_root_path (str): The root path of the workspace.
            workspace (Workspace): The workspace to be added.
        """
        self.workspaces[workspace_root_path] = workspace

    def get_workspace(self, workspace_root_path: str) -> Optional[Workspace]:
        """
        Retrieves a workspace from the registry.

        Args:
            workspace_root_path (str): The root path of the workspace.

        Returns:
            Optional[Workspace]: The workspace if it exists, None otherwise.
        """
        return self.workspaces.get(workspace_root_path)

    def workspace_exists(self, workspace_root_path: str) -> bool:
        """
        Checks if a workspace already exists in the registry.

        Args:
            workspace_root_path (str): The root path of the workspace.

        Returns:
            bool: True if the workspace exists, False otherwise.
        """
        return workspace_root_path in self.workspaces