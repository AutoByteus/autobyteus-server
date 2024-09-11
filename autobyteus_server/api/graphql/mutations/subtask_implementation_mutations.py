"""
Module: subtask_implementation_mutations

This module provides GraphQL mutations related to subtask implementation operations.
"""

import json
import logging
import strawberry
from typing import List, Optional
from autobyteus_server.workflow.steps.subtask_implementation.subtask_implementation_step import SubtaskImplementationStep
from autobyteus.tools.file_tool import FileTool
from autobyteus.llm.models import LLMModel
from autobyteus.llm.llm_factory import LLMFactory

# Logger setup
logger = logging.getLogger(__name__)

@strawberry.type
class SubtaskImplementationMutation:
    @strawberry.mutation
    async def run_subtask_implementation(
        self, 
        context_file_paths: List[str], 
        implementation_requirement: str,
        workspace_root_path: str,
        llm_model: Optional[LLMModel] = None
    ) -> str:
        """
        Runs the subtask implementation step with the provided context file paths, implementation requirement, and LLM model.

        Args:
            context_file_paths (List[str]): List of file paths to include in the context for implementation.
            implementation_requirement (str): The requirement for the subtask implementation.
            workspace_root_path (str): The root path of the workspace.
            llm_model (Optional[LLMModel]): The LLM model to use for the implementation. 
                                            Defaults to Claude 3.5 Sonnet if not specified.

        Returns:
            str: The result of the subtask implementation.
        """
        try:
            # Use Claude 3.5 Sonnet as default if no model is specified
            if llm_model is None:
                llm_model = LLMModel.CLAUDE_3_5_SONNET

            # Initialize LLM using the factory
            llm_factory = LLMFactory()
            llm = llm_factory.create_llm(llm_model)

            # Initialize tools
            tools = [FileTool()]  # Add more tools as needed

            # Create and execute the subtask implementation step
            step = SubtaskImplementationStep(llm, tools)
            result = await step.execute(context_file_paths, implementation_requirement)

            return result
        except Exception as e:
            error_message = f"Error while running subtask implementation: {str(e)}"
            logger.error(error_message)
            return json.dumps({"error": error_message})
