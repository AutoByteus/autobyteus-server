import asyncio
import strawberry
from typing import AsyncGenerator, Optional
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager

workspace_manager = WorkspaceManager()
@strawberry.type
class StepResponse:
    response: str
    cost: float

def get_step(workspace_id: str, step_id: str) -> Optional[BaseStep]:
    workspace = workspace_manager.get_workspace_by_id(workspace_id)
    if not workspace:
        return None
    workflow = workspace.workflow
    if not workflow:
        return None
    step = workflow.get_step(step_id)
    return step
@strawberry.type
class Subscription:
    @strawberry.subscription
    async def step_response(
        self,
        workspace_id: str,
        step_id: str
    ) -> AsyncGenerator[StepResponse, None]:
        step = get_step(workspace_id, step_id)
        if not step:
            yield StepResponse(response="Error: Invalid step", cost=0.0)
            return

        while True:
            response = await step.get_latest_response()
            if response:
                cost = step.get_current_cost()
                yield StepResponse(response=response, cost=cost)
            else:
                await asyncio.sleep(1)  # Wait for 1 second before checking again