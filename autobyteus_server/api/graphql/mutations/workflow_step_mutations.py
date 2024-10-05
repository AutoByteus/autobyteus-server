"""
Module: workflow_step_mutations

This module provides GraphQL mutations related to workflow step operations.
"""

import logging
from typing import List, Optional
import strawberry
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus.llm.models import LLMModel
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.api.graphql.types.llm_model_types import LLMModel as GraphQLLLMModel, convert_to_original_llm_model

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
        workspace_root_path: str,
        step_id: str,
        llm_model: GraphQLLLMModel
    ) -> str:
        try:
            workspace = workspace_manager.get_workspace(workspace_root_path)
            if not workspace:
                return f"Error: No workspace found for path {workspace_root_path}"

            workflow = workspace.workflow
            if not workflow:
                return f"Error: No workflow found for workspace {workspace_root_path}"

            step = workflow.get_step(step_id)
            if not step:
                return f"Error: Step {step_id} not found in the workflow"

            original_llm_model = convert_to_original_llm_model(llm_model)
            step.configure_llm_model(original_llm_model)
            
            return f"LLM model configured successfully for step {step_id}"

        except Exception as e:
            return f"Error configuring LLM model: {str(e)}"

    @strawberry.mutation
    async def send_step_requirement(
        self,
        workspace_root_path: str,
        step_id: str,
        context_file_paths: List[ContextFilePathInput],
        requirement: str,
        llm_model: Optional[GraphQLLLMModel] = None
    ) -> str:
        try:
            workspace = workspace_manager.get_workspace(workspace_root_path)
            if not workspace:
                return f"Error: No workspace found for path {workspace_root_path}"

            workflow = workspace.workflow
            if not workflow:
                return f"Error: No workflow found for workspace {workspace_root_path}"

            step = workflow.get_step(step_id)
            if not isinstance(step, BaseStep):
                return f"Error: Step {step_id} is not a valid workflow step"

            original_llm_model = convert_to_original_llm_model(llm_model) if llm_model else None

            # Convert ContextFileInput to the expected format
            processed_context_files = [{"path": cf.path, "type": cf.type} for cf in context_file_paths]

            # Process the requirement
            agent_id = await step.process_requirement(
                requirement,
                processed_context_files,
                original_llm_model
            )

            if agent_id:
                return f"New agent created (ID: {agent_id}) and requirement sent for processing. Subscribe to 'stepResponse' for updates."
            else:
                return "Requirement sent for processing using existing agent. Subscribe to 'stepResponse' for updates."

        except Exception as e:
            logger.exception(e)
            return f"Error processing step requirement: {str(e)}"