"""
Module for handling command execution within a workspace context.
"""

from dataclasses import dataclass
from autobyteus.tools.bash.bash_executor import BashExecutor
import logging

logger = logging.getLogger(__name__)

@dataclass
class CommandExecutionResult:
    """Results from command execution."""
    success: bool
    message: str

class CommandExecutor:
    """
    Handles command execution within a specific workspace context.
    """
    def __init__(self, workspace_root_path: str):
        """
        Initialize the CommandExecutor.

        Args:
            workspace_root_path (str): The root path where commands will be executed.
        """
        self.workspace_root_path = workspace_root_path
        self.bash_executor = BashExecutor()

    def execute_command(self, command: str) -> CommandExecutionResult:
        """
        Execute a command in the workspace context.

        Args:
            command (str): The command to execute.

        Returns:
            CommandExecutionResult: The result of the command execution.
        """
        try:
            # Ensure command runs in workspace directory
            full_command = f"cd {self.workspace_root_path} && {command}"
            output = self.bash_executor.execute(command=full_command)
            
            return CommandExecutionResult(
                success=True,
                message=output
            )
        except Exception as e:
            error_message = f"Command execution failed: {str(e)}"
            logger.error(error_message)
            return CommandExecutionResult(
                success=False,
                message=error_message
            )