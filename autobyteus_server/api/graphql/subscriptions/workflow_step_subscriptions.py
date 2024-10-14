import asyncio
import strawberry
from typing import AsyncGenerator
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager

workspace_manager = WorkspaceManager()

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def step_response(self, workspace_id: str, step_id: str) -> AsyncGenerator[str, None]:
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            yield f"Error: No workspace found for ID {workspace_id}"
            return

        workflow = workspace.workflow
        if not workflow:
            yield f"Error: No workflow found for workspace {workspace_id}"
            return

        step = workflow.get_step(step_id)
        if not isinstance(step, BaseStep):
            yield f"Error: Step {step_id} is not a valid workflow step"
            return

        while True:
            response = await step.get_latest_response()
            if response:
                yield response
            else:
                await asyncio.sleep(1)  # Wait for 1 second before checking again