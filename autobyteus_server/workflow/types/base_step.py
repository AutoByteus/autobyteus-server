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
from autobyteus_server.prompt.prompt_template import PromptTemplate
from autobyteus_server.workflow.types.base_workflow import BaseWorkflow
from autobyteus_server.workflow.utils.unique_id_generator import UniqueIDGenerator


class BaseStep(ABC):
    """
    BaseStep is the abstract base class for all steps in the automated coding workflow.
    Each step should inherit from this class and implement the required methods.
    """

    name = None
    prompt_template: PromptTemplate = None  # Instance of PromptTemplate

    def __init__(self, workflow: BaseWorkflow):
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
    def construct_prompt(self) -> str:
        """
        Construct the prompt for this step.

        Returns:
            str: The constructed prompt for this step.
        """
        pass

    @abstractmethod
    def process_response(self, response: str) -> None:
        """
        Process the response from the LLM API for this step.

        Args:
            response (str): The LLM API response as a string.
        """
        pass

    @abstractmethod
    def execute(self) -> None:
        """
        Execute the step.

        This method should be implemented in derived classes to define the step's execution logic.
        """
        raise NotImplementedError("Derived classes must implement the execute method.")