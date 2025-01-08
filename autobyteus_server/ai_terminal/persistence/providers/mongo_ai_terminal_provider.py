
import logging
from datetime import datetime
from typing import List, Optional
import uuid

from autobyteus_server.ai_terminal.persistence.providers.ai_terminal_persistence_provider import AiTerminalPersistenceProvider
from autobyteus_server.ai_terminal.persistence.domain.models import AiTerminalConversation, AiTerminalMessage, ConversationHistory
from autobyteus_server.ai_terminal.persistence.repositories.mongodb.ai_terminal_conversation_repository import (
    AiTerminalConversationRepository,
    ConversationNotFoundError
)
from autobyteus_server.ai_terminal.persistence.converters.mongodb_converter import MongoDBConverter

logger = logging.getLogger(__name__)

class MongoAiTerminalProvider(AiTerminalPersistenceProvider):
    """
    MongoDB-based provider for AI Terminal conversations.
    Orchestrates domain logic and uses the Mongo repository for data persistence.
    """

    def __init__(self):
        super().__init__()
        self.repo = AiTerminalConversationRepository()
        self.converter = MongoDBConverter()
        self.current_conversations = {}  # Cache for domain models

    def create_conversation(self) -> AiTerminalConversation:
        """Create a new conversation with a unique ID."""
        try:
            conversation_id = str(uuid.uuid4())
            mongo_conversation = self.repo.create_conversation(conversation_id)
            domain_conversation = self.converter.to_domain_conversation(mongo_conversation, [])
            self.current_conversations[conversation_id] = domain_conversation
            logger.info(f"Created new conversation with ID: {conversation_id}")
            return domain_conversation
        except Exception as e:
            logger.error(f"Failed to create conversation: {str(e)}")
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
            # Check if conversation is already cached
            domain_conv = self.current_conversations.get(conversation_id)
            if not domain_conv:
                mongo_conv = self.repo.find_by_conversation_id(conversation_id)
                if not mongo_conv:
                    logger.error(f"Conversation not found with ID: {conversation_id}")
                    raise ConversationNotFoundError(f"Conversation with ID {conversation_id} not found")
                domain_conv = self.converter.to_domain_conversation(mongo_conv, mongo_conv.messages)
                self.current_conversations[conversation_id] = domain_conv

            # Add message to the domain model
            new_message = AiTerminalMessage(
                role=role,
                message=message,
                timestamp=datetime.utcnow(),
                token_count=token_count,
                cost=cost
            )
            domain_conv.messages.append(new_message)

            # Update the database
            updated_conv = self.repo.add_message(
                conversation_id=conversation_id,
                role=role,
                message=message,
                token_count=token_count,
                cost=cost
            )
            
            if not updated_conv:
                raise ValueError(f"Failed to update conversation: {conversation_id}")

            # Update cache with the latest version
            domain_conv = self.converter.to_domain_conversation(updated_conv, updated_conv.messages)
            self.current_conversations[conversation_id] = domain_conv

            logger.info(f"Stored message in conversation: {conversation_id}")
            return domain_conv
        except ConversationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to store message: {str(e)}")
            raise

    def get_conversation_history(self, conversation_id: str) -> AiTerminalConversation:
        """Retrieve conversation history by ID."""
        try:
            # Check cache first
            if conversation_id in self.current_conversations:
                return self.current_conversations[conversation_id]

            mongo_conv = self.repo.find_by_conversation_id(conversation_id)
            if not mongo_conv:
                raise ConversationNotFoundError(f"Conversation not found: {conversation_id}")

            domain_conv = self.converter.to_domain_conversation(mongo_conv, mongo_conv.messages)
            self.current_conversations[conversation_id] = domain_conv
            
            logger.info(f"Retrieved conversation history: {conversation_id}")
            return domain_conv
        except ConversationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            raise

    def list_conversations(self, page: int = 1, page_size: int = 10) -> ConversationHistory:
        """List all conversations with pagination."""
        try:
            result = self.repo.list_conversations(
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            conversations = []
            for mongo_conv in result["conversations"]:
                domain_conv = self.converter.to_domain_conversation(mongo_conv, mongo_conv.messages)
                conversations.append(domain_conv)
                # Update cache
                self.current_conversations[domain_conv.conversation_id] = domain_conv
            
            return ConversationHistory(
                conversations=conversations,
                total_conversations=result["total_conversations"],
                total_pages=result["total_pages"],
                current_page=result["current_page"]
            )
        except Exception as e:
            logger.error(f"Failed to list conversations: {str(e)}")
            raise
