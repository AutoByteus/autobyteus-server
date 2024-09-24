# autobyteus_server/workflow/automated_coding_workflow.py
"""
automated_coding_workflow.py: Contains the AutomatedCodingWorkflow class, which represents the main entry point for running the automated coding workflow.
"""

import json
from typing import Dict, Optional
from autobyteus_server.workflow.config import WORKFLOW_CONFIG
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus_server.workflow.types.base_workflow import WorkflowStatus
from autobyteus_server.workflow.types.workflow_template_config import StepsTemplateConfig

class AutomatedCodingWorkflow:
    """
    A class to represent and manage a fully automated coding workflow.

    The workflow is composed of multiple steps, each step represented as an instance of a class derived from BaseStep. Steps can have sub-steps, forming a potentially multi-level workflow.

    Attributes:
        steps (Dict[str, BaseStep]): A dictionary of step instances keyed by their step IDs.
        name (str): The name of the workflow. Default is "automated_coding_workflow".
        config (dict): The configuration details for the workflow. Loaded from `WORKFLOW_CONFIG`.
    """

    name = "automated_coding_workflow"
    config = WORKFLOW_CONFIG

    def __init__(self):
        """
        Initialize the AutomatedCodingWorkflow.
        """
        self._workspace = None
        self.steps: Dict[str, BaseStep] = {}
        self._initialize_steps(AutomatedCodingWorkflow.config['steps'])
    
    @property
    def workspace(self):
        """
        Get the workspace associated with this workflow.

        Returns:
            Workspace: The workspace associated with this workflow.
        """
        return self._workspace

    @workspace.setter
    def workspace(self, value: 'Workspace'):
        """
        Set the workspace associated with this workflow.

        Args:
            value (Workspace): The workspace to associate with this workflow.
        """
        self._workspace = value

    def _initialize_steps(self, steps_config: Dict[str, StepsTemplateConfig]):
        """
        Initializes the steps of the workflow from a given configuration.

        If a step has sub-steps, it recursively initializes those as well.

        :param steps_config: A dictionary containing step configuration.
        """
        for step_id, step_config in steps_config.items():
            step_class = step_config['step_class']
            step_instance: BaseStep = step_class(self)
            self.steps[step_instance.id] = step_instance

            if 'steps' in step_config:
                self._initialize_steps(step_config['steps'])

    def to_json(self) -> str:
        """
        Converts the workflow instance to a JSON representation, including its steps.

        Returns:
            str: The JSON representation of the workflow instance.
        """
        workflow_data = {
            "name": self.name,
            "steps": {step_id: step.to_dict() for step_id, step in self.steps.items()}
        }

        return json.dumps(workflow_data)
    
    def get_step(self, step_id: str) -> Optional[BaseStep]:
        """
        Retrieve a step from the workflow based on its ID.

        Args:
            step_id (str): The ID of the step to retrieve.

        Returns:
            Optional[BaseStep]: The step instance if found, None otherwise.
        """
        return self.steps.get(step_id)

    def execute_step(self, step_id: str) -> Optional[str]:
        """
        Execute a specific step within the workflow using its ID.

        Args:
            step_id (str): The ID of the step to execute.

        Returns:
            Optional[str]: The step result or None if the step_id is invalid.

        Raises:
            ValueError: If the provided step_id is invalid.
        """
        step = self.get_step(step_id)
        if step:
            return step.execute()
        else:
            raise ValueError(f"Invalid step_id: {step_id}")

    def start_workflow(self):
        """
        Set the status of the workflow to Started and raise a NotImplementedError for derived classes to implement.
        """
        self.status = WorkflowStatus.Started