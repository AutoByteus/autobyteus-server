"""
Module: python_project_refactorer

This module offers the PythonProjectRefactorer class which is tasked with refactoring Python projects.
It provides mechanisms to organize, structure, and refactor Python source code in alignment with 
best practices and standards specific to Python development.
"""
import logging
import os
from autobyteus.prompt.prompt_template import PromptTemplate
from autobyteus_server.file_explorer.file_explorer import FileExplorer
from autobyteus_server.file_explorer.tree_node import TreeNode
from autobyteus_server.workspaces.workspace import Workspace
from autobyteus_server.workspaces.workspace_tools.workspace_refactorer.base_project_refactorer import BaseProjectRefactorer

# Logger setup
logger = logging.getLogger(__name__)

class PythonProjectRefactorer(BaseProjectRefactorer):
    """
    Class to refactor Python projects.
    """
    
    # Define the prompt template string
    template_str = """
    You are a top python software engineer who creates maintainable and understandable codes. You are given a task located between '$start$' and '$end$' tokens in the `[Task]` section.

    [Criterias]
    - Follow python PEP8 best practices. Don't forget add or update file-level docstring
    - Include complete updated code in code block. Do not use placeholders.

    Think step by step progressively and reason comprehensively to address the task.

    [Task]
    $start$
    Please examine the source code in file {file_path}
    ```
    {source_code}
    ```
    $end$
    """

    # Define the class-level prompt_template without variables
    prompt_template: PromptTemplate = PromptTemplate(template=template_str)

    def __init__(self, workspace: Workspace):
        """
        Constructor for PythonProjectRefactorer.

        Args:
            workspace (Workspace): The workspace to be refactored.
        """
        self.workspace: Workspace = workspace

    def refactor(self):
        """
        Refactor the Python project.

        This method iterates over each Python file in the src directory and replaces its content 
        with the refactored code from LLM.
        """
        directory_tree: FileExplorer = self.workspace.file_explorer
        root_node = directory_tree.get_tree()

        for file_node in self._traverse_tree_and_collect_files(root_node):
            self._apply_refactored_code(file_node)

    def construct_prompt(self, file_path: str):
        """
        Construct the prompt for the Python file refactoring.

        Args:
            file_path (str): The path to the Python file.

        Returns:
            str: The constructed prompt for the Python file refactoring.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source_code = file.read()
        except (UnicodeDecodeError, PermissionError):
            source_code = ""

        prompt = self.prompt_template.fill({"file_path": file_path, "source_code": source_code})
        return prompt

    def _traverse_tree_and_collect_files(self, node: TreeNode) -> list:
            """
            Recursively traverse the directory tree and collect all valid python file nodes.

            Args:
                node (TreeNode): The current node being inspected.

            Returns:
                list[TreeNode]: List of all valid python file nodes.
            """
            valid_files = []
            if node.is_file and "src" in node.path and "__init__.py" not in node.path:
                valid_files.append(node)
            for child in node.children:
                valid_files.extend(self._traverse_tree_and_collect_files(child))
            return valid_files

    def _apply_refactored_code(self, file_node: TreeNode):
        """
        Send the content of the file to the LLM model for refactoring and replace the file content 
        with the refactored code.
        """
        prompt = self.construct_prompt(file_node.path)
        refactored_code = self.llm_integration.process_input_messages([prompt])
        
        logger.info(refactored_code)
