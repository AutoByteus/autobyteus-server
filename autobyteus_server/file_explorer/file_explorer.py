import os
import shutil
from typing import Optional, List
from dataclasses import dataclass, field
import json

from autobyteus_server.file_explorer.tree_node import TreeNode
from autobyteus_server.file_explorer.directory_traversal import DirectoryTraversal
from autobyteus_server.file_explorer.traversal_ignore_strategy.dot_ignore_strategy import DotIgnoreStrategy
from autobyteus_server.file_explorer.traversal_ignore_strategy.git_ignore_strategy import GitIgnoreStrategy
from autobyteus_server.file_explorer.traversal_ignore_strategy.specific_folder_ignore_strategy import SpecificFolderIgnoreStrategy
from autobyteus_server.file_explorer.file_system_changes import AddChange, DeleteChange, FileSystemChange, FileSystemChangeEvent


@dataclass
class FileExplorer:
    """
    Class to manage workspace directory tree.
    """
    workspace_root_path: Optional[str] = None
    root_node: Optional[TreeNode] = None

    def __post_init__(self):
        if self.workspace_root_path:
            self.workspace_root_path = os.path.normpath(self.workspace_root_path)

    def build_workspace_directory_tree(self) -> TreeNode:
        """
        Builds and returns the directory tree of a workspace.

        Returns:
            TreeNode: The root TreeNode of the directory tree.
        """
        if not self.workspace_root_path:
            raise ValueError("Workspace root path is not set")

        files_ignore_strategies = [
            SpecificFolderIgnoreStrategy(folders_to_ignore=['.git']),
            GitIgnoreStrategy(root_path=self.workspace_root_path),
            DotIgnoreStrategy()
        ]
        directory_traversal = DirectoryTraversal(strategies=files_ignore_strategies)

        self.root_node = directory_traversal.build_tree(self.workspace_root_path)
        return self.root_node

    def remove_file_or_folder(self, file_or_folder_path: str) -> FileSystemChangeEvent:
        """
        Removes a file or folder from the workspace directory tree and the filesystem,
        then returns the corresponding file system changes.

        Args:
            file_or_folder_path (str): The relative path of the file or folder to be removed.

        Returns:
            FileSystemChangeEvent: The event representing the file system changes.

        Raises:
            ValueError: If the path is invalid or not found.
            PermissionError: If there's no permission to delete the file or folder.
            OSError: If an OS-related error occurs during deletion.
        """
        if not self.workspace_root_path:
            raise ValueError("Workspace root path is not set")

        normalized_path = os.path.normpath(file_or_folder_path)
        if os.path.isabs(normalized_path):
            raise ValueError("The path must be relative to the workspace root.")

        absolute_path = os.path.join(self.workspace_root_path, normalized_path)

        if not absolute_path.startswith(self.workspace_root_path):
            raise ValueError("Access denied: Path is outside the workspace.")

        if not os.path.exists(absolute_path):
            raise ValueError(f"Path not found: {file_or_folder_path}")

        # Delete the file or folder from the filesystem
        try:
            if os.path.isfile(absolute_path):
                os.remove(absolute_path)
            elif os.path.isdir(absolute_path):
                shutil.rmtree(absolute_path)
            else:
                raise ValueError(f"Unsupported file type: {file_or_folder_path}")
        except PermissionError as pe:
            raise PermissionError(f"Permission denied: Cannot delete {absolute_path}") from pe
        except OSError as oe:
            raise OSError(f"Error deleting {absolute_path}: {oe}") from oe

        # Now, remove the node from the in-memory tree
        parts = normalized_path.split(os.sep)
        current_node = self.root_node
        parent_node = None

        for part in parts:
            parent_node = current_node
            for child in current_node.children:
                if child.name == part:
                    current_node = child
                    break
            else:
                raise ValueError(f"Path not found in tree: {file_or_folder_path}")

        if parent_node and current_node in parent_node.children:
            parent_node.children.remove(current_node)
        else:
            raise ValueError(f"Cannot remove the node from tree: {file_or_folder_path}")

        # Create DeleteChange
        delete_change = DeleteChange(
            node_id=current_node.id,
            parent_id=parent_node.id
        )

        # Create and return FileSystemChangeEvent
        change_event = FileSystemChangeEvent(changes=[delete_change])
        return change_event

    def read_file_content(self, file_path: str, max_size: int = 1024 * 1024) -> str:
        """
        Reads and returns the content of a file within the workspace.

        Args:
            file_path (str): The relative path of the file to read.
            max_size (int): Maximum file size to read, in bytes. Defaults to 1MB.

        Returns:
            str: The content of the file.

        Raises:
            ValueError: If the file is not within the workspace or exceeds the size limit.
            FileNotFoundError: If the file does not exist.
            PermissionError: If there's no permission to read the file.
        """
        if not self.workspace_root_path:
            raise ValueError("Workspace root path is not set")

        # Security check: ensure the file is within the workspace
        absolute_file_path = os.path.normpath(os.path.join(self.workspace_root_path, file_path))
        if not absolute_file_path.startswith(self.workspace_root_path):
            raise ValueError("Access denied: File is outside the workspace.")

        if not os.path.exists(absolute_file_path):
            raise FileNotFoundError(f"File not found: {absolute_file_path}")

        if not os.access(absolute_file_path, os.R_OK):
            raise PermissionError(f"Permission denied: Cannot read {absolute_file_path}")

        file_size = os.path.getsize(absolute_file_path)
        if file_size > max_size:
            raise ValueError(f"File size ({file_size} bytes) exceeds the maximum allowed size ({max_size} bytes).")

        with open(absolute_file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def write_file_content(self, file_path: str, content: str) -> FileSystemChangeEvent:
        """
        Writes content to a file within the workspace and returns the corresponding file system changes.

        Args:
            file_path (str): The relative path of the file to write.
            content (str): The content to write to the file.

        Returns:
            FileSystemChangeEvent: The event representing the file system changes.

        Raises:
            ValueError: If the file is not within the workspace.
            PermissionError: If there's no permission to write to the file.
        """
        if not self.workspace_root_path:
            raise ValueError("Workspace root path is not set")

        # Security check: ensure the file is within the workspace
        normalized_path = os.path.normpath(file_path)
        if os.path.isabs(normalized_path):
            raise ValueError("The path must be relative to the workspace root.")

        absolute_file_path = os.path.normpath(os.path.join(self.workspace_root_path, normalized_path))
        if not absolute_file_path.startswith(self.workspace_root_path):
            raise ValueError("Access denied: File is outside the workspace.")

        if os.path.exists(absolute_file_path) and not os.access(absolute_file_path, os.W_OK):
            raise PermissionError(f"Permission denied: Cannot write to {absolute_file_path}")

        directory = os.path.dirname(absolute_file_path)
        changes: List[FileSystemChange] = []

        # Create directories if they do not exist and track added directories
        if not os.path.exists(directory):
            os.makedirs(directory)
            # Update the in-memory directory tree and track added directories
            relative_dir_path = os.path.relpath(directory, self.workspace_root_path)
            normalized_dir_path = os.path.normpath(relative_dir_path)
            parts = normalized_dir_path.split(os.sep)
            current_node = self.root_node

            for part in parts:
                if part == '.':
                    continue  # Skip current directory reference
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
                    # Track the added directory
                    add_change = AddChange(
                        node=new_node,
                        parent_id=current_node.parent.id
                    )
                    changes.append(add_change)

        # Write the file
        with open(absolute_file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        # Update the in-memory directory tree
        parts = normalized_path.split(os.sep)
        current_node = self.root_node

        for part in parts[:-1]:
            for child in current_node.children:
                if child.name == part and not child.is_file:
                    current_node = child
                    break

        new_part = parts[-1]
        is_file = True
        existing_node = None
        for child in current_node.children:
            if child.name == new_part:
                existing_node = child
                break

        if not existing_node:
            new_node = TreeNode(name=new_part, is_file=is_file, parent=current_node)
            current_node.add_child(new_node)
            # Track the added file
            add_change = AddChange(
                node=new_node,
                parent_id=current_node.id
            )
            changes.append(add_change)
        else:
            new_node = existing_node  # Overwriting existing file
            # No need to track an AddChange when overwriting an existing file

        # Create and return FileSystemChangeEvent
        change_event = FileSystemChangeEvent(changes=changes)
        return change_event

    def get_tree(self) -> Optional[TreeNode]:
        """
        Gets the workspace directory tree.
        Returns:
            TreeNode: The root node of the workspace directory tree.
        """
        return self.root_node

    def to_json(self) -> str:
        """
        Returns a JSON representation of the workspace directory tree.
        Returns:
            str: The JSON representation of the workspace directory tree.
        """
        return self.root_node.to_json()