import logging
from typing import List, Optional
import strawberry
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
        try:
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

        except Exception as e:
            return f"Error configuring LLM model: {str(e)}"

    @strawberry.mutation
    async def send_step_requirement(
        self,
        workspace_id: str,
        step_id: str,
        context_file_paths: List[ContextFilePathInput],
        requirement: str,
        llm_model: Optional[GraphQLLLMModel] = None
    ) -> str:
        try:
            workspace = workspace_manager.get_workspace_by_id(workspace_id)
            if not workspace:
                return f"Error: No workspace found for ID {workspace_id}"

            workflow = workspace.workflow
            if not workflow:
                return f"Error: No workflow found for workspace {workspace_id}"

            step = workflow.get_step(step_id)
            if not isinstance(step, BaseStep):
                return f"Error: Step {step_id} is not a valid workflow step"

            llm_model_name = llm_model.name if llm_model else None

            # Convert ContextFileInput to the expected format
            processed_context_files = [{"path": cf.path, "type": cf.type} for cf in context_file_paths]

            # Process the requirement
            agent_id = await step.process_requirement(
                requirement,
                processed_context_files,
                llm_model_name
            )

            if agent_id:
                return f"New agent created (ID: {agent_id}) and requirement sent for processing. Subscribe to 'stepResponse' for updates."
            else:
                return "Requirement sent for processing using existing agent. Subscribe to 'stepResponse' for updates."

        except Exception as e:
            logger.exception(e)
            return f"Error processing step requirement: {str(e)}"

    @strawberry.mutation
    def set_llm_api_key(self, model: str, api_key: str) -> str:
        """
        Set the API key for a specific LLM model.
        """
        try:
            config.set_llm_api_key(model, api_key)
            return f"API key for model {model} has been set successfully."
        except Exception as e:
            logger.exception(e)
            return f"Error setting API key: {str(e)}"

    @strawberry.mutation
    def get_llm_api_key(self, model: str) -> str:
        """
        Get the API key for a specific LLM model.
        """
        try:
            api_key = config.get_llm_api_key(model)
            return api_key if api_key else "API key not found for this model."
        except Exception as e:
            logger.exception(e)
            return f"Error retrieving API key: {str(e)}"