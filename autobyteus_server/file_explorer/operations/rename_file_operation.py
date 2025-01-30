import os
from autobyteus_server.file_explorer.operations.base_operation import BaseFileOperation
from autobyteus_server.file_explorer.file_system_changes import (
    FileSystemChangeEvent,
    RenameChange
)
from autobyteus_server.file_explorer.tree_node import TreeNode

class RenameFileOperation(BaseFileOperation):
    """
    Operation to rename a file or folder within the same parent directory in the workspace.
    """

    def __init__(self, file_explorer, target_path: str, new_name: str):
        super().__init__(file_explorer)
        self.target_path = target_path
        self.new_name = new_name

    def execute(self) -> FileSystemChangeEvent:
        normalized_target = os.path.normpath(self.target_path)
        if os.path.isabs(normalized_target):
            raise ValueError("The path must be relative to the workspace root.")

        absolute_target = os.path.join(self.file_explorer.workspace_root_path, normalized_target)
        if not absolute_target.startswith(self.file_explorer.workspace_root_path):
            raise ValueError("Access denied: Target is outside the workspace.")

        if not os.path.exists(absolute_target):
            raise ValueError(f"Target path not found: {self.target_path}")

        parent_directory = os.path.dirname(absolute_target)
        absolute_destination = os.path.join(parent_directory, self.new_name)
        if os.path.exists(absolute_destination):
            raise ValueError(f"A file or folder named '{self.new_name}' already exists in this location.")

        try:
            os.rename(absolute_target, absolute_destination)
        except PermissionError as pe:
            raise PermissionError(f"Permission denied: Cannot rename {absolute_target}") from pe
        except OSError as oe:
            raise OSError(f"Error renaming {absolute_target} to {absolute_destination}: {oe}") from oe

        # Update in-memory tree
        parts = normalized_target.split(os.sep)
        current_node = self.file_explorer.root_node
        parent_node = None

        for part in parts:
            parent_node = current_node
            for child in current_node.children:
                if child.name == part:
                    current_node = child
                    break
            else:
                raise ValueError(f"Target path not found in tree: {self.target_path}")

        old_name = current_node.name
        current_node.name = self.new_name

        rename_change = RenameChange(
            node=current_node,
            parent_id=parent_node.id if parent_node else ""
        )

        return FileSystemChangeEvent(changes=[rename_change])
