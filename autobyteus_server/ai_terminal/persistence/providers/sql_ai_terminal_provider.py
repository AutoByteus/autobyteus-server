
from typing import List, Optional
import logging
from autobyteus_server.ai_terminal.persistence.providers.ai_terminal_persistence_provider import AiTerminalPersistenceProvider
from autobyteus_server.ai_terminal.persistence.repositories.sql.ai_terminal_conversation_repository import AiTerminalConversationRepository
from autobyteus_server.ai_terminal.persistence.repositories.sql.ai_terminal_conversation_message_repository import AiTerminalConversationMessageRepository
from autobyteus_server.ai_terminal.persistence.domain.models import AiTerminalConversation, ConversationHistory
from autobyteus_server.ai_terminal.persistence.converters.sql_converter import SQLConverter

logger = logging.getLogger(__name__)

class SqlAiTerminalProvider(AiTerminalPersistenceProvider):
    """
    SQL-based provider for AI Terminal conversations.
    Manages domain-level logic, while relying on repositories for data access.
    """

    def __init__(self):
        super().__init__()
        self.conversation_repository = AiTerminalConversationRepository()
        self.message_repository = AiTerminalConversationMessageRepository()
        self.converter = SQLConverter()
        self.current_conversations = {}  # Cache for active conversations

    def create_conversation(self) -> AiTerminalConversation:
        """Create a new empty conversation."""
        try:
            sql_conversation = self.conversation_repository.create_conversation()
            self.current_conversations[sql_conversation.conversation_id] = sql_conversation
            return self.converter.to_domain_conversation(sql_conversation, [])
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise

    def store_message(
        self, 
        conversation_id: str, 
        role: str, 
        message: str,
        token_count: Optional[int] = None,
        cost: Optional[float] = None
    ) -> AiTerminalConversation:
        """Store a message and return the updated conversation."""
        try:
            # Get or retrieve conversation
            sql_conv = self.current_conversations.get(conversation_id)
            if not sql_conv:
                sql_conv = self.conversation_repository.find_by_conversation_id(conversation_id)
                if not sql_conv:
                    logger.error(f"Conversation with ID {conversation_id} does not exist.")
                    raise ValueError(f"Conversation with ID {conversation_id} does not exist.")
                self.current_conversations[conversation_id] = sql_conv

            # Create message
            self.message_repository.create_message(
                conversation_id=sql_conv.id,
                role=role,
                message=message,
                token_count=token_count,
                cost=cost
            )

            # Retrieve updated messages
            messages = self.message_repository.get_messages_by_conversation_id(sql_conv.id)
            
            # Convert to domain model
            return self.converter.to_domain_conversation(sql_conv, messages)
        except Exception as e:
            logger.error(f"Failed to store message in conversation '{conversation_id}': {str(e)}")
            raise

    def get_conversation_history(self, page: int = 1, page_size: int = 10) -> ConversationHistory:
        """Retrieve paginated conversation history."""
        try:
            result = self.conversation_repository.list_conversations(skip=(page - 1) * page_size, limit=page_size)
            
            # Build messages dictionary for efficient conversion
            messages_by_conversation = {}
            for conv in result["conversations"]:
                messages = self.message_repository.get_messages_by_conversation_id(conv.id)
                messages_by_conversation[conv.id] = messages
            
            return self.converter.to_conversation_history(
                result["conversations"],
                messages_by_conversation,
                result["total"],
                result["total_pages"],
                result["current_page"]
            )
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            raise
