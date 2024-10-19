from typing import List, Optional
from autobyteus_server.workflow.types.base_step import BaseStep
import os
from autobyteus.llm.llm_factory import LLMFactory

class RequirementStep(BaseStep):
    name = "requirement"
    
    def __init__(self, workflow):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_dir = os.path.join(current_dir, "prompt")
        super().__init__(workflow, prompt_dir)

    def construct_initial_prompt(self, requirement: str, context: str, llm_model: str) -> str:
        return self.get_prompt_template(llm_model).fill({
            "requirement": requirement,
            "context": context
        })
    
    async def process_requirement(
        self, 
        requirement: str, 
        context_file_paths: List[str],
        llm_model: Optional[str] = None
    ) -> str:
        model_to_use = llm_model or self.llm_model
        if not model_to_use:
            raise ValueError("LLM model not configured for this step.")
        
        context = self._construct_context(context_file_paths)
        prompt = self.construct_initial_prompt(requirement, context, model_to_use)
        
        # Use model_to_use to process the requirement
        # This is a placeholder. Replace with actual LLM processing logic.
        llm_instance = LLMFactory.create_llm(model_to_use)
        result = await llm_instance.generate(prompt)
        
        return f"Processed requirement: {result}"

    def _construct_context(self, context_file_paths: List[str]) -> str:
        # Implement context construction logic
        return f"Context constructed from {len(context_file_paths)} files."