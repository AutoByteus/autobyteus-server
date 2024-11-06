from datetime import datetime
from typing import Any, List, Optional

from bson import ObjectId
import logging  # Added for logging
from autobyteus_server.workflow.persistence.conversation.persistence.provider import PersistenceProvider
from autobyteus_server.workflow.persistence.conversation.repositories.mongodb.step_conversation_repository import ConversationNotFoundError, StepConversationRepository
from autobyteus_server.workflow.persistence.conversation.converters.mongodb_converter import MongoDBConverter
from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation, ConversationHistory
from autobyteus.utils.singleton import SingletonMeta

# Initialize logger
logger = logging.getLogger(__name__)

class MongoPersistenceProvider(PersistenceProvider):
    def __init__(self):
        super().__init__()
        self.conversation_repository = StepConversationRepository()
        self.converter = MongoDBConverter()
        self.current_conversations = {}  # Stores domain models instead of MongoDB models

    def create_conversation(self, step_name: str) -> StepConversation:
        """Create a new empty conversation."""
        try:
            mongo_conversation = self.conversation_repository.create_conversation(step_name)
            domain_conversation = self.converter.to_domain_conversation(mongo_conversation, [])
            step_conversation_id = domain_conversation.step_conversation_id
            self.current_conversations[step_conversation_id] = domain_conversation
            logger.info(f"Created new conversation with ID: {step_conversation_id}")
            return domain_conversation
        except Exception as e:
            logger.error(f"Failed to create conversation for step '{step_name}': {str(e)}")
            raise

    def store_message(
        self, 
        step_name: str, 
        role: str, 
        message: str, 
        original_message: Optional[str] = None,  # Use original_message in domain model
        context_paths: Optional[List[str]] = None,
        step_conversation_id: Optional[str] = None  # Updated parameter name
    ) -> StepConversation:
        """Store a message and return the updated conversation."""
        try:
            if step_conversation_id:
                # Check if conversation is already cached
                domain_conv = self.current_conversations.get(step_conversation_id)
                if not domain_conv:
                    try:
                        conversation_object_id = ObjectId(step_conversation_id)
                    except Exception as e:
                        logger.error(f"Invalid step_conversation_id format: {step_conversation_id}. Error: {str(e)}")
                        raise ValueError(f"Invalid step_conversation_id format: {step_conversation_id}")

                    mongo_conv = self.conversation_repository.get_conversation_by_id(conversation_object_id)
                    if not mongo_conv:
                        logger.error(f"Conversation with ID {step_conversation_id} not found in the database.")
                        raise ConversationNotFoundError(f"Conversation with ID {step_conversation_id} not found")
                    domain_conv = self.converter.to_domain_conversation(mongo_conv, mongo_conv.messages)
                    self.current_conversations[step_conversation_id] = domain_conv
                    logger.info(f"Loaded existing conversation with ID: {step_conversation_id}")
            else:
                # Create a new conversation
                domain_conv = self.create_conversation(step_name)
                step_conversation_id = domain_conv.step_conversation_id

            # Add message to the domain model
            domain_conv.messages.append(
                Message(
                    role=role,
                    message=message,
                    timestamp=datetime.utcnow(),
                    original_message=original_message,
                    context_paths=context_paths or []
                )
            )

            # Persist the updated conversation to the database
            mongo_conv = self.converter.to_mongo_conversation(domain_conv)
            self.conversation_repository.add_message(
                conversation_id=ObjectId(step_conversation_id),
                role=role,
                message=message,
                original_message=original_message,
                context_paths=context_paths
            )

            logger.info(f"Added message to conversation ID: {step_conversation_id}")

            # Update the cache with the updated domain model
            self.current_conversations[step_conversation_id] = domain_conv

            return domain_conv
        except ConversationNotFoundError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Failed to store message in conversation '{step_conversation_id}': {str(e)}")
            raise

    def get_conversation_history(self, step_name: str, page: int = 1, page_size: int = 10) -> ConversationHistory:
        """
        Retrieve paginated conversations by step name.
        """
        try:
            result = self.conversation_repository.get_conversations_by_step_name(step_name, page, page_size)
            
            conversations = []
            for mongo_conv in result["conversations"]:
                domain_conv = self.converter.to_domain_conversation(mongo_conv, mongo_conv.messages)
                conversations.append(domain_conv)
                # Cache the conversation
                self.current_conversations[domain_conv.step_conversation_id] = domain_conv
            
            logger.info(f"Retrieved conversation history for step '{step_name}': Page {page} of {result['total_pages']}")
            
            return ConversationHistory(
                conversations=conversations,
                total_conversations=result["total_conversations"],
                total_pages=result["total_pages"],
                current_page=result["current_page"]
            )
        except Exception as e:
            logger.error(f"Error retrieving conversation history for step '{step_name}': {str(e)}")
            raise