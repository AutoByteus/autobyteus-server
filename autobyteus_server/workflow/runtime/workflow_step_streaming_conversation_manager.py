import logging
from typing import Dict, Optional, List
from autobyteus.utils.singleton import SingletonMeta
from autobyteus.conversation.user_message import UserMessage
from autobyteus.llm.base_llm import BaseLLM
from autobyteus.llm.llm_factory import LLMFactory
from autobyteus_server.workflow.runtime.streaming_conversation import StreamingConversation
from autobyteus_server.workflow.runtime.agent_runtime import AgentRuntime

logger = logging.getLogger(__name__)

class WorkflowStepStreamingConversationManager(metaclass=SingletonMeta):
    """
    Manages multiple streaming conversations for workflow steps.
    Handles the lifecycle of step-specific conversations and ensures proper resource management.
    """
    
    def __init__(self):
        self._conversations: Dict[str, StreamingConversation] = {}
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
    ) -> StreamingConversation:
        """
        Creates a new streaming conversation.
        """
        try:
            if conversation_id in self._conversations:
                raise RuntimeError(f"Conversation with ID {conversation_id} already exists")
                
            llm = LLMFactory.create_llm(llm_model)
            
            conversation = StreamingConversation(
                conversation_id=conversation_id,
                step_name=step_name,
                workspace_id=workspace_id,
                step_id=step_id,
                llm=llm,
                initial_message=initial_message,
                tools=tools
            )
            
            # Start conversation using runtime's event loop
            self._runtime.execute_coroutine(conversation.start()).result()
            
            self._conversations[conversation_id] = conversation
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to create conversation with ID {conversation_id}: {str(e)}")
            raise RuntimeError(f"Failed to create conversation: {str(e)}")

    async def send_message(self, conversation_id: str, message: str) -> None:
        """Sends a message to the specified conversation."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            raise RuntimeError(f"No conversation found with ID: {conversation_id}")
            
        # Execute send_message in runtime's event loop
        future = self._runtime.execute_coroutine(conversation.send_message(message))
        await future

    def get_conversation(self, conversation_id: str) -> Optional[StreamingConversation]:
        """Retrieves a conversation by ID."""
        return self._conversations.get(conversation_id)

    def close_conversation(self, conversation_id: str) -> None:
        """Closes a conversation and cleans up its resources."""
        if conversation := self._conversations.pop(conversation_id, None):
            try:
                # Stop the conversation using runtime's event loop
                self._runtime.execute_coroutine(conversation.stop()).result()
            except Exception as e:
                logger.error(f"Error stopping conversation {conversation_id}: {str(e)}")

    def shutdown(self) -> None:
        """Shuts down all conversations."""
        for conversation_id in list(self._conversations.keys()):
            self.close_conversation(conversation_id)
        self._runtime.shutdown()