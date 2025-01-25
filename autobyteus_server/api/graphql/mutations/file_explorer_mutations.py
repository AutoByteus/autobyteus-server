import logging
import strawberry
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.file_explorer.file_system_changes import serialize_change_event

workspace_manager = WorkspaceManager()
logger = logging.getLogger(__name__)

@strawberry.type
class Mutation:
    """
    A class containing GraphQL mutations for file explorer operations.
    """

    @strawberry.mutation
    def write_file_content(self, workspace_id: str, file_path: str, content: str) -> str:
        """
        Writes new content to the specified file.

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
        """
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        file_explorer = workspace.get_file_explorer()
        change_event = file_explorer.write_file_content(file_path, content)
        return serialize_change_event(change_event)

    @strawberry.mutation
    def delete_file_or_folder(self, workspace_id: str, path: str) -> str:
        """
        Deletes a file or folder from the workspace.

        Args:
            workspace_id (str): The ID of the workspace.
            path (str): The relative path of the file or folder to be deleted.

        Returns:
            str: A JSON string containing the changes made to the filesystem.

        Raises:
            FileNotFoundError: If the specified path is not found.
            PermissionError: If there's no permission to delete.
            ValueError: If there's an issue with the input values.
            Exception: For any other unexpected errors.
        """
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        file_explorer = workspace.get_file_explorer()
        change_event = file_explorer.remove_file_or_folder(path)
        return serialize_change_event(change_event)

    @strawberry.mutation
    def move_file_or_folder(self, workspace_id: str, source_path: str, destination_path: str) -> str:
        """
        Moves or renames a file or folder within the workspace.

        Args:
            workspace_id (str): The ID of the workspace.
            source_path (str): The relative path of the file or folder to be moved.
            destination_path (str): The relative destination path.

        Returns:
            str: A JSON string containing the changes made to the filesystem.

        Raises:
            FileNotFoundError: If the source path is not found.
            PermissionError: If there's no permission to move.
            ValueError: If there's an issue with the input values.
            Exception: For any other unexpected errors.
        """
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        file_explorer = workspace.get_file_explorer()
        change_event = file_explorer.move_file_or_folder(source_path, destination_path)
        return serialize_change_event(change_event)

    @strawberry.mutation
    def rename_file_or_folder(self, workspace_id: str, target_path: str, new_name: str) -> str:
        """
        Renames a file or folder within the same directory. The node's ID should remain the same.

        Args:
            workspace_id (str): The ID of the workspace.
            target_path (str): The relative path of the file or folder to rename.
            new_name (str): The new name for the file or folder.

        Returns:
            str: A JSON string containing the changes made to the filesystem.

        Raises:
            FileNotFoundError: If the specified path is not found.
            PermissionError: If there's no permission to rename.
            ValueError: If there's an issue with the input values.
            Exception: For any other unexpected errors.
        """
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        file_explorer = workspace.get_file_explorer()
        change_event = file_explorer.rename_file_or_folder(target_path, new_name)
        return serialize_change_event(change_event)
