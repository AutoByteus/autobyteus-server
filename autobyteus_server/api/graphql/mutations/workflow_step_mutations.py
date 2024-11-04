import logging
from typing import List, Optional
import strawberry
from autobyteus_server.config import config
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.api.graphql.types.llm_model_types import LLMModel as GraphQLLLMModel

# Logger setup
logger = logging.getLogger(__name__)

workspace_manager = WorkspaceManager()

@strawberry.input
class ContextFilePathInput:
    path: str
    type: str

@strawberry.type
class WorkflowStepMutation:
    @strawberry.mutation
    async def configure_step_llm(
        self,
        workspace_id: str,
        step_id: str,
        llm_model: GraphQLLLMModel
    ) -> str:
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            return f"Error: No workspace found for ID {workspace_id}"

        workflow = workspace.workflow
        if not workflow:
            return f"Error: No workflow found for workspace {workspace_id}"

        step = workflow.get_step(step_id)
        if not step:
            return f"Error: Step {step_id} not found in the workflow"

        step.configure_llm_model(llm_model.value)
        return f"LLM model configured successfully for step {step_id}"

    @strawberry.mutation
    async def send_step_requirement(
        self,
        workspace_id: str,
        step_id: str,
        context_file_paths: List[ContextFilePathInput],
        requirement: str,
        conversation_id: Optional[str] = None,
        llm_model: Optional[GraphQLLLMModel] = None
    ) -> str:
        workspace = workspace_manager.get_workspace_by_id(workspace_id)
        if not workspace:
            return f"Error: No workspace found for ID {workspace_id}"

        workflow = workspace.workflow
        if not workflow:
            return f"Error: No workflow found for workspace {workspace_id}"

        step = workflow.get_step(step_id)
        if not isinstance(step, BaseStep):
            return f"Error: Step {step_id} is not a valid workflow step"

        llm_model_name = llm_model.value if llm_model else None

        # Convert ContextFileInput to the expected format
        processed_context_files = [{"path": cf.path, "type": cf.type} for cf in context_file_paths]

        # Process the requirement
        conversation_id = await step.process_requirement(
            requirement,
            processed_context_files,
            llm_model_name,
            conversation_id
        )

        return conversation_id