import logging
import os
from typing import Callable, TYPE_CHECKING, List

from watchdog.events import FileSystemEventHandler, FileSystemEvent

if TYPE_CHECKING:
    from autobyteus_server.file_explorer.file_explorer import FileExplorer

from autobyteus_server.file_explorer.operations.move_file_operation import MoveFileOperation
from autobyteus_server.file_explorer.operations.remove_file_operation import RemoveFileOperation
from autobyteus_server.file_explorer.operations.write_file_operation import WriteFileOperation
from autobyteus_server.file_explorer.file_system_changes import FileSystemChangeEvent
from autobyteus_server.file_explorer.traversal_ignore_strategy.traversal_ignore_strategy import TraversalIgnoreStrategy
from autobyteus_server.file_explorer.traversal_ignore_strategy.git_ignore_strategy import GitIgnoreStrategy

logger = logging.getLogger(__name__)

class WatchdogHandler(FileSystemEventHandler):
    """
    Handler for filesystem events to convert them into FileSystemChangeEvents,
    leveraging existing file operations and applying ignore strategies.
    """

    def __init__(self, file_explorer: 'FileExplorer', callback: Callable[[FileSystemChangeEvent], None], 
                 ignore_strategies: List[TraversalIgnoreStrategy]):
        """
        Initialize the handler with a FileExplorer instance, callback, and ignore strategies.

        Args:
            file_explorer (FileExplorer): The FileExplorer instance managing the workspace.
            callback (Callable): Function to call with FileSystemChangeEvent.
            ignore_strategies (List[TraversalIgnoreStrategy]): Strategies to filter events.
        """
        super().__init__()
        self.file_explorer = file_explorer
        self.callback = callback
        self.ignore_strategies = ignore_strategies

    def _should_ignore(self, path: str) -> bool:
        """
        Determine if a path should be ignored based on strategies and dynamic .gitignore files.

        Args:
            path (str): The absolute path to check.

        Returns:
            bool: True if the path should be ignored, False otherwise.
        """
        # Check base strategies
        if any(strategy.should_ignore(path) for strategy in self.ignore_strategies):
            logger.debug(f"Ignoring path {path} due to base ignore strategy")
            return True

        # Check for local .gitignore in the parent directory
        parent_dir = os.path.dirname(path)
        gitignore_path = os.path.join(parent_dir, '.gitignore')
        if os.path.isfile(gitignore_path):
            local_git_strategy = GitIgnoreStrategy(root_path=parent_dir)
            if local_git_strategy.should_ignore(path):
                logger.debug(f"Ignoring path {path} due to local .gitignore in {parent_dir}")
                return True

        return False

    def on_created(self, event: FileSystemEvent) -> None:
        """
        Handle file/folder creation events by writing an empty file, if not ignored.
        """
        if self._should_ignore(event.src_path):
            logger.info(f"Skipping creation event for ignored path: {event.src_path}")
            return

        logger.info(f"File created: {event.src_path}")
        relative_path = os.path.relpath(event.src_path, self.file_explorer.workspace_root_path)
        try:
            change_event = self.file_explorer.write_file_content(relative_path, "")
            self.callback(change_event)
        except Exception as e:
            logger.error(f"Error handling creation event for {relative_path}: {e}")

    def on_deleted(self, event: FileSystemEvent) -> None:
        """
        Handle file/folder deletion events using RemoveFileOperation, if not ignored.
        """
        if self._should_ignore(event.src_path):
            logger.info(f"Skipping deletion event for ignored path: {event.src_path}")
            return

        logger.info(f"File deleted: {event.src_path}")
        relative_path = os.path.relpath(event.src_path, self.file_explorer.workspace_root_path)
        try:
            operation = RemoveFileOperation(self.file_explorer, relative_path)
            change_event = operation.execute()
            self.callback(change_event)
        except Exception as e:
            logger.error(f"Error handling deletion event for {relative_path}: {e}")

    def on_moved(self, event: FileSystemEvent) -> None:
        """
        Handle file/folder move or rename events using MoveFileOperation, if not ignored.
        """
        if self._should_ignore(event.src_path) or self._should_ignore(event.dest_path):
            logger.info(f"Skipping move event for ignored path: {event.src_path} -> {event.dest_path}")
            return

        logger.info(f"File moved from {event.src_path} to {event.dest_path}")
        src_relative = os.path.relpath(event.src_path, self.file_explorer.workspace_root_path)
        dest_relative = os.path.relpath(event.dest_path, self.file_explorer.workspace_root_path)
        try:
            operation = MoveFileOperation(self.file_explorer, src_relative, dest_relative)
            change_event = operation.execute()
            self.callback(change_event)
        except Exception as e:
            logger.error(f"Error handling move/rename event from {src_relative} to {dest_relative}: {e}")

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Handle file modification events using WriteFileOperation, if not ignored.
        """
        if event.is_directory:
            return  # Ignore directory modifications

        if self._should_ignore(event.src_path):
            logger.info(f"Skipping modification event for ignored path: {event.src_path}")
            return

        logger.info(f"File modified: {event.src_path}")
        relative_path = os.path.relpath(event.src_path, self.file_explorer.workspace_root_path)
        try:
            content = self.file_explorer.read_file_content(relative_path)
            operation = WriteFileOperation(self.file_explorer, relative_path, content)
            change_event = operation.execute()
            self.callback(change_event)
        except Exception as e:
            logger.error(f"Error handling modification event for {relative_path}: {e}")
