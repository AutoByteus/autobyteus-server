# default_sort_strategy.py

import os
from typing import List

from autobyteus_server.file_explorer.sort_strategy.sort_strategy import SortStrategy


class DefaultSortStrategy(SortStrategy):
    """
    Default sorting strategy for directory traversal.

    The strategy is to sort folders and files such that all directories come first, 
    and all files come later. Both directories and files are sorted in alphabetical 
    order by their basename.
    """

    def sort(self, paths: List[str]) -> List[str]:
        """
        Sorts the provided paths based on the default strategy.

        Args:
            paths (List[str]): List of absolute paths to sort.

        Returns:
            List[str]: Sorted list of paths.
        """
        return sorted(paths, key=lambda path: (not os.path.isdir(path), os.path.basename(path).lower()))
