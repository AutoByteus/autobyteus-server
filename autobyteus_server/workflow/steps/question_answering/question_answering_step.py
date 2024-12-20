
import os
from autobyteus_server.workflow.types.base_step import BaseStep

class QuestionAnsweringStep(BaseStep):
    name = "question_answering"

    def __init__(self, workflow):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_dir = os.path.join(current_dir, "prompt")
        super().__init__(workflow, prompt_dir)
        # Add any question answering-specific initialization here if needed
