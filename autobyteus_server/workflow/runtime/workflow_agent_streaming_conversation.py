import asyncio
import logging
import uuid
from queue import Queue, Empty
from typing import Optional, List
from autobyteus.conversation.user_message import UserMessage
from autobyteus.llm.base_llm import BaseLLM
from autobyteus.llm.utils.token_usage import TokenUsage
from autobyteus.events.event_emitter import EventEmitter
from autobyteus.events.event_types import EventType
from autobyteus_server.agent_runtime.exceptions import StreamClosedError
from autobyteus_server.workflow.persistence.conversation.provider.persistence_proxy import PersistenceProxy as ConversationPersistenceProxy
from autobyteus_server.token_usage.provider.persistence_proxy import PersistenceProxy as TokenUsagePersistenceProxy
from autobyteus_server.agent_runtime.base_agent_streaming_conversation import BaseAgentStreamingConversation
from autobyteus_server.agent_runtime.agent_response import AgentResponseData

logger = logging.getLogger(__name__)

class WorkflowAgentStreamingConversation(BaseAgentStreamingConversation):
    """
    A streaming conversation for workflow steps that manages its own agent and message flow.
    Extends the BaseAgentStreamingConversation with workflow-specific persistence and token usage.
    """
    def __init__(self,
                 workspace_id: str,
                 step_id: str,
                 step_name: str,
                 llm: BaseLLM,
                 initial_message: UserMessage,
                 tools: List = None):
        super().__init__(llm)
        self.workspace_id = workspace_id
        self.step_id = step_id
        self.step_name = step_name
        self.persistence_proxy = ConversationPersistenceProxy()
        self.token_usage_proxy = TokenUsagePersistenceProxy()

        # Store the initial message and generate conversation_id
        new_conversation = self.persistence_proxy.store_message(
            step_name=self.step_name,
            role='user',
            message=initial_message.content,
            original_message=initial_message.original_requirement,
            context_paths=initial_message.context_file_paths
        )
        self.conversation_id = new_conversation.step_conversation_id

        # Initialize agent
        self._agent = self._initialize_agent(llm, initial_message)
        self.subscribe_from(self._agent, EventType.ASSISTANT_RESPONSE, self._on_assistant_response)

    def _initialize_agent(self, llm: BaseLLM, initial_message: UserMessage):
        from autobyteus.agent.async_agent import AsyncAgent  # local import to avoid circular dependencies
        agent_id = self._generate_agent_id(self.step_name)
        return AsyncAgent(
            role=self.step_name,
            llm=llm,
            agent_id=agent_id,
            initial_user_message=initial_message
        )

    @staticmethod
    def _generate_agent_id(step_name: str) -> str:
        sanitized_name = step_name.lower().replace(' ', '_')
        unique_id = str(uuid.uuid4())
        return f"{sanitized_name}_{unique_id}"

    def _on_assistant_response(self, *args, **kwargs):
        try:
            response = kwargs.get('response')
            is_complete = kwargs.get('is_complete', False)

            if not response:
                return

            if is_complete:
                token_usage: TokenUsage = self._agent.llm.latest_token_usage
                llm_model = self._agent.llm.model.value
                
                self.token_usage_proxy.create_conversation_token_usage_records(
                    conversation_id=self.conversation_id,
                    conversation_type='WORKFLOW',
                    token_usage=token_usage,
                    llm_model=llm_model
                )
                
                self.persistence_proxy.update_last_user_message_usage(
                    self.conversation_id,
                    token_count=token_usage.prompt_tokens,
                    cost=token_usage.prompt_cost or 0.0
                )
                
                self.persistence_proxy.store_message(
                    step_name=self.step_name,
                    role='assistant',
                    message=response,
                    token_count=token_usage.completion_tokens,
                    cost=token_usage.completion_cost or 0.0,
                    conversation_id=self.conversation_id
                )
                
                response_data = AgentResponseData(
                    message="",
                    is_complete=True,
                    prompt_tokens=token_usage.prompt_tokens,
                    completion_tokens=token_usage.completion_tokens,
                    total_tokens=token_usage.total_tokens,
                    prompt_cost=token_usage.prompt_cost,
                    completion_cost=token_usage.completion_cost,
                    total_cost=token_usage.total_cost
                )
                
                logger.debug(f"Saved complete response with token usage for conversation {self.conversation_id} using model {llm_model}")
            else:
                response_data = AgentResponseData(
                    message=response,
                    is_complete=False
                )
            
            self.put_response(response_data)

        except Exception as e:
            logger.error(f"Error in _on_assistant_response: {str(e)}")
            response_data = AgentResponseData(
                message=str(e),
                is_complete=True
            )
            self.put_response(response_data)

    async def send_message(self, message: UserMessage) -> None:
        if not self.is_active:
            raise StreamClosedError("Cannot send message to inactive conversation")

        self.persistence_proxy.store_message(
            step_name=self.step_name,
            role='user',
            message=message.content,
            original_message=message.original_requirement,
            context_paths=message.context_file_paths,
            conversation_id=self.conversation_id
        )

        await self._agent.receive_user_message(message)
