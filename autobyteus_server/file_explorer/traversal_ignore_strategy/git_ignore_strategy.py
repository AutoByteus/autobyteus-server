# autobyteus_server/file_explorer/traversal_ignore_strategy/git_ignore_strategy.py

import pathlib
import pathspec
import os

from autobyteus_server.file_explorer.traversal_ignore_strategy.traversal_ignore_strategy import TraversalIgnoreStrategy


class GitIgnoreStrategy(TraversalIgnoreStrategy):
    """
    A strategy to ignore files and folders specified in a .gitignore file using pathspec.
    """

    def __init__(self, root_path: str):
        """
        Initialize GitIgnoreStrategy.

        Args:
            root_path (str): The root path of the directory containing the .gitignore file.
        """
        self.root_path = pathlib.Path(root_path).resolve()
        gitignore_path = self.root_path / '.gitignore'
        if gitignore_path.is_file():
            with gitignore_path.open('r') as gitignore_file:
                # Read all non-empty, non-comment lines
                gitignore_lines = [line.strip() for line in gitignore_file if line.strip() and not line.startswith('#')]
                self.spec = pathspec.PathSpec.from_lines('gitwildmatch', gitignore_lines)
        else:
            self.spec = pathspec.PathSpec([])  # Empty spec if no .gitignore

    def should_ignore(self, path: str) -> bool:
        """
        Determines if a file or folder should be ignored based on patterns specified in the .gitignore file.

        Args:
            path (str): The absolute path of the file or folder.

        Returns:
            bool: True if the file or folder matches a pattern in the .gitignore file and should be ignored, 
                  False otherwise.
        """
        try:
            relative_path = pathlib.Path(path).resolve().relative_to(self.root_path)
        except ValueError:
            # The path is not under the root_path; do not ignore
            return False

        relative_path_str = str(relative_path).replace(os.sep, '/')
        
        # Append '/' if the path is a directory to correctly match directory patterns
        if os.path.isdir(path):
            relative_path_str += '/'
        
        return self.spec.match_file(relative_path_str)
