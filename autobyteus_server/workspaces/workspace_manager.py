# autobyteus_server/workspaces/workspace_manager.py
"""
This module provides a manager for handling operations related to workspaces.

This manager is responsible for adding workspaces, building their directory structures, 
and maintaining their settings. A workspace is represented by its root path, 
and its setting is stored in a dictionary, with the root path as the key. 
Upon successful addition of a workspace, a directory tree structure represented 
by TreeNode objects is returned.
"""

import logging
from typing import Optional

from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus.utils.singleton import SingletonMeta
from autobyteus_server.workspaces.workspace import Workspace
from autobyteus_server.workspaces.workspace_registry import WorkspaceRegistry
from autobyteus_server.workspaces.workspace_tools.project_type_determiner import ProjectTypeDeterminer

from autobyteus_server.workflow.automated_coding_workflow import AutomatedCodingWorkflow
from autobyteus_server.workspaces.errors.workspace_already_exists_error import WorkspaceAlreadyExistsError

logger = logging.getLogger(__name__)

class WorkspaceManager(metaclass=SingletonMeta):
    """
    Manager to handle operations related to workspaces.

    Attributes:
        workspace_registry (WorkspaceRegistry): A registry to store workspaces.
    """

    def __init__(self):
        """
        Initialize WorkspaceManager.
        """
        self.workspace_registry = WorkspaceRegistry()
        self.project_type_determiner = ProjectTypeDeterminer()

    def get_workspace_file_explorer(self, workspace_root_path: str) -> Optional[FileExplorer]:
        """
        Retrieves the FileExplorer for a given workspace path if it exists.

        Args:
            workspace_root_path (str): The root path of the workspace.

        Returns:
            Optional[FileExplorer]: The FileExplorer object if the workspace exists, None otherwise.
        """
        workspace = self.workspace_registry.get_workspace(workspace_root_path)
        return workspace.file_explorer if workspace else None

    def add_workspace(self, workspace_root_path: str) -> FileExplorer:
        """
        Adds a workspace to the workspace registry.
        If the workspace already exists, it raises a WorkspaceAlreadyExistsError.
        If the workspace doesn't exist, it builds the directory tree of the workspace
        and initializes an AutomatedCodingWorkflow for the workspace.

        Args:
            workspace_root_path (str): The root path of the workspace.

        Returns:
            FileExplorer: The FileExplorer object representing the workspace directory tree.

        Raises:
            WorkspaceAlreadyExistsError: If the workspace already exists.
        """
        if self.workspace_registry.get_workspace(workspace_root_path):
            raise WorkspaceAlreadyExistsError(f"Workspace at {workspace_root_path} already exists")

        # Determine the project type
        project_type = self.project_type_determiner.determine(workspace_root_path)
        
        # Build the directory tree
        file_explorer = FileExplorer(workspace_root_path)
        file_explorer.build_workspace_directory_tree()
        
        # Create the workflow
        workflow = AutomatedCodingWorkflow()
        
        # Create and register the Workspace
        workspace = Workspace(root_path=workspace_root_path, project_type=project_type, 
                              file_explorer=file_explorer, workflow=workflow)
        self.workspace_registry.add_workspace(workspace_root_path, workspace)

        return file_explorer

    def get_workspace(self, workspace_root_path: str) -> Optional[Workspace]:
        """
        Retrieves a workspace from the workspace registry.

        Args:
            workspace_root_path (str): The root path of the workspace.

        Returns:
            Optional[Workspace]: The workspace if it exists, None otherwise.
        """
        return self.workspace_registry.get_workspace(workspace_root_path)