"""
Module: subtask_implementation_mutations

This module provides GraphQL mutations related to subtask implementation operations.
"""

import asyncio
import json
import logging
import strawberry
from typing import List, Optional, AsyncGenerator
from autobyteus_server.workflow.steps.subtask_implementation.subtask_implementation_step import SubtaskImplementationStep
from autobyteus.llm.models import LLMModel
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager
from autobyteus_server.api.graphql.types.llm_model_types import LLMModel as GraphQLLLMModel, convert_to_original_llm_model

# Logger setup
logger = logging.getLogger(__name__)

workspace_manager = WorkspaceManager()

@strawberry.type
class SubtaskImplementationMutation:
    @strawberry.mutation
    async def configure_step_llm(
        self,
        workspace_root_path: str,
        step_id: str,
        llm_model: GraphQLLLMModel
    ) -> str:
        try:
            workflow = workspace_manager.workflows.get(workspace_root_path)
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
    async def send_implementation_requirement(
        self,
        workspace_root_path: str,
        step_id: str,
        context_file_paths: List[str],
        implementation_requirement: str
    ) -> str:
        try:
            workflow = workspace_manager.workflows.get(workspace_root_path)
            if not workflow:
                return f"Error: No workflow found for workspace {workspace_root_path}"

            step = workflow.get_step(step_id)
            if not isinstance(step, SubtaskImplementationStep):
                return f"Error: Step {step_id} is not a SubtaskImplementationStep"

            # Process the requirement
            await step.process_requirement(
                implementation_requirement,
                context_file_paths
            )
            return f"Requirement sent for processing. Subscribe to 'implementationResponse' for updates."

        except Exception as e:
            return f"Error processing implementation requirement: {str(e)}"