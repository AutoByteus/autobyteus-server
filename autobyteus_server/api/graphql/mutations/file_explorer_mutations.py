# File: autobyteus_server/api/graphql/mutations/file_explorer_mutations.py

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
    def apply_file_change(self, workspace_root_path: str, file_path: str, content: str) -> str:
        """
        Applies changes to a file by overwriting its content.

        This mutation takes the workspace root path, the absolute path of the file
        to be modified, and the new content to be written to the file. It then
        attempts to write the new content to the specified file.

        Args:
            workspace_root_path (str): The root path of the workspace.
            file_path (str): The absolute path of the file to be modified.
            content (str): The new content to be written to the file.

        Returns:
            str: A JSON string indicating success or failure. The string will
                 contain either a success message or an error message.

        Raises:
            FileNotFoundError: If the specified file is not found.
            PermissionError: If there's no permission to write to the file.
            ValueError: If there's an issue with the input values.
            Exception: For any other unexpected errors.

        Example:
            mutation {
                applyFileChange(
                    workspaceRootPath: "/path/to/workspace",
                    filePath: "/path/to/workspace/file.txt",
                    content: "New file content"
                )
            }
        """
        try:
            workspace = workspace_manager.get_workspace(workspace_root_path)
            if not workspace:
                return json.dumps({"error": "Workspace not found"})

            file_explorer = workspace.get_file_explorer()
            file_explorer.write_file_content(file_path, content)
            return json.dumps({"success": True, "message": "File updated successfully"})
        except FileNotFoundError as e:
            return json.dumps({"error": f"File not found: {str(e)}"})
        except PermissionError as e:
            return json.dumps({"error": f"Permission denied: {str(e)}"})
        except ValueError as e:
            return json.dumps({"error": str(e)})
        except Exception as e:
            logger.error(f"Error applying file change: {str(e)}")
            return json.dumps({"error": "An unexpected error occurred while updating the file"})