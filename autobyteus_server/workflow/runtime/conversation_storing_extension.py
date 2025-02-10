import logging
from typing import Optional, List

from autobyteus.llm.extensions.base_extension import LLMExtension
from autobyteus.llm.utils.response_types import CompleteResponse
from autobyteus.llm.base_llm import BaseLLM
from autobyteus.llm.utils.messages import Message

from autobyteus_server.workflow.persistence.conversation.provider.persistence_proxy import PersistenceProxy as ConversationPersistenceProxy
from autobyteus_server.token_usage.provider.persistence_proxy import PersistenceProxy as TokenUsagePersistenceProxy

logger = logging.getLogger(__name__)

class ConversationStoringExtension(LLMExtension):
    """
    Extension to store conversation messages and token usage after LLM invocation.
    
    This extension is implemented in the autobyteus-server (business layer) and is
    responsible for handling persistence using business-specific proxies.
    """

    def __init__(
        self,
        llm: BaseLLM,
        conversation_id: str,
        step_name: str,
        token_usage_proxy: TokenUsagePersistenceProxy,
        persistence_proxy: ConversationPersistenceProxy
    ) -> None:
        """
        Initialize the ConversationStoringExtension with conversation-specific parameters.

        Args:
            llm (BaseLLM): The LLM instance.
            conversation_id (str): Unique identifier for the conversation.
            step_name (str): The name of the workflow step.
            token_usage_proxy (TokenUsagePersistenceProxy): Business proxy for token usage persistence.
            persistence_proxy (ConversationPersistenceProxy): Business proxy for storing conversation messages.
        """
        super().__init__(llm)
        self.conversation_id: str = conversation_id
        self.step_name: str = step_name
        self.token_usage_proxy: TokenUsagePersistenceProxy = token_usage_proxy
        self.persistence_proxy: ConversationPersistenceProxy = persistence_proxy

    async def before_invoke(
        self,
        user_message: str,
        file_paths: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        # No pre-invocation action required for storing logic.
        pass

    async def after_invoke(
        self,
        user_message: str,
        file_paths: Optional[List[str]] = None,
        response: Optional[CompleteResponse] = None,
        **kwargs
    ) -> None:
        """
        After invocation hook to store conversation data if a complete response is received.

        Args:
            user_message (str): The original user message.
            file_paths (Optional[List[str]]): List of file paths provided as context.
            response (Optional[CompleteResponse]): The complete LLM response.
        """
        try:
            if response is None:
                logger.debug("No response received; skipping storing logic.")
                return

            token_usage = self.llm.latest_token_usage
            if token_usage is None:
                logger.debug("Token usage is not available; skipping storing logic.")
                return

            llm_model = self.llm.model.value

            # Create conversation token usage records.
            self.token_usage_proxy.create_conversation_token_usage_records(
                conversation_id=self.conversation_id,
                conversation_type='WORKFLOW',
                token_usage=token_usage,
                llm_model=llm_model
            )
            
            # Update last user message usage.
            self.persistence_proxy.update_last_user_message_usage(
                self.conversation_id,
                token_count=token_usage.prompt_tokens,
                cost=token_usage.prompt_cost or 0.0
            )
            
            # Store assistant's response message.
            self.persistence_proxy.store_message(
                step_name=self.step_name,
                role='assistant',
                message=response.content,
                token_count=token_usage.completion_tokens,
                cost=token_usage.completion_cost or 0.0,
                conversation_id=self.conversation_id
            )

            logger.info(f"Stored conversation data for conversation {self.conversation_id}")

        except Exception as e:
            logger.error(f"Error in ConversationStoringExtension.after_invoke: {e}")

    def on_user_message_added(self, message: Message) -> None:
        # No action required when a user message is added.
        pass

    def on_assistant_message_added(self, message: Message) -> None:
        # No action required when an assistant message is added.
        pass

    async def cleanup(self) -> None:
        # No cleanup actions necessary for this extension.
        pass