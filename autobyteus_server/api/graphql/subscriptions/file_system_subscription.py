# File: autobyteus_server/api/graphql/subscriptions/file_system_subscription.py

import asyncio
import strawberry
from typing import AsyncGenerator
from strawberry.subscriptions import AsyncPubSub

@strawberry.type
class FileSystemSubscription:
    """
    GraphQL Subscriptions for File Explorer operations.
    """

    @strawberry.subscription
    async def tree_updated(self, workspace_id: str) -> AsyncGenerator[None, None]:
        """
        Subscription that notifies when the directory tree is updated.

        Args:
            workspace_id (str): The ID of the workspace to listen for tree updates.

        Yields:
            TreeNodeType: The updated tree node information.
        """
        channel = f"tree_updated:{workspace_id}"
        async for event in AsyncPubSub.subscribe(channel):
            yield event
