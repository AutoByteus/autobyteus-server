# autobyteus/workflow/steps/requirement_step.py

"""
requirement_step.py

This module contains the RequirementStep class, derived from the BaseStep class.
"""

from typing import List, Optional
from autobyteus.llm.models import LLMModel
from autobyteus.prompt.prompt_template import PromptTemplate
from autobyteus.prompt.prompt_template_variable import PromptTemplateVariable
from autobyteus_server.workflow.types.base_step import BaseStep

class RequirementStep(BaseStep):
    name = "requirement"
    
    # Define the PromptTemplateVariable
    requirement_variable = PromptTemplateVariable(name="requirement", 
                                                  source=PromptTemplateVariable.SOURCE_USER_INPUT, 
                                                  allow_code_context_building=True, 
                                                  allow_llm_refinement=True)

    # Define the PromptTemplate
    prompt_template = PromptTemplate(
        template="""
        As the best Python software engineer on earth, address the requirements outlined between the `$start$` and `$end$` tokens in the `[Requirement]` section.
        [Guidelines]
        - Use appropriate design patterns where necessary.
        - Follow SOLID principles and Python's best coding practices.
        - Consider refactoring where necessary.
        - Follow python docstring best practices, ensuring each file begins with a file-level docstring.
        - Include file paths with their complete codes in code block in the output, so I can easily copy and paste. Do not use placeholders.
        - Explain whether to create a new folder or use an existing one for file placement. Use descriptive naming conventions for files and folders that correlate with the requirement's features. For context, 
            the current project's file structure looks like this:
            - src
                - ...
                - semantic_code
                    - embedding
                        - openai_embedding_creator.py
            - tests
                - unit_tests
                    - ...
                    - semantic_code
                        - embedding
                            - test_openai_embedding_creator.py
                - integration_tests
                    - ...
                    - semantic_code
                        - index
                            - test_index_service_integration.py
                    
        - Always use absolute imports over relative ones.
        - Update docstrings in line with any code modifications.

        Think step by step, and reason comprehensively to address the task.
        [Requirement]
        $start$
        {requirement}
        $end$

        [Context]
        {context}
        """,
        variables=[requirement_variable]
    )
    
    def construct_initial_prompt(self, requirement: str, context: str) -> str:
        """
        Construct the initial prompt for the requirement step.

        Args:
            requirement (str): The requirement to be filled in the prompt_template.
            context (str): The context string for the requirement step.

        Returns:
            str: The constructed prompt for the requirement step.
        """
        # Use the PromptTemplate's method to fill in the variables
        prompt = self.prompt_template.fill({"requirement": requirement, "context": context})
        return prompt
    
    async def process_requirement(
        self, 
        requirement: str, 
        context_file_paths: List[str], 
        llm_model: Optional[LLMModel] = None
    ) -> str:
        """
        Process the requirement for this step.

        Args:
            requirement (str): The requirement to be processed.
            context_file_paths (List[str]): List of file paths providing context.
            llm_model (Optional[LLMModel]): The LLM model to be used, if any.

        Returns:
            str: The processed result.
        """
        context = self._construct_context(context_file_paths)
        prompt = self.construct_initial_prompt(requirement, context)
        
        # Here you would typically use the LLM to process the requirement
        # For now, we'll just return a placeholder message
        return f"Requirement processing initiated with prompt: {prompt}"

    def _construct_context(self, context_file_paths: List[str]) -> str:
        """
        Construct the context string from the given file paths.

        Args:
            context_file_paths (List[str]): List of file paths to construct context from.

        Returns:
            str: The constructed context string.
        """
        # This is a placeholder implementation. You should replace it with actual logic
        # to read the files and construct the context string.
        return f"Context constructed from {len(context_file_paths)} files."

