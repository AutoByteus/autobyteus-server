
import asyncio
import strawberry
from typing import AsyncGenerator
from autobyteus_server.api.graphql.types.step_response import StepResponse
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.api.graphql.converters import to_graphql_step_response
from autobyteus_server.ai_terminal.runtime.ai_terminal_agent_conversation_manager import AITerminalAgentConversationManager

workspace_manager = WorkspaceManager()
streaming_manager = AITerminalAgentConversationManager()

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def ai_terminal_response(
        self, 
        workspace_id: str, 
        conversation_id: str
    ) -> AsyncGenerator[StepResponse, None]:
        """
        Subscribe to AI Terminal responses for a given conversation.
        """
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            yield StepResponse(
                conversation_id=conversation_id,
                message_chunk=f"Error: No workspace found for ID {workspace_id}",
                is_complete=True
            )
            return

        streaming_conversation = streaming_manager.get_conversation(conversation_id)
        if not streaming_conversation:
            yield StepResponse(
                conversation_id=conversation_id,
                message_chunk=f"Error: No conversation found with ID {conversation_id}",
                is_complete=True
            )
            return

        try:
            async for response_data in streaming_conversation:
                if response_data:
                    yield to_graphql_step_response(conversation_id, response_data)
        finally:
            # No explicit close here as it's handled by the mutation
            pass
