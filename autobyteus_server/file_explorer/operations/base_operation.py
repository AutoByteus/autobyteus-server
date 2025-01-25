import abc
from autobyteus_server.file_explorer.file_system_changes import FileSystemChangeEvent
from autobyteus_server.file_explorer.file_explorer import FileExplorer

class BaseFileOperation(abc.ABC):
    """
    Abstract base class for file operations in the workspace.

    Concrete subclasses must implement the `execute` method
    and return a FileSystemChangeEvent.
    """

    def __init__(self, file_explorer: FileExplorer):
        if not file_explorer or not file_explorer.workspace_root_path:
            raise ValueError("FileExplorer with a valid workspace_root_path is required.")
        self.file_explorer = file_explorer

    @abc.abstractmethod
    def execute(self) -> FileSystemChangeEvent:
        """
        Execute the file operation and return a FileSystemChangeEvent.
        """
        pass