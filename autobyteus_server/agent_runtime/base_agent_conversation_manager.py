
import logging
from typing import Dict, Optional
from autobyteus.utils.singleton import SingletonMeta
from autobyteus.llm.llm_factory import LLMFactory

from autobyteus_server.agent_runtime.agent_runtime import AgentRuntime
from autobyteus_server.agent_runtime.base_agent_streaming_conversation import BaseAgentStreamingConversation


logger = logging.getLogger(__name__)

class BaseAgentConversationManager(metaclass=SingletonMeta):
    """
    Base manager for agent conversations.
    Provides generic management of conversations and runtime environment.
    Specific implementations should extend this class.
    """
    def __init__(self):
        self._conversations: Dict[str, BaseAgentStreamingConversation] = {}
        self._runtime = AgentRuntime()

    def send_message(self, conversation_id: str, message) -> None:
        """
        Sends a message to the specified conversation.
        Expects subclass to manage conversation type specifics.
        """
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            raise RuntimeError(f"No conversation found with ID: {conversation_id}")

        # Execute send_message in runtime's event loop
        self._runtime.execute_coroutine(conversation.send_message(message))

    def get_conversation(self, conversation_id: str) -> Optional[BaseAgentStreamingConversation]:
        """
        Retrieves a conversation by ID.
        """
        return self._conversations.get(conversation_id)

    def close_conversation(self, conversation_id: str) -> None:
        """
        Closes a conversation and cleans up its resources.
        """
        if conversation := self._conversations.pop(conversation_id, None):
            try:
                # Stop the conversation using runtime's event loop
                self._runtime.execute_coroutine(conversation.stop()).result()
            except Exception as e:
                logger.error(f"Error stopping conversation {conversation_id}: {str(e)}")

    def shutdown(self) -> None:
        """
        Shuts down all conversations and the runtime environment.
        """
        for conversation_id in list(self._conversations.keys()):
            self.close_conversation(conversation_id)
        self._runtime.shutdown()
