import os
from typing import List
from autobyteus_server.file_explorer.operations.base_operation import BaseFileOperation
from autobyteus_server.file_explorer.file_system_changes import (
    FileSystemChangeEvent,
    AddChange
)
from autobyteus_server.file_explorer.tree_node import TreeNode

class WriteFileOperation(BaseFileOperation):
    """
    Operation to write content to a file within the workspace.
    Creates parent directories if needed.
    """

    def __init__(self, file_explorer, file_path: str, content: str):
        super().__init__(file_explorer)
        self.file_path = file_path
        self.content = content

    def execute(self) -> FileSystemChangeEvent:
        normalized_path = os.path.normpath(self.file_path)
        if os.path.isabs(normalized_path):
            raise ValueError("The path must be relative to the workspace root.")

        absolute_file_path = os.path.normpath(
            os.path.join(self.file_explorer.workspace_root_path, normalized_path)
        )
        if not absolute_file_path.startswith(self.file_explorer.workspace_root_path):
            raise ValueError("Access denied: File is outside the workspace.")

        if os.path.exists(absolute_file_path) and not os.access(absolute_file_path, os.W_OK):
            raise PermissionError(f"Permission denied: Cannot write to {absolute_file_path}")

        directory = os.path.dirname(absolute_file_path)
        changes: List = []

        if not os.path.exists(directory):
            os.makedirs(directory)
            relative_dir_path = os.path.relpath(directory, self.file_explorer.workspace_root_path)
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
                    new_node = TreeNode(name=part, is_file=False, parent=current_node)
                    current_node.add_child(new_node)
                    current_node = new_node
                    add_change = AddChange(
                        node=new_node,
                        parent_id=current_node.parent.id
                    )
                    changes.append(add_change)

        with open(absolute_file_path, 'w', encoding='utf-8') as file:
            file.write(self.content)

        parts = normalized_path.split(os.sep)
        current_node = self.file_explorer.root_node

        for part in parts[:-1]:
            for child in current_node.children:
                if child.name == part and not child.is_file:
                    current_node = child
                    break

        new_part = parts[-1]
        existing_node = None
        for child in current_node.children:
            if child.name == new_part:
                existing_node = child
                break

        if not existing_node:
            new_node = TreeNode(name=new_part, is_file=True, parent=current_node)
            current_node.add_child(new_node)
            add_change = AddChange(
                node=new_node,
                parent_id=current_node.id
            )
            changes.append(add_change)

        return FileSystemChangeEvent(changes=changes)