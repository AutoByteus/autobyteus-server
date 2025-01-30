import os
from typing import Optional, List
from dataclasses import dataclass
import json

from autobyteus_server.file_explorer.operations.add_file_or_folder_operation import AddFileOrFolderOperation
from autobyteus_server.file_explorer.tree_node import TreeNode
from autobyteus_server.file_explorer.directory_traversal import DirectoryTraversal
from autobyteus_server.file_explorer.traversal_ignore_strategy.git_ignore_strategy import GitIgnoreStrategy
from autobyteus_server.file_explorer.traversal_ignore_strategy.specific_folder_ignore_strategy import SpecificFolderIgnoreStrategy
from autobyteus_server.file_explorer.file_system_changes import FileSystemChangeEvent

# The new operations:
from autobyteus_server.file_explorer.operations.write_file_operation import WriteFileOperation
from autobyteus_server.file_explorer.operations.remove_file_operation import RemoveFileOperation
from autobyteus_server.file_explorer.operations.move_file_operation import MoveFileOperation
from autobyteus_server.file_explorer.operations.rename_file_operation import RenameFileOperation

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
            GitIgnoreStrategy(root_path=self.workspace_root_path)
        ]
        directory_traversal = DirectoryTraversal(strategies=files_ignore_strategies)

        self.root_node = directory_traversal.build_tree(self.workspace_root_path)
        return self.root_node

    def write_file_content(self, file_path: str, content: str) -> FileSystemChangeEvent:
        """
        Write file content operation, delegates to WriteFileOperation.
        """
        operation = WriteFileOperation(self, file_path, content)
        return operation.execute()

    def remove_file_or_folder(self, file_or_folder_path: str) -> FileSystemChangeEvent:
        """
        Remove file or folder operation, delegates to RemoveFileOperation.
        """
        operation = RemoveFileOperation(self, file_or_folder_path)
        return operation.execute()

    def move_file_or_folder(self, source_path: str, destination_path: str) -> FileSystemChangeEvent:
        """
        Move file or folder operation, delegates to MoveFileOperation.
        """
        operation = MoveFileOperation(self, source_path, destination_path)
        return operation.execute()

    def rename_file_or_folder(self, target_path: str, new_name: str) -> FileSystemChangeEvent:
        """
        Rename file or folder operation, delegates to RenameFileOperation.
        """
        operation = RenameFileOperation(self, target_path, new_name)
        return operation.execute()

    def add_file_or_folder(self, path: str, is_file: bool) -> FileSystemChangeEvent:
        """
        Creates a new file or folder at the given path (relative to the workspace).

        Args:
            path (str): The relative path where to create the file or folder
            is_file (bool): True if creating a file, False if creating a folder

        Returns:
            FileSystemChangeEvent: Event describing the addition

        Raises:
            ValueError: If the path is outside the workspace
            RuntimeError: If creation fails
        """
        operation = AddFileOrFolderOperation(self, path, is_file)
        return operation.execute()

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
        """
        return self.root_node.to_json() if self.root_node else ""

    def get_all_file_paths(self) -> List[str]:
        """
        Returns a list of all file paths in the workspace.
        """
        if not self.root_node:
            raise ValueError("Directory tree is not built")

        all_paths = []

        def traverse(node: TreeNode):
            if node.is_file:
                all_paths.append(node.get_path())
            else:
                for child in node.children:
                    traverse(child)

        traverse(self.root_node)
        return all_paths