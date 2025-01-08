
import logging
from typing import List, Optional
from autobyteus.conversation.user_message import UserMessage
from autobyteus.llm.llm_factory import LLMFactory
from autobyteus_server.agent_runtime.base_agent_conversation_manager import BaseAgentConversationManager
from autobyteus_server.workflow.runtime.workflow_agent_streaming_conversation import WorkflowAgentStreamingConversation

logger = logging.getLogger(__name__)

class WorkflowAgentConversationManager(BaseAgentConversationManager):
    """
    Manages agent conversations for workflow steps.
    Extends the BaseAgentConversationManager with workflow-specific conversation creation.
    """

    def create_conversation(
        self,
        step_name: str,
        workspace_id: str,
        step_id: str,
        llm_model: str,
        initial_message: UserMessage,
        tools: List = None
    ) -> WorkflowAgentStreamingConversation:
        """
        Creates a new workflow agent conversation.
        """
        llm = LLMFactory.create_llm(llm_model)

        conversation = WorkflowAgentStreamingConversation(
            workspace_id=workspace_id,
            step_id=step_id,
            step_name=step_name,
            llm=llm,
            initial_message=initial_message,
            tools=tools
        )

        _ = self._runtime.execute_coroutine(conversation.start())
        self._conversations[conversation.conversation_id] = conversation
        return conversation
