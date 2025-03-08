import asyncio
import strawberry
from typing import AsyncGenerator
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager

workspace_manager = WorkspaceManager()

@strawberry.type
class FileSystemSubscription:
    """
    GraphQL Subscriptions for File Explorer operations.
    """

    @strawberry.subscription
    async def file_system_changed(self, workspace_id: str) -> AsyncGenerator[str, None]:
        """
        Subscription that notifies when the file system is changed.
        Retrieves the workspace, accesses its FileExplorer's FileWatcher,
        and yields the latest event (if available) followed by new events.
        
        Args:
            workspace_id (str): The ID of the workspace to listen for file system changes.
        
        Yields:
            str: The serialized FileSystemChangeEvent as JSON.
        """
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            raise Exception("Workspace not found")

        file_watcher = workspace.file_explorer.file_watcher
        async for change_event in file_watcher.events():
            yield change_event
