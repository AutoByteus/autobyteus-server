# autobyteus_server/file_explorer/tree_node.py

import json
from typing import List, Dict, Any
from collections import deque


class TreeNode:
    """
    A class used to represent a file or directory in a directory structure.

    Attributes
    ----------
    name : str
        The name of the file or directory.
    path : str
        The full path of the file or directory.
    is_file : bool
        True if this node represents a file, False if it represents a directory.
    children : List['TreeNode']
        The children of this node. Each child is a TreeNode representing a file or subdirectory.

    Methods
    -------
    add_child(node: 'TreeNode')
        Adds a child to this node.
    to_dict() -> Dict[str, Any]
        Returns a dictionary representation of the TreeNode.
    to_json() -> str
        Returns a JSON representation of the TreeNode.
    """

    def __init__(self, name: str, path: str, is_file: bool = False):
        self.name = name
        self.path = path
        self.is_file = is_file
        self.children: List['TreeNode'] = []

    def add_child(self, node: 'TreeNode'):
        """Adds a child to this node."""
        self.children.append(node)

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the TreeNode using an iterative approach.

        Returns:
            dict: The dictionary representation of the TreeNode.
        """
        root_dict = {
            "name": self.name,
            "path": self.path,
            "is_file": self.is_file,
            "children": []
        }

        stack = deque([(self, root_dict)])

        while stack:
            current_node, current_dict = stack.pop()
            for child in current_node.children:
                child_dict = {
                    "name": child.name,
                    "path": child.path,
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
        # For better performance with large trees, consider using faster JSON libraries
        return json.dumps(self.to_dict(), separators=(',', ':'))
