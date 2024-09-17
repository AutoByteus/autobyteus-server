from typing import List
from autobyteus_server.workflow.types.base_step import BaseStep
import os

class RequirementStep(BaseStep):
    name = "requirement"
    
    def __init__(self, workflow):

        super().__init__(workflow)
        # Read the prompt template
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "prompt", "requirement.prompt")
        self.read_prompt_template(prompt_path)

    def construct_initial_prompt(self, requirement: str, context: str) -> str:
        return self.prompt_template.fill({
            "requirement": requirement,
            "context": context
        })
    
    async def process_requirement(
        self, 
        requirement: str, 
        context_file_paths: List[str]
    ) -> str:
        if not self.llm_model:
            raise ValueError("LLM model not configured for this step.")
        
        context = self._construct_context(context_file_paths)
        prompt = self.construct_initial_prompt(requirement, context)
        
        # Use self.llm_model to process the requirement
        # This is a placeholder. Replace with actual LLM processing logic.
        result = await self.llm_model.generate(prompt)
        
        return f"Processed requirement: {result}"

    def _construct_context(self, context_file_paths: List[str]) -> str:
        # Implement context construction logic
        return f"Context constructed from {len(context_file_paths)} files."