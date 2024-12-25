
import logging
from typing import Dict, Optional, List
from autobyteus.utils.singleton import SingletonMeta
from autobyteus.conversation.user_message import UserMessage
from autobyteus.llm.base_llm import BaseLLM
from autobyteus.llm.llm_factory import LLMFactory
from autobyteus_server.workflow.runtime.agent_streaming_conversation import AgentStreamingConversation
from autobyteus_server.workflow.runtime.agent_runtime import AgentRuntime

logger = logging.getLogger(__name__)

class StepAgentConversationManager(metaclass=SingletonMeta):
    """
    Manages agent conversations for workflow steps.
    Handles the lifecycle of step-specific agent conversations and ensures proper resource management.
    """

    def __init__(self):
        self._conversations: Dict[str, AgentStreamingConversation] = {}
        self._runtime = AgentRuntime()

    def create_conversation(
        self,
        conversation_id: str,
        step_name: str,
        workspace_id: str,
        step_id: str,
        llm_model: str,
        initial_message: UserMessage,
        tools: List = None
    ) -> AgentStreamingConversation:
        """
        Creates a new agent conversation.

        Args:
            conversation_id: Unique identifier for the conversation
            step_name: Name of the workflow step
            workspace_id: ID of the workspace
            step_id: ID of the step
            llm_model: Name of the LLM model to use
            initial_message: Initial message to start the conversation
            tools: Optional list of tools available to the agent

        Returns:
            AgentStreamingConversation: The created conversation instance

        Raises:
            RuntimeError: If conversation with given ID already exists
        """
        if conversation_id in self._conversations:
            raise RuntimeError(f"Conversation with ID {conversation_id} already exists")

        llm = LLMFactory.create_llm(llm_model)

        conversation = AgentStreamingConversation(
            conversation_id=conversation_id,
            step_name=step_name,
            workspace_id=workspace_id,
            step_id=step_id,
            llm=llm,
            initial_message=initial_message,
            tools=tools
        )

        # Start the conversation in the runtime's event loop
        _ = self._runtime.execute_coroutine(conversation.start())

        self._conversations[conversation_id] = conversation
        return conversation

    def send_message(self, conversation_id: str, message: UserMessage) -> None:
        """
        Sends a message to the specified conversation.

        Args:
            conversation_id: ID of the target conversation
            message: UserMessage object to send

        Raises:
            RuntimeError: If no conversation found with given ID
        """
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            raise RuntimeError(f"No conversation found with ID: {conversation_id}")

        # Execute send_message in runtime's event loop
        self._runtime.execute_coroutine(conversation.send_message(message))

    def get_conversation(self, conversation_id: str) -> Optional[AgentStreamingConversation]:
        """
        Retrieves a conversation by ID.

        Args:
            conversation_id: ID of the conversation to retrieve

        Returns:
            Optional[AgentStreamingConversation]: The conversation if found, None otherwise
        """
        return self._conversations.get(conversation_id)

    def close_conversation(self, conversation_id: str) -> None:
        """
        Closes a conversation and cleans up its resources.

        Args:
            conversation_id: ID of the conversation to close
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
