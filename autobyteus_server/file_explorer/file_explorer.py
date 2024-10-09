# File: autobyteus_server/file_explorer/file_explorer.py

import os
from autobyteus_server.file_explorer.tree_node import TreeNode
from autobyteus_server.file_explorer.directory_traversal import DirectoryTraversal
from autobyteus_server.file_explorer.traversal_ignore_strategy.dot_ignore_strategy import DotIgnoreStrategy
from autobyteus_server.file_explorer.traversal_ignore_strategy.git_ignore_strategy import GitIgnoreStrategy
from autobyteus_server.file_explorer.traversal_ignore_strategy.specific_folder_ignore_strategy import SpecificFolderIgnoreStrategy

class FileExplorer:
    """
    Class to manage workspace directory tree.
    """
    def __init__(self, workspace_root_path: str = None):
        """
        Initialize FileExplorer.
        """
        self.root_node = None
        self.workspace_root_path = workspace_root_path

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

    def add_file_or_folder(self, file_or_folder_path: str):
        """
        Adds a file or folder to the workspace directory tree.
        Args:
            file_or_folder_path (str): The path of the file or folder to be added.
        """
        # Code to add the file or folder to the tree

    def remove_file_or_folder(self, file_or_folder_path: str):
        """
        Removes a file or folder from the workspace directory tree.
        Args:
            file_or_folder_path (str): The path of the file or folder to be removed.
        """
        # Code to remove the file or folder from the tree

    def read_file_content(self, file_path: str, max_size: int = 1024 * 1024) -> str:
        """
        Reads and returns the content of a file within the workspace.

        Args:
            file_path (str): The absolute path of the file to read.
            max_size (int): Maximum file size to read, in bytes. Defaults to 1MB.

        Returns:
            str: The content of the file.

        Raises:
            ValueError: If the file is not within the workspace or exceeds the size limit.
            FileNotFoundError: If the file does not exist.
            PermissionError: If there's no permission to read the file.
        """
        # Security check: ensure the file is within the workspace
        if not os.path.commonpath([self.workspace_root_path, file_path]) == self.workspace_root_path:
            raise ValueError("Access denied: File is outside the workspace.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Permission denied: Cannot read {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            raise ValueError(f"File size ({file_size} bytes) exceeds the maximum allowed size ({max_size} bytes).")

        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def write_file_content(self, file_path: str, content: str):
        """
        Writes content to a file within the workspace.

        Args:
            file_path (str): The absolute path of the file to write.
            content (str): The content to write to the file.

        Raises:
            ValueError: If the file is not within the workspace.
            PermissionError: If there's no permission to write to the file.
        """
        # Security check: ensure the file is within the workspace
        if not os.path.commonpath([self.workspace_root_path, file_path]) == self.workspace_root_path:
            raise ValueError("Access denied: File is outside the workspace.")

        if os.path.exists(file_path) and not os.access(file_path, os.W_OK):
            raise PermissionError(f"Permission denied: Cannot write to {file_path}")

        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    def get_tree(self) -> TreeNode:
        """
        Gets the workspace directory tree.
        Returns:
            TreeNode: The root node of the workspace directory tree.
        """
        return self.root_node

    def to_json(self):
        """
        Returns a JSON representation of the workspace directory tree.
        Returns:
            JSON: The JSON representation of the workspace directory tree.
        """
        return self.root_node.to_json()