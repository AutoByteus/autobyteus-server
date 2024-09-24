# dot_ignore_strategy.py

import os
from autobyteus_server.file_explorer.traversal_ignore_strategy.traversal_ignore_strategy import TraversalIgnoreStrategy

class DotIgnoreStrategy(TraversalIgnoreStrategy):
    """
    Ignore all hidden files and directories (those starting with a dot).
    """
    def should_ignore(self, path: str) -> bool:
        return os.path.basename(path).startswith('.')
