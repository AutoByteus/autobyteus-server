import asyncio
import strawberry
from typing import AsyncGenerator
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.workflow.steps.subtask_implementation.subtask_implementation_step import SubtaskImplementationStep

workspace_manager = WorkspaceManager()

@strawberry.type
class StepResponse:
    conversation_id: str
    message: str

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
                message=f"Error: No workspace found for ID {workspace_id}"
            )
            return

        workflow = workspace.workflow
        if not workflow:
            yield StepResponse(
                conversation_id=conversation_id,
                message=f"Error: No workflow found for workspace {workspace_id}"
            )
            return

        step = workflow.get_step(step_id)
        
        while True:
            response = await step.get_latest_response(conversation_id)
            if response:
                yield StepResponse(
                    conversation_id=conversation_id,
                    message=response
                )
            else:
                await asyncio.sleep(1)  # Wait for 1 second before checking again