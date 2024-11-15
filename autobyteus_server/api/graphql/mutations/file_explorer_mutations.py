# File: autobyteus-server/autobyteus_server/api/graphql/mutations/file_explorer_mutations.py

"""
This module contains GraphQL mutations for file explorer operations.

It provides functionality to apply changes to files within a workspace.
"""

import json
import logging
import strawberry
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager

workspace_manager = WorkspaceManager()

logger = logging.getLogger(__name__)

@strawberry.type
class Mutation:
    """
    A class containing GraphQL mutations for file explorer operations.
    """

    @strawberry.mutation
    def apply_file_change(self, workspace_id: str, file_path: str, content: str) -> str:
        """
        Applies changes to a file by overwriting its content.

        This mutation takes the workspace ID, the relative path of the file
        to be modified, and the new content to be written to the file. It then
        attempts to write the new content to the specified file.

        Args:
            workspace_id (str): The ID of the workspace.
            file_path (str): The relative path of the file to be modified from the workspace root.
            content (str): The new content to be written to the file.

        Returns:
            str: A JSON string containing the changes made to the file.

        Raises:
            FileNotFoundError: If the specified file is not found.
            PermissionError: If there's no permission to write to the file.
            ValueError: If there's an issue with the input values.
            Exception: For any other unexpected errors.

        Example:
            mutation {
                applyFileChange(
                    workspaceId: "123e4567-e89b-12d3-a456-426614174000",
                    filePath: "src/utils/helpers.py",
                    content: "New file content"
                )
            }
        """
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        file_explorer = workspace.get_file_explorer()
        change_event = file_explorer.write_file_content(file_path, content)
        return json.dumps(change_event.to_dict())