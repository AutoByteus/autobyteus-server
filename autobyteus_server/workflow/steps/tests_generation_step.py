"""
test_generation_step.py

This module contains the TestGenerationStep class, which represents the test generation step of the automated coding workflow.
"""
from typing import List, Optional
from autobyteus.llm.models import LLMModel
from autobyteus.prompt.prompt_template import PromptTemplate
from autobyteus.prompt.prompt_template_variable import PromptTemplateVariable
from autobyteus_server.workflow.types.base_step import BaseStep


class TestsGenerationStep(BaseStep):
    name = "generate_tests"
    # Define the PromptTemplateVariable
    code_variable = PromptTemplateVariable(name="code", 
                                           source=PromptTemplateVariable.SOURCE_USER_INPUT, 
                                           allow_code_context_building=True, 
                                           allow_llm_refinement=False)

    # Define the PromptTemplate
    prompt_template = PromptTemplate(
        template="""
        You are a senior Python software engineer. You have been given a Python code file provided in the `[Code]` section. Your task is to create integration for the given Python code file.

        [Criteria]
        - Ensure that the test cases follow pytest best practices.
        - Create the test file path to follow the same practice used in the current project's test files structure:
            src
                - ...
                - semantic_code
                    - embedding
                        - openai_embedding_creator.py
            tests
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

        - Ensure that the tests provide full coverage of the code.
        - Use behavior-driven naming conventions for the test cases.

        [Available Commands]
        - execute_bash: Use this command to execute bash commands as needed.
        - write_file: Use this command to write the test cases to a file.

        Think and reason yourself in high detail to address the task.

        [Code]
        {code}
        """,
        variables=[code_variable]
    )
    
    def construct_initial_prompt(self, requirement: str, context: str) -> str:
        """
        Construct the initial prompt for the test generation step.

        Args:
            requirement (str): The requirement for the test generation step.
            context (str): The context string for the test generation step.

        Returns:
            str: The constructed prompt for the test generation step.
        """
        prompt = f"Please provide the requirements for the project:\n\nRequirement: {requirement}\n\nContext: {context}"
        return prompt
    
    async def process_requirement(
        self, 
        requirement: str, 
        context_file_paths: List[str], 
        llm_model: Optional[LLMModel] = None
    ) -> str:
        """
        Process the requirement for the test generation step.

        Args:
            requirement (str): The requirement to be processed.
            context_file_paths (List[str]): List of file paths providing context.
            llm_model (Optional[LLMModel]): The LLM model to be used, if any.

        Returns:
            str: The processed result.
        """
        # Process the requirement specific to the test generation step.
        # This is a placeholder implementation. You should replace it with actual logic.
        context = self._construct_context(context_file_paths)
        prompt = self.construct_initial_prompt(requirement, context)
        
        # Here you would typically use the LLM to generate the tests
        # For now, we'll just return a placeholder message
        return f"Test generation process initiated with prompt: {prompt}"

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
