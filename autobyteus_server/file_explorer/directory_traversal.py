# directory_traversal.py

import os
from typing import List, Optional
from collections import deque

from autobyteus_server.file_explorer.traversal_ignore_strategy.traversal_ignore_strategy import TraversalIgnoreStrategy
from autobyteus_server.file_explorer.traversal_ignore_strategy.git_ignore_strategy import GitIgnoreStrategy
from autobyteus_server.file_explorer.tree_node import TreeNode
from autobyteus_server.file_explorer.sort_strategy.default_sort_strategy import DefaultSortStrategy
from autobyteus_server.file_explorer.sort_strategy.sort_strategy import SortStrategy


class DirectoryTraversal:
    """
    A class used to traverse directories and represent the directory structure as a TreeNode.
    The traversal order follows a specified SortStrategy.

    Methods
    -------
    build_tree(folder_path: str) -> TreeNode:
        Traverses a specified directory and returns its structure as a TreeNode.
    """

    def __init__(self, strategies: Optional[List[TraversalIgnoreStrategy]] = None, 
                 sort_strategy: Optional[SortStrategy] = None):
        """
        Initialize DirectoryTraversal.

        Args:
            strategies (Optional[List[TraversalIgnoreStrategy]]): A list of strategies to ignore files or folders.
                If none is provided, no file or folder will be ignored.
            sort_strategy (Optional[SortStrategy]): A strategy for sorting directories and files.
                If none is provided, DefaultSortStrategy is used.
        """
        self.initial_strategies = strategies or []
        self.sort_strategy = sort_strategy or DefaultSortStrategy()

    def build_tree(self, folder_path: str) -> TreeNode:
        """
        Traverses a specified directory and returns its structure as a TreeNode.

        This method uses an iterative approach and applies ignore strategies dynamically based on the presence
        of .gitignore files in each directory.

        Parameters:
        ----------
        folder_path : str
            The path of the directory to be traversed.

        Returns:
        -------
        TreeNode
            The root node of the directory structure.
        """
        folder_path = os.path.abspath(folder_path)
        root_name = os.path.basename(folder_path) or folder_path  # Handle root directories like '/'
        root_node = TreeNode(root_name, folder_path, os.path.isfile(folder_path))

        if root_node.is_file:
            return root_node

        queue = deque()
        # Each item in the queue is a tuple: (current_node, current_path, current_strategies)
        queue.append((root_node, folder_path, list(self.initial_strategies)))

        while queue:
            current_node, current_path, current_strategies = queue.popleft()

            try:
                children = os.listdir(current_path)
            except (PermissionError, FileNotFoundError) as e:
                # Log the error or handle accordingly
                continue  # Skip directories that cannot be accessed

            # Generate absolute paths
            children_abs_paths = [os.path.join(current_path, child) for child in children]
            sorted_children = self.sort_strategy.sort(children_abs_paths)

            # Check for .gitignore once per directory
            gitignore_path = os.path.join(current_path, '.gitignore')
            if os.path.isfile(gitignore_path):
                git_strategy = GitIgnoreStrategy(root_path=current_path)
                # Prepend to strategies for higher priority
                updated_strategies = [git_strategy] + current_strategies
            else:
                updated_strategies = current_strategies

            for child_path in sorted_children:
                if any(strategy.should_ignore(child_path) for strategy in updated_strategies):
                    continue

                name = os.path.basename(child_path)
                is_file = os.path.isfile(child_path)
                child_node = TreeNode(name, child_path, is_file)

                current_node.add_child(child_node)

                if not is_file:
                    # Add directory to queue with updated strategies
                    queue.append((child_node, child_path, list(updated_strategies)))

        return root_node
