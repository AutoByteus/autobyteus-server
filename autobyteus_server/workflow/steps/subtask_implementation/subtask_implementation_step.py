import os
import logging
from autobyteus_server.workflow.types.base_step import BaseStep

logger = logging.getLogger(__name__)

class SubtaskImplementationStep(BaseStep):
    name = "implementation"

    def __init__(self, workflow):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_dir = os.path.join(current_dir, "prompt")
        super().__init__(workflow, prompt_dir)