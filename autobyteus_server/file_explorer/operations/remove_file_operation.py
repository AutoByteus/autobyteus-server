import os
import shutil
from autobyteus_server.file_explorer.operations.base_operation import BaseFileOperation
from autobyteus_server.file_explorer.file_system_changes import (
    FileSystemChangeEvent,
    DeleteChange
)
from autobyteus_server.file_explorer.tree_node import TreeNode

class RemoveFileOperation(BaseFileOperation):
    """
    Operation to remove a file or folder from the workspace.
    """

    def __init__(self, file_explorer, file_or_folder_path: str):
        super().__init__(file_explorer)
        self.file_or_folder_path = file_or_folder_path

    def execute(self) -> FileSystemChangeEvent:
        normalized_path = os.path.normpath(self.file_or_folder_path)
        if os.path.isabs(normalized_path):
            raise ValueError("The path must be relative to the workspace root.")

        absolute_path = os.path.join(self.file_explorer.workspace_root_path, normalized_path)

        if not absolute_path.startswith(self.file_explorer.workspace_root_path):
            raise ValueError("Access denied: Path is outside the workspace.")

        if not os.path.exists(absolute_path):
            raise ValueError(f"Path not found: {self.file_or_folder_path}")

        try:
            if os.path.isfile(absolute_path):
                os.remove(absolute_path)
            elif os.path.isdir(absolute_path):
                shutil.rmtree(absolute_path)
            else:
                raise ValueError(f"Unsupported file type: {self.file_or_folder_path}")
        except PermissionError as pe:
            raise PermissionError(f"Permission denied: Cannot delete {absolute_path}") from pe
        except OSError as oe:
            raise OSError(f"Error deleting {absolute_path}: {oe}") from oe

        parts = normalized_path.split(os.sep)
        current_node = self.file_explorer.root_node
        parent_node = None

        for part in parts:
            parent_node = current_node
            for child in current_node.children:
                if child.name == part:
                    current_node = child
                    break
            else:
                raise ValueError(f"Path not found in tree: {self.file_or_folder_path}")

        if parent_node and current_node in parent_node.children:
            parent_node.children.remove(current_node)
        else:
            raise ValueError(f"Cannot remove the node from tree: {self.file_or_folder_path}")

        delete_change = DeleteChange(
            node_id=current_node.id,
            parent_id=parent_node.id
        )

        return FileSystemChangeEvent(changes=[delete_change])