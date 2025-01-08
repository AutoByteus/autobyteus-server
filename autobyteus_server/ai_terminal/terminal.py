"""
Module for handling persistent terminal operations within a workspace context, maintaining state across commands.
"""

import asyncio
from dataclasses import dataclass
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CommandExecutionResult:
    """Results from command execution."""
    success: bool
    message: str


class Terminal:
    """
    Handles persistent terminal operations within a specific workspace context, maintaining state across commands.
    """
    def __init__(self, workspace_root_path: str):
        """
        Initialize the Terminal with a persistent bash subprocess.

        Args:
            workspace_root_path (str): The root path where commands will be executed.
        """
        self.workspace_root_path = os.path.abspath(workspace_root_path)
        self.process: Optional[asyncio.subprocess.Process] = None
        self.loop = asyncio.get_event_loop()
        self.stdout_buffer = asyncio.Queue()
        self.stderr_buffer = asyncio.Queue()
        self._initialize_terminal()

    def _initialize_terminal(self):
        """
        Initializes the persistent bash subprocess.
        """
        logger.debug(f"Initializing terminal in root path: {self.workspace_root_path}")
        self.process = self.loop.run_until_complete(
            asyncio.create_subprocess_shell(
                "/bin/bash",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace_root_path
            )
        )
        self.loop.create_task(self._read_stdout())
        self.loop.create_task(self._read_stderr())

    async def _read_stdout(self):
        """
        Asynchronously reads from the subprocess's stdout and stores the output.
        """
        assert self.process is not None
        while True:
            line = await self.process.stdout.readline()
            if line:
                decoded_line = line.decode('utf-8')
                await self.stdout_buffer.put(decoded_line)
                logger.debug(f"STDOUT: {decoded_line.strip()}")
            else:
                break

    async def _read_stderr(self):
        """
        Asynchronously reads from the subprocess's stderr and stores the error output.
        """
        assert self.process is not None
        while True:
            line = await self.process.stderr.readline()
            if line:
                decoded_line = line.decode('utf-8')
                await self.stderr_buffer.put(decoded_line)
                logger.debug(f"STDERR: {decoded_line.strip()}")
            else:
                break

    async def execute_command(self, command: str) -> CommandExecutionResult:
        """
        Execute a command in the persistent terminal context.

        Args:
            command (str): The command to execute.

        Returns:
            CommandExecutionResult: The result of the command execution.
        """
        if self.process is None:
            error_message = "Terminal process is not initialized."
            logger.error(error_message)
            return CommandExecutionResult(success=False, message=error_message)

        logger.debug(f"Sending command to terminal: {command}")
        try:
            # Send the command followed by a newline to the bash subprocess
            self.process.stdin.write(f"{command}\n".encode('utf-8'))
            await self.process.stdin.drain()

            # Collect the output until the next prompt
            output = ""
            while True:
                line = await self.stdout_buffer.get()
                if line.strip().endswith("$"):
                    break
                output += line

            success_message = output.strip()
            logger.info(f"Command executed successfully: {command}")
            return CommandExecutionResult(success=True, message=success_message)
        except Exception as e:
            error_message = f"An error occurred while executing the command: {str(e)}"
            logger.exception(error_message)
            return CommandExecutionResult(success=False, message=error_message)

    def close(self):
        """
        Closes the terminal subprocess gracefully.
        """
        if self.process and self.process.returncode is None:
            logger.debug("Terminating terminal subprocess.")
            self.process.terminate()
            try:
                self.loop.run_until_complete(self.process.wait())
                logger.info("Terminal subprocess terminated.")
            except Exception as e:
                logger.error(f"Error terminating terminal subprocess: {str(e)}")
