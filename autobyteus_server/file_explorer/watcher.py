# File: autobyteus-server/autobyteus_server/file_explorer/watcher.py

import asyncio
import logging
import os
from typing import Callable

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from autobyteus_server.file_explorer.file_system_changes import FileSystemChangeEvent, AddChange, DeleteChange, RenameChange
from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus_server.utils.pubsub import pubsub  # Updated import

logger = logging.getLogger(__name__)

class WatchdogHandler(FileSystemEventHandler):
    """
    Handler for filesystem events to convert them into FileSystemChangeEvents.
    """

    def __init__(self, file_explorer: FileExplorer, callback: Callable[[FileSystemChangeEvent], None]):
        super().__init__()
        self.file_explorer = file_explorer
        self.callback = callback

    def on_created(self, event: FileSystemEvent):
        logger.info(f"File created: {event.src_path}")
        relative_path = os.path.relpath(event.src_path, self.file_explorer.workspace_root_path)
        change_event = self.file_explorer.write_file_content(relative_path, "")
        self.callback(change_event)

    def on_deleted(self, event: FileSystemEvent):
        logger.info(f"File deleted: {event.src_path}")
        relative_path = os.path.relpath(event.src_path, self.file_explorer.workspace_root_path)
        try:
            change_event = self.file_explorer.remove_file_or_folder(relative_path)
            self.callback(change_event)
        except Exception as e:
            logger.error(f"Error removing file or folder: {e}")

    def on_moved(self, event: FileSystemEvent):
        logger.info(f"File moved from {event.src_path} to {event.dest_path}")
        src_relative = os.path.relpath(event.src_path, self.file_explorer.workspace_root_path)
        dest_relative = os.path.relpath(event.dest_path, self.file_explorer.workspace_root_path)
        
        # Handle rename as a rename change
        change_event = FileSystemChangeEvent(changes=[
            RenameChange(
                node=self.file_explorer.find_node_by_path(dest_relative),
                parent_id=self.file_explorer.get_parent_id(dest_relative),
                previous_id=self.file_explorer.get_node_id(src_relative)
            )
        ])
        self.callback(change_event)

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory:
            return  # Ignore directory modifications
        logger.info(f"File modified: {event.src_path}")
        relative_path = os.path.relpath(event.src_path, self.file_explorer.workspace_root_path)
        content = self.file_explorer.read_file_content(relative_path)
        change_event = FileSystemChangeEvent(changes=[
            AddChange(
                node=self.file_explorer.find_node_by_path(relative_path),
                parent_id=self.file_explorer.get_parent_id(relative_path)
            )
        ])
        self.file_explorer.file_contents[relative_path] = content
        self.callback(change_event)

class FileSystemWatcher:
    """
    Watches the filesystem for changes and notifies via callbacks.
    """

    def __init__(self, file_explorer: FileExplorer, loop: asyncio.AbstractEventLoop):
        self.file_explorer = file_explorer
        self.loop = loop
        self.observer = Observer()
        self.handler = WatchdogHandler(file_explorer, self.handle_change_event)

    def handle_change_event(self, change_event: FileSystemChangeEvent):
        logger.info(f"Change event detected: {change_event}")
        # Serialize the change event to JSON and publish via PubSub
        serialized_event = change_event.to_json()
        asyncio.run_coroutine_threadsafe(
            pubsub.publish(f"file_system_updated:{self.file_explorer.workspace_id}", serialized_event),
            self.loop
        )

    def start(self):
        self.observer.schedule(self.handler, self.file_explorer.workspace_root_path, recursive=True)
        self.observer.start()
        logger.info(f"Started filesystem watcher for workspace {self.file_explorer.workspace_id}")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        logger.info(f"Stopped filesystem watcher for workspace {self.file_explorer.workspace_id}")
