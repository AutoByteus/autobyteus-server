import os
import shutil
from autobyteus_server.file_explorer.operations.base_operation import BaseFileOperation
from autobyteus_server.file_explorer.file_system_changes import (
    FileSystemChangeEvent,
    MoveChange
)
from autobyteus_server.file_explorer.tree_node import TreeNode

class MoveFileOperation(BaseFileOperation):
    """
    Operation to move or rename a file or folder within the workspace.
    """

    def __init__(self, file_explorer, source_path: str, destination_path: str):
        super().__init__(file_explorer)
        self.source_path = source_path
        self.destination_path = destination_path

    def execute(self) -> FileSystemChangeEvent:
        normalized_source = os.path.normpath(self.source_path)
        if os.path.isabs(normalized_source):
            raise ValueError("The path must be relative to the workspace root.")

        absolute_source = os.path.join(self.file_explorer.workspace_root_path, normalized_source)
        if not absolute_source.startswith(self.file_explorer.workspace_root_path):
            raise ValueError("Access denied: Source is outside the workspace.")

        if not os.path.exists(absolute_source):
            raise ValueError(f"Source path not found: {self.source_path}")

        normalized_destination = os.path.normpath(self.destination_path)
        if os.path.isabs(normalized_destination):
            raise ValueError("The path must be relative to the workspace root.")

        absolute_destination = os.path.join(self.file_explorer.workspace_root_path, normalized_destination)
        if not absolute_destination.startswith(self.file_explorer.workspace_root_path):
            raise ValueError("Access denied: Destination is outside the workspace.")

        if os.path.exists(absolute_destination) and os.path.isdir(absolute_destination):
            final_destination = os.path.join(absolute_destination, os.path.basename(absolute_source))
        else:
            final_destination = absolute_destination

        if os.path.exists(final_destination):
            raise ValueError(f"Destination path already exists: {self.destination_path}")

        try:
            shutil.move(absolute_source, final_destination)
        except PermissionError as pe:
            raise PermissionError(f"Permission denied: Cannot move {absolute_source}") from pe
        except OSError as oe:
            raise OSError(f"Error moving {absolute_source} to {final_destination}: {oe}") from oe

        # Remove source node
        source_parts = normalized_source.split(os.sep)
        source_current_node = self.file_explorer.root_node
        source_parent_node = None

        for part in source_parts:
            source_parent_node = source_current_node
            for child in source_current_node.children:
                if child.name == part:
                    source_current_node = child
                    break
            else:
                raise ValueError(f"Source path not found in tree: {self.source_path}")

        if source_parent_node and source_current_node in source_parent_node.children:
            source_parent_node.children.remove(source_current_node)
        else:
            raise ValueError(f"Cannot remove the node from tree: {self.source_path}")

        # Update new parent reference
        new_parent_directory = os.path.dirname(final_destination)
        relative_new_parent = os.path.relpath(new_parent_directory, self.file_explorer.workspace_root_path)
        normalized_new_parent = os.path.normpath(relative_new_parent).split(os.sep)

        new_parent_node = self.file_explorer.root_node
        if normalized_new_parent and normalized_new_parent[0] != '.':
            for part in normalized_new_parent:
                found = False
                for child in new_parent_node.children:
                    if child.name == part and not child.is_file:
                        new_parent_node = child
                        found = True
                        break
                if not found:
                    raise ValueError(f"Destination directory does not exist in tree: {self.destination_path}")

        source_current_node.parent = new_parent_node
        new_name = os.path.basename(final_destination)
        source_current_node.name = new_name
        new_parent_node.children.append(source_current_node)

        move_change = MoveChange(
            node=source_current_node,
            old_parent_id=source_parent_node.id if source_parent_node else "",
            new_parent_id=new_parent_node.id
        )
        return FileSystemChangeEvent(changes=[move_change])