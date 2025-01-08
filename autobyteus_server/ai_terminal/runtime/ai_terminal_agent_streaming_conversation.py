
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
from autobyteus_server.ai_terminal.persistence.providers.ai_terminal_persistence_proxy import AiTerminalPersistenceProxy
from autobyteus_server.token_usage.provider.persistence_proxy import PersistenceProxy as TokenUsagePersistenceProxy
from autobyteus_server.agent_runtime.base_agent_streaming_conversation import BaseAgentStreamingConversation
from autobyteus_server.agent_runtime.agent_response import AgentResponseData

logger = logging.getLogger(__name__)

class AITerminalAgentStreamingConversation(BaseAgentStreamingConversation):
    """
    A streaming conversation for AI Terminal that manages its own agent and message flow.
    Extends the BaseAgentStreamingConversation with AI Terminal-specific persistence and token usage.
    """
    def __init__(self,
                 workspace_id: str,
                 llm: BaseLLM,
                 initial_message: UserMessage,
                 tools: List = None):
        super().__init__(llm)
        self.workspace_id = workspace_id
        self.persistence_proxy = AiTerminalPersistenceProxy()
        self.token_usage_proxy = TokenUsagePersistenceProxy()

        # Create new conversation and store initial message
        new_conversation = self.persistence_proxy.create_conversation()
        self.conversation_id = new_conversation.conversation_id
        
        self.persistence_proxy.store_message(
            conversation_id=self.conversation_id,
            role='user',
            message=initial_message.content
        )

        # Initialize agent
        self._agent = self._initialize_agent(llm, initial_message)
        self.subscribe_from(self._agent, EventType.ASSISTANT_RESPONSE, self._on_assistant_response)

    def _initialize_agent(self, llm: BaseLLM, initial_message: UserMessage):
        from autobyteus.agent.async_agent import AsyncAgent
        agent_id = f"ai_terminal_{str(uuid.uuid4())}"
        return AsyncAgent(
            role="ai_terminal",
            llm=llm,
            agent_id=agent_id,
            initial_user_message=initial_message
        )

    def _on_assistant_response(self, *args, **kwargs):
        try:
            response = kwargs.get('response')
            is_complete = kwargs.get('is_complete', False)

            if not response:
                return

            if is_complete:
                token_usage: TokenUsage = self._agent.llm.latest_token_usage
                
                self.token_usage_proxy.create_conversation_token_usage_records(
                    conversation_id=self.conversation_id,
                    conversation_type='AI_TERMINAL',
                    token_usage=token_usage
                )
                
                self.persistence_proxy.store_message(
                    conversation_id=self.conversation_id,
                    role='assistant',
                    message=response,
                    token_count=token_usage.completion_tokens,
                    cost=token_usage.completion_cost or 0.0
                )
                
                response_data = AgentResponseData(
                    message=None,
                    is_complete=True,
                    prompt_tokens=token_usage.prompt_tokens,
                    completion_tokens=token_usage.completion_tokens,
                    total_tokens=token_usage.total_tokens,
                    prompt_cost=token_usage.prompt_cost,
                    completion_cost=token_usage.completion_cost,
                    total_cost=token_usage.total_cost
                )
                
                logger.debug(f"Saved complete response with token usage for conversation {self.conversation_id}")
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
                is_complete=True,
                error=True
            )
            self.put_response(response_data)

    async def send_message(self, message: UserMessage) -> None:
        """
        Send a new message to the conversation.
        
        Args:
            message (UserMessage): The message to send
        """
        if not self.is_active:
            raise StreamClosedError("Cannot send message to inactive conversation")

        self.persistence_proxy.store_message(
            conversation_id=self.conversation_id,
            role='user',
            message=message.content
        )

        await self._agent.receive_user_message(message)
