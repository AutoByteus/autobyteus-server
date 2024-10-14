"""
Module: workspace_mutations

This module provides GraphQL mutations related to workspace operations in the AutoByteus server.
It includes functionality for starting workflows, adding workspaces, and retrieving file content
within workspaces. These mutations serve as the interface between the GraphQL API and the
underlying workspace management system.

The module uses Strawberry for GraphQL schema definition and interacts with the WorkspaceManager
to perform operations on workspaces.
"""

import json
import logging
import os
import strawberry
from strawberry.types import Info
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.api.graphql.types.workspace_info import WorkspaceInfo

# Singleton instance of WorkspaceManager to manage all workspace operations
workspace_manager = WorkspaceManager()

# Set up logging for this module
logger = logging.getLogger(__name__)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def start_workflow(self, workspace_id: str) -> bool:
        """
        Starts the workflow associated with the provided workspace.

        This mutation attempts to initiate the workflow for the specified workspace. It first
        checks if the workspace exists, and if so, calls the start_workflow method on the
        workspace object.

        Args:
            workspace_id (str): The unique identifier of the workspace.

        Returns:
            bool: True if the workflow was started successfully, False otherwise.

        Raises:
            Exception: Any exception that occurs during the workflow start process is caught
                       and logged, returning False to indicate failure.
        """
        # Retrieve the workspace object using the provided ID
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            logger.error(f"Workspace with ID {workspace_id} not found.")
            return False
        
        # Attempt to start the workflow
        try:
            workspace.start_workflow()
            logger.info(f"Workflow started for workspace ID {workspace_id}.")
            return True
        except Exception as e:
            logger.error(f"Failed to start workflow for workspace ID {workspace_id}: {str(e)}")
            return False

    @strawberry.mutation
    def add_workspace(self, workspace_root_path: str) -> WorkspaceInfo:
        """
        Adds a new workspace to the workspace service or returns the existing one.

        This mutation attempts to add a new workspace with the given root path. If a workspace
        already exists at the specified path, it returns the existing workspace information.

        Args:
            workspace_root_path (str): The root path of the workspace to be added or retrieved.

        Returns:
            WorkspaceInfo: An object containing the workspace ID, name, and file explorer information.

        Raises:
            Exception: Any exception during the process is caught, logged, and re-raised.
        """
        try:
            # Attempt to add the workspace or retrieve existing one
            workspace = workspace_manager.add_workspace(workspace_root_path)
            logger.info(f"Workspace added/retrieved with ID {workspace.workspace_id} at path {workspace_root_path}.")
            
            # Construct and return the WorkspaceInfo object
            return WorkspaceInfo(
                workspace_id=workspace.workspace_id,
                name=workspace.name,
                file_explorer=workspace.file_explorer.to_json()
            )
        except Exception as e:
            error_message = f"Error while adding/retrieving workspace: {str(e)}"
            logger.error(error_message)
            raise  # Re-raise the exception after logging

    @strawberry.mutation
    def get_file_content(self, workspace_id: str, file_path: str) -> str:
        """
        Retrieves the content of the specified file within the workspace.

        This mutation fetches the content of a file given its path within a specific workspace.
        It performs several checks to ensure the workspace and file exist before attempting to
        read the file content.

        Args:
            workspace_id (str): The unique identifier of the workspace.
            file_path (str): The relative path to the file within the workspace.

        Returns:
            str: A JSON string containing either the file content or an error message.
                 Format: {"content": "<file_content>"} or {"error": "<error_message>"}

        Note:
            The file_path is expected to be relative to the workspace root path.
        """
        # Retrieve the workspace object
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            error_message = f"Workspace with ID {workspace_id} not found."
            logger.error(error_message)
            return json.dumps({"error": error_message})

        # Construct the full file path
        full_path = os.path.join(workspace.root_path, file_path)
        logger.debug(f"Resolving file path: {full_path}")

        # Check if the file exists
        if not os.path.exists(full_path):
            error_message = f"File not found: {full_path}"
            logger.error(error_message)
            return json.dumps({"error": error_message})

        # Attempt to read and return the file content
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            logger.info(f"File content retrieved for {full_path}.")
            return json.dumps({"content": content})
        except Exception as e:
            error_message = f"Error reading file {full_path}: {str(e)}"
            logger.error(error_message)
            return json.dumps({"error": error_message})