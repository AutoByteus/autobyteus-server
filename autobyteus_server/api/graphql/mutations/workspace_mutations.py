"""
Module: workspace_mutations

This module provides GraphQL mutations related to workspace operations in the AutoByteus server.
It includes functionality for starting workflows and adding workspaces. These mutations serve as 
the interface between the GraphQL API and the underlying workspace management system.

The module uses Strawberry for GraphQL schema definition and interacts with the WorkspaceManager
to perform operations on workspaces.
"""

import logging
import strawberry
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.api.graphql.types.workspace_info import WorkspaceInfo

# Singleton instance of WorkspaceManager to manage all workspace operations
workspace_manager = WorkspaceManager()

# Set up logging for this module
logger = logging.getLogger(__name__)


@strawberry.type
class CommandExecutionResult:
    success: bool
    message: str

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
    def execute_bash_commands(self, workspace_id: str, command: str) -> CommandExecutionResult:
        """
        Executes a bash command within the specified workspace.

        Args:
            workspace_id (str): The unique identifier of the workspace.
            command (str): The bash command to be executed.

        Returns:
            CommandExecutionResult: The result of the command execution.
        """
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            logger.error(f"Workspace with ID {workspace_id} not found.")
            return CommandExecutionResult(success=False, message="Workspace not found.")

        result = workspace.execute_command(command)
        return CommandExecutionResult(
            success=result.success,
            message=result.message
        )