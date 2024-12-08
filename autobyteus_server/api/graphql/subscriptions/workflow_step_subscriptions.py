import asyncio
import strawberry
from typing import AsyncGenerator
from autobyteus_server.api.graphql.types.step_response import StepResponse
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.api.graphql.converters import to_graphql_step_response

workspace_manager = WorkspaceManager()

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def step_response(
        self, 
        workspace_id: str, 
        step_id: str, 
        conversation_id: str
    ) -> AsyncGenerator[StepResponse, None]:
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            yield StepResponse(
                conversation_id=conversation_id,
                message_chunk=f"Error: No workspace found for ID {workspace_id}",
                is_complete=True
            )
            return

        workflow = workspace.workflow
        if not workflow:
            yield StepResponse(
                conversation_id=conversation_id,
                message_chunk=f"Error: No workflow found for workspace {workspace_id}",
                is_complete=True
            )
            return

        step = workflow.get_step(step_id)
        streaming_conversation = step.conversation_manager.get_conversation(conversation_id)
        
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
            streaming_conversation.close()