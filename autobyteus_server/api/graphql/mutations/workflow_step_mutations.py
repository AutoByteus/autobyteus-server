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
            raise ValueError(f"No workspace found for ID {workspace_id}")

        workflow = workspace.workflow
        if not workflow:
            raise ValueError(f"No workflow found for workspace {workspace_id}")

        step = workflow.get_step(step_id)
        if not isinstance(step, BaseStep):
            raise ValueError(f"Step {step_id} is not a valid workflow step")

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

    @strawberry.mutation
    async def close_conversation(
        self,
        workspace_id: str,
        step_id: str,
        conversation_id: str
    ) -> bool:
        """
        Close a specific conversation and clean up its resources.
        
        Args:
            workspace_id (str): ID of the workspace
            step_id (str): ID of the step
            conversation_id (str): ID of the conversation to close
            
        Returns:
            bool: True if the conversation was successfully closed
            
        Raises:
            ValueError: If workspace, workflow, or step is not found
            Exception: If there's an error during conversation closure
        """
        try:
            workspace = workspace_manager.get_workspace_by_id(workspace_id)
            if not workspace:
                raise ValueError(f"No workspace found for ID {workspace_id}")

            workflow = workspace.workflow
            if not workflow:
                raise ValueError(f"No workflow found for workspace {workspace_id}")

            step = workflow.get_step(step_id)
            if not isinstance(step, BaseStep):
                raise ValueError(f"Step {step_id} is not a valid workflow step")

            # Attempt to close the conversation
            step.close_conversation(conversation_id)
            return True
            
        except Exception as e:
            logger.error(f"Error closing conversation: {str(e)}")
            raise