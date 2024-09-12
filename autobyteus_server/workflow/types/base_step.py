"""
autobyteus/workflow_types/types/base_step.py

This module contains the BaseStep class, which serves as an abstract base class for all steps in the automated coding
workflow. Each step in the workflow should inherit from this class and implement the required methods. The BaseStep
class provides a foundation for creating custom steps with unique IDs, names, and prompt construction.

BaseStep class features:
- Unique ID generation for each step instance.
- A class attribute for the step name.
- Abstract methods for constructing prompts and processing responses that need to be implemented in derived classes.
- A method called execute for triggering the step's execution, which needs to be implemented in derived classes.

To create a new step, inherit from the BaseStep class, set the step name using the set_step_name class method,
and implement the required abstract methods and the execute method.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from autobyteus.prompt.prompt_template import PromptTemplate
from autobyteus_server.workflow.types.base_workflow import BaseWorkflow
from autobyteus_server.workflow.utils.unique_id_generator import UniqueIDGenerator
from autobyteus.llm.models import LLMModel
from autobyteus.events.event_emitter import EventEmitter


class BaseStep(ABC, EventEmitter):
    """
    BaseStep is the abstract base class for all steps in the automated coding workflow.
    Each step should inherit from this class and implement the required methods.
    """

    name: str
    prompt_template: str

    def __init__(self, workflow: BaseWorkflow):
        super().__init__()  # Initialize EventEmitter
        self.id = UniqueIDGenerator.generate_id()
        self.workflow = workflow

    def to_dict(self) -> dict:
        """
        Converts the BaseStep instance to a dictionary representation.

        Returns:
            dict: Dictionary representation of the BaseStep instance.
        """
        return {
            "id": self.id,
            "name": self.name,
            "prompt_template": self.prompt_template.to_dict() if self.prompt_template else None
        }

    @abstractmethod
    def construct_initial_prompt(self, requirement: str, context: str) -> str:
        """
        Construct the initial prompt for the step.

        Args:
            requirement (str): The requirement for the step.
            context (str): The context string for the step.

        Returns:
            str: The constructed initial prompt for the step.
        """
        pass

    @abstractmethod
    async def process_requirement(
        self, 
        requirement: str, 
        context_file_paths: List[str], 
        llm_model: Optional[LLMModel] = None
    ) -> str:
        """
        Process the requirement for the step.

        Args:
            requirement (str): The requirement to be processed.
            context_file_paths (List[str]): List of file paths providing context.
            llm_model (Optional[LLMModel]): The LLM model to be used, if any.

        Returns:
            str: The processed result.
        """
        pass