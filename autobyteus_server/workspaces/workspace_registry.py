# autobyteus_server/workspaces/workspace_registry.py
"""
This module provides a registry for storing workspaces.

Workspaces are stored in two dictionaries: one with the workspace ID as the key, 
and another with the root path of a workspace as the key. Both dictionaries store 
the corresponding Workspace object as the value.
"""

from typing import Dict, Optional
from autobyteus.utils.singleton import SingletonMeta

from autobyteus_server.workspaces.workspace import Workspace


class WorkspaceRegistry(metaclass=SingletonMeta):
    """
    A registry to store workspaces.

    Attributes:
        id_to_workspace (Dict[str, Workspace]): A dictionary mapping workspace IDs to
            their corresponding Workspace.
        root_path_to_workspace (Dict[str, Workspace]): A dictionary mapping workspace root paths to 
            their corresponding Workspace.
    """

    def __init__(self):
        """
        Initialize WorkspaceRegistry.
        """
        self.id_to_workspace: Dict[str, Workspace] = {}
        self.root_path_to_workspace: Dict[str, Workspace] = {}

    def add_workspace(self, workspace: Workspace) -> None:
        """
        Adds a workspace to the registry.

        Args:
            workspace (Workspace): The workspace to be added.
        """
        self.id_to_workspace[workspace.workspace_id] = workspace
        self.root_path_to_workspace[workspace.root_path] = workspace

    def get_workspace_by_id(self, workspace_id: str) -> Optional[Workspace]:
        """
        Retrieves a workspace from the registry using its ID.

        Args:
            workspace_id (str): The ID of the workspace.

        Returns:
            Optional[Workspace]: The workspace if it exists, None otherwise.
        """
        return self.id_to_workspace.get(workspace_id)

    def get_workspace_by_root_path(self, root_path: str) -> Optional[Workspace]:
        """
        Retrieves a workspace from the registry using its root path.

        Args:
            root_path (str): The root path of the workspace.

        Returns:
            Optional[Workspace]: The workspace if it exists, None otherwise.
        """
        return self.root_path_to_workspace.get(root_path)

    def workspace_exists_by_id(self, workspace_id: str) -> bool:
        """
        Checks if a workspace already exists in the registry using its ID.

        Args:
            workspace_id (str): The ID of the workspace.

        Returns:
            bool: True if the workspace exists, False otherwise.
        """
        return workspace_id in self.id_to_workspace

    def workspace_exists_by_root_path(self, root_path: str) -> bool:
        """
        Checks if a workspace already exists in the registry using its root path.

        Args:
            root_path (str): The root path of the workspace.

        Returns:
            bool: True if the workspace exists, False otherwise.
        """
        return root_path in self.root_path_to_workspace