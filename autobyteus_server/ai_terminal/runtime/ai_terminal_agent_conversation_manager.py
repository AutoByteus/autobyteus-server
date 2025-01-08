
import logging
from typing import List, Optional
from autobyteus.conversation.user_message import UserMessage
from autobyteus.llm.llm_factory import LLMFactory
from autobyteus_server.agent_runtime.base_agent_conversation_manager import BaseAgentConversationManager
from autobyteus_server.ai_terminal.runtime.ai_terminal_agent_streaming_conversation import AITerminalAgentStreamingConversation

logger = logging.getLogger(__name__)

class AITerminalAgentConversationManager(BaseAgentConversationManager):
    """
    Manages agent conversations for AI Terminal.
    Extends the BaseAgentConversationManager with AI Terminal-specific conversation creation.
    """

    def create_conversation(
        self,
        workspace_id: str,
        llm_model: str,
        initial_message: UserMessage,
        tools: List = None
    ) -> AITerminalAgentStreamingConversation:
        """
        Creates a new AI Terminal agent conversation.
        
        Args:
            workspace_id (str): ID of the workspace
            llm_model (str): Name of the LLM model to use
            initial_message (UserMessage): Initial user message
            tools (List, optional): List of available tools
            
        Returns:
            AITerminalAgentStreamingConversation: New conversation instance
        """
        llm = LLMFactory.create_llm(llm_model)

        conversation = AITerminalAgentStreamingConversation(
            workspace_id=workspace_id,
            llm=llm,
            initial_message=initial_message,
            tools=tools
        )

        _ = self._runtime.execute_coroutine(conversation.start())
        self._conversations[conversation.conversation_id] = conversation
        return conversation
