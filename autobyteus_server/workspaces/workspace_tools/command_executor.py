"""
Module for handling command execution within a workspace context.
"""

from dataclasses import dataclass
from autobyteus.tools.bash.bash_executor import BashExecutor
from autobyteus.events.event_types import EventType
import logging
import subprocess


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

    async def execute_command(self, command: str) -> CommandExecutionResult:
        """
        Execute a command in the workspace context.

        Args:
            command (str): The command to execute.

        Returns:
            CommandExecutionResult: The result of the command execution.
        """
        logger.debug(f"Preparing to execute command: {command} in workspace: {self.workspace_root_path}")
        try:
            # Ensure command runs in workspace directory
            full_command = f"cd {self._escape_path(self.workspace_root_path)} && {command}"
            logger.debug(f"Full command: {full_command}")
            output = await self.bash_executor.execute(command=full_command)

            logger.info(f"Command executed successfully: {command}")
            return CommandExecutionResult(
                success=True,
                message=output
            )
        except subprocess.CalledProcessError as e:
            error_message = f"Command execution failed with return code {e.returncode}: {e.stderr}"
            logger.error(error_message)
            return CommandExecutionResult(
                success=False,
                message=error_message
            )
        except Exception as e:
            error_message = f"An unexpected error occurred during command execution: {str(e)}"
            logger.exception(error_message)
            return CommandExecutionResult(
                success=False,
                message=error_message
            )

    def _escape_path(self, path: str) -> str:
        """
        Escapes the workspace path to prevent shell injection.

        Args:
            path (str): The workspace root path.

        Returns:
            str: The escaped path.
        """
        # Corrected the escaping to ensure proper syntax
        escaped_path = path.replace('"', '\\"')
        return f'"{escaped_path}"'