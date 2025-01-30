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
        Renames a file or folder within the same directory.
        """
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        file_explorer = workspace.get_file_explorer()
        change_event = file_explorer.rename_file_or_folder(target_path, new_name)
        return serialize_change_event(change_event)

    @strawberry.mutation
    def create_file_or_folder(self, workspace_id: str, path: str, is_file: bool) -> str:
        """
        Creates a new file or folder at the specified path within the workspace.
        """
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        file_explorer = workspace.get_file_explorer()
        change_event = file_explorer.add_file_or_folder(path, is_file)
        return serialize_change_event(change_event)
