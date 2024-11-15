# autobyteus_server/file_explorer/traversal_ignore_strategy/specific_folder_ignore_strategy.py

import os
from typing import List

from autobyteus_server.file_explorer.traversal_ignore_strategy.traversal_ignore_strategy import TraversalIgnoreStrategy


class SpecificFolderIgnoreStrategy(TraversalIgnoreStrategy):
    """
    A strategy to ignore specific folders based on their names.
    """

    def __init__(self, folders_to_ignore: List[str]):
        """
        Initialize SpecificFolderIgnoreStrategy.

        Args:
            folders_to_ignore (List[str]): A list of folder names to ignore.
        """
        self.folders_to_ignore = set(folders_to_ignore)

    def should_ignore(self, path: str) -> bool:
        """
        Determines if a folder should be ignored based on its name.

        Args:
            path (str): The path of the folder.

        Returns:
            bool: True if the folder should be ignored, False otherwise.
        """
        return os.path.isdir(path) and os.path.basename(path) in self.folders_to_ignore
