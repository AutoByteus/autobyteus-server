
import os
from autobyteus_server.workflow.types.base_step import BaseStep

class PromptCreationStep(BaseStep):
    name = "prompt_creation"

    def __init__(self, workflow):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_dir = os.path.join(current_dir, "prompt")
        super().__init__(workflow, prompt_dir)
        # Add any prompt creation-specific initialization here if needed
