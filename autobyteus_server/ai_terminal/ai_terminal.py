
"""
Module for handling the standalone AI Terminal functionality, managing a persistent bash subprocess
and interpreting natural language commands using an AI agent.
"""

import asyncio
from dataclasses import dataclass
import logging
import os
from typing import Optional

from autobyteus_server.ai_terminal.terminal import CommandExecutionResult, Terminal
from autobyteus_server.ai_terminal.runtime.ai_terminal_agent_conversation_manager import AITerminalAgentConversationManager
from autobyteus.conversation.user_message import UserMessage

logger = logging.getLogger(__name__)

class AITerminal:
    """
    Standalone AI Terminal that maintains a persistent bash subprocess and interacts with an AI agent
    to interpret natural language commands into bash commands.
    """
    DEFAULT_LLM_MODEL = "OLLAMA_LLAMA_3_2"
    
    def __init__(self, workspace: 'Workspace', llm_model: Optional[str] = None):
        """
        Initialize the AITerminal with a persistent bash subprocess and agent runtime.
        
        Args:
            workspace (Workspace): The workspace instance to which this AI Terminal belongs.
            llm_model (Optional[str]): The LLM model to use for command interpretation. 
                                     Defaults to DEFAULT_LLM_MODEL if not specified.
        """
        self.workspace = workspace
        self.terminal = Terminal(self.workspace.root_path)
        self.conversation_manager = AITerminalAgentConversationManager()
        self._llm_model = llm_model or self.DEFAULT_LLM_MODEL
        logger.debug(f"AI Terminal initialized in workspace: {self.workspace.root_path} with model: {self._llm_model}")

    @property
    def llm_model(self) -> str:
        """Get the current LLM model configuration."""
        return self._llm_model

    def set_llm_model(self, model: str) -> None:
        """
        Set the LLM model to be used for command interpretation.
        
        Args:
            model (str): The name/identifier of the LLM model to use.
        """
        self._llm_model = model
        logger.info(f"AI Terminal LLM model set to: {model}")

    async def suggest_command(self, natural_input: str) -> str:
        """
        Suggest a bash command based on natural language input using an AI agent.
        
        Args:
            natural_input (str): The natural language input from the user.
        
        Returns:
            str: The conversation ID for streaming responses.
        """
        try:
            logger.debug(f"Processing natural language input: {natural_input} using model: {self._llm_model}")
            
            # Create a conversation with the AI Terminal agent
            conversation = self.conversation_manager.create_conversation(
                workspace_id=self.workspace.workspace_id,
                llm_model=self._llm_model,
                initial_message=UserMessage(content=natural_input)
            )
            
            return conversation.conversation_id
            
        except Exception as e:
            logger.exception("Failed to process natural language input.")
            raise

    async def execute_command(self, command: str) -> CommandExecutionResult:
        """
        Execute a bash command in the persistent terminal.
        
        Args:
            command (str): The bash command to execute.
        
        Returns:
            CommandExecutionResult: The result of the command execution.
        """
        return await self.terminal.execute_command(command)

    def close(self):
        """
        Gracefully close the AI Terminal and its subprocess.
        """
        self.terminal.close()
        self.conversation_manager.shutdown()
        logger.info("AI Terminal has been closed.")
