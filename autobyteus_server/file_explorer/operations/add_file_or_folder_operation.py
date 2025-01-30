import os
from typing import List
from autobyteus_server.file_explorer.operations.base_operation import BaseFileOperation
from autobyteus_server.file_explorer.file_system_changes import (
    FileSystemChangeEvent,
    AddChange
)
from autobyteus_server.file_explorer.tree_node import TreeNode

class AddFileOrFolderOperation(BaseFileOperation):
    """
    Operation to add a new file or folder within the workspace.
    """

    def __init__(self, file_explorer, path: str, is_file: bool):
        super().__init__(file_explorer)
        self.path = path
        self.is_file = is_file

    def execute(self) -> FileSystemChangeEvent:
        normalized_path = os.path.normpath(self.path)
        if os.path.isabs(normalized_path):
            raise ValueError("The path must be relative to the workspace root.")

        absolute_path = os.path.join(self.file_explorer.workspace_root_path, normalized_path)
        if not absolute_path.startswith(self.file_explorer.workspace_root_path):
            raise ValueError("Access denied: Target is outside the workspace.")

        if os.path.exists(absolute_path):
            raise ValueError(f"File or folder already exists at path: {self.path}")

        changes: List[AddChange] = []

        # Ensure parent directories exist
        parent_directory = os.path.dirname(absolute_path)
        if not os.path.exists(parent_directory):
            os.makedirs(parent_directory)
            # Update the tree for each newly created parent directory
            relative_dir_path = os.path.relpath(parent_directory, self.file_explorer.workspace_root_path)
            self._create_missing_directories_in_tree(relative_dir_path, changes)

        # Create the file or folder
        if self.is_file:
            open(absolute_path, 'w', encoding='utf-8').close()
        else:
            os.makedirs(absolute_path, exist_ok=True)

        # Finally update the tree with the newly created node
        parts = normalized_path.split(os.sep)
        current_node = self.file_explorer.root_node
        # Traverse or create intermediate directories if they somehow weren't created yet
        for part in parts[:-1]:
            for child in current_node.children:
                if child.name == part and not child.is_file:
                    current_node = child
                    break

        new_node_name = parts[-1]
        new_node = TreeNode(name=new_node_name, is_file=self.is_file, parent=current_node)
        current_node.add_child(new_node)

        add_change = AddChange(
            node=new_node,
            parent_id=current_node.id
        )
        changes.append(add_change)

        return FileSystemChangeEvent(changes=changes)

    def _create_missing_directories_in_tree(self, relative_dir_path: str, changes: List[AddChange]) -> None:
        """
        Create any missing directory nodes in the in-memory tree, 
        mirroring the actual directories created on the filesystem.
        """
        normalized_dir_path = os.path.normpath(relative_dir_path)
        parts = normalized_dir_path.split(os.sep)

        current_node = self.file_explorer.root_node
        for part in parts:
            if part == ".":
                continue
            found = False
            for child in current_node.children:
                if child.name == part and not child.is_file:
                    current_node = child
                    found = True
                    break

            if not found:
                new_dir_node = TreeNode(name=part, is_file=False, parent=current_node)
                current_node.add_child(new_dir_node)
                add_change = AddChange(node=new_dir_node, parent_id=current_node.id)
                changes.append(add_change)
                current_node = new_dir_node
