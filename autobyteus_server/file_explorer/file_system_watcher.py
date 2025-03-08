import asyncio
import logging
from typing import Optional, AsyncGenerator, TYPE_CHECKING, List

from watchdog.observers import Observer

if TYPE_CHECKING:
    from autobyteus_server.file_explorer.file_explorer import FileExplorer

from autobyteus_server.file_explorer.file_system_changes import FileSystemChangeEvent
from autobyteus_server.file_explorer.watchdog_handler import WatchdogHandler
from autobyteus_server.file_explorer.traversal_ignore_strategy.traversal_ignore_strategy import TraversalIgnoreStrategy

logger = logging.getLogger(__name__)

class FileSystemWatcher:
    """
    Watches the filesystem for changes and notifies via a simple queue-based mechanism.
    Integrates ignore strategies to filter events consistent with directory traversal.
    """

    def __init__(self, file_explorer: 'FileExplorer', loop: asyncio.AbstractEventLoop, 
                 ignore_strategies: List[TraversalIgnoreStrategy]):
        """
        Initialize the watcher with a FileExplorer instance, event loop, and ignore strategies.
        
        Args:
            file_explorer (FileExplorer): The FileExplorer instance managing the workspace.
            loop (asyncio.AbstractEventLoop): The event loop for async operations.
            ignore_strategies (List[TraversalIgnoreStrategy]): Strategies to filter events.
        """
        self.file_explorer = file_explorer
        self.loop = loop
        self.observer: Optional[Observer] = None
        self.handler = WatchdogHandler(file_explorer, self.handle_change_event, ignore_strategies)
        self._event_queue: asyncio.Queue[str] = asyncio.Queue()

    def handle_change_event(self, change_event: FileSystemChangeEvent) -> None:
        """
        Handle a filesystem change event by pushing it into the event queue.
        
        Args:
            change_event (FileSystemChangeEvent): The event to process.
        """
        logger.info(f"Change event detected: {change_event}")
        serialized_event = change_event.to_json()
        self.loop.call_soon_threadsafe(self._event_queue.put_nowait, serialized_event)

    def start(self) -> None:
        """
        Start watching the filesystem for changes.
        """
        self.observer = Observer()
        self.observer.schedule(self.handler, self.file_explorer.workspace_root_path, recursive=True)
        self.observer.start()
        logger.info(f"Started filesystem watcher for workspace {self.file_explorer.workspace_root_path}")

    def stop(self) -> None:
        """
        Stop watching the filesystem and clean up resources.
        """
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info(f"Stopped filesystem watcher for workspace {self.file_explorer.workspace_root_path}")
            self.observer = None

    async def events(self) -> AsyncGenerator[str, None]:
        """
        Async generator that yields change events from the internal event queue.
        
        Yields:
            str: The serialized FileSystemChangeEvent as JSON.
        """
        while True:
            event = await self._event_queue.get()
            yield event
