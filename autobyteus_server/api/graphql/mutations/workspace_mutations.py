"""
Module: workspace_mutations

This module provides GraphQL mutations related to workspace operations.
"""

import json
import logging
import strawberry
from strawberry.scalars import JSON
from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.workspaces.errors.workspace_already_exists_error import WorkspaceAlreadyExistsError

# Singleton instances
workspace_manager = WorkspaceManager()

# Logger setup
logger = logging.getLogger(__name__)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def start_workflow(self, workspace_root_path: str) -> bool:
        """
        Starts the workflow associated with the provided workspace.

        Args:
            workspace_root_path (str): The root path of the workspace.

        Returns:
            bool: True if the workflow was started successfully, otherwise False.
        """

    @strawberry.mutation
    def add_workspace(self, workspace_root_path: str) -> JSON:
        """
        Adds a new workspace to the workspace service or returns the existing one,
        and returns a JSON representation of the workspace directory tree.

        Args:
            workspace_root_path (str): The root path of the workspace to be added or retrieved.

        Returns:
            JSON: The JSON representation of the workspace directory tree.
        """
        try:
            file_explorer = workspace_manager.get_file_explorer(workspace_root_path)
            if file_explorer is None:
                file_explorer = workspace_manager.add_workspace(workspace_root_path)
            return file_explorer.to_json()
        except WorkspaceAlreadyExistsError as e:
            error_message = str(e)
            logger.info(error_message)
            return json.dumps({"error": error_message})
        except Exception as e:
            error_message = f"Error while adding/retrieving workspace: {str(e)}"
            logger.error(error_message)
            return json.dumps({"error": error_message})