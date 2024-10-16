import json
from typing import List, Dict, Any, Optional
from collections import deque
import os

class TreeNode:
    """
    A class used to represent a file or directory in a directory structure.

    Attributes
    ----------
    name : str
        The name of the file or directory.
    is_file : bool
        True if this node represents a file, False if it represents a directory.
    children : List['TreeNode']
        The children of this node. Each child is a TreeNode representing a file or subdirectory.
    parent : Optional['TreeNode']
        The parent node of this TreeNode. None for the root node.

    Methods
    -------
    add_child(node: 'TreeNode')
        Adds a child to this node.
    to_dict() -> Dict[str, Any]
        Returns a dictionary representation of the TreeNode.
    to_json() -> str
        Returns a JSON representation of the TreeNode.
    """

    def __init__(self, name: str, is_file: bool = False, parent: Optional['TreeNode'] = None):
        self.name = name
        self.is_file = is_file
        self.children: List['TreeNode'] = []
        self.parent = parent

    def add_child(self, node: 'TreeNode'):
        """Adds a child to this node."""
        node.parent = self  # Ensure the child's parent is set correctly
        self.children.append(node)

    def get_path(self) -> str:
        """
        Constructs and returns the relative path of the current node with respect to the root.

        Returns:
            str: The relative path of the node.
        """
        parts = []
        current = self
        while current is not None:
            parts.append(current.name)
            current = current.parent
        parts = list(reversed(parts))
        if len(parts) > 1:
            # Exclude the root node's name
            relative_parts = parts[1:]
            return os.path.join(*relative_parts)
        return parts[0]

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the TreeNode using an iterative approach.

        Returns:
            dict: The dictionary representation of the TreeNode.
        """
        root_dict = {
            "name": self.name,
            "path": self.get_path(),
            "is_file": self.is_file,
            "children": []
        }

        stack = deque([(self, root_dict)])

        while stack:
            current_node, current_dict = stack.pop()
            for child in current_node.children:
                child_dict = {
                    "name": child.name,
                    "path": child.get_path(),
                    "is_file": child.is_file,
                    "children": []
                }
                current_dict["children"].append(child_dict)
                if not child.is_file:
                    stack.append((child, child_dict))

        return root_dict

    def to_json(self) -> str:
        """
        Returns a JSON representation of the TreeNode using an iterative approach.

        Returns:
            str: The JSON representation of the TreeNode.
        """
        # Updated to include indentation for better readability in tests
        return json.dumps(self.to_dict(), indent=4)