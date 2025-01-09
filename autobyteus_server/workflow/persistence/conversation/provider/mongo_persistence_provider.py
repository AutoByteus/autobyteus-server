
from datetime import datetime
from typing import Any, List, Optional

from bson import ObjectId
import logging
from autobyteus_server.workflow.persistence.conversation.provider.provider import PersistenceProvider
from autobyteus_server.workflow.persistence.conversation.repositories.mongodb.step_conversation_repository import (
    ConversationNotFoundError,
    StepConversationRepository
)
from autobyteus_server.workflow.persistence.conversation.converters.mongodb_converter import MongoDBConverter
from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation, ConversationHistory

logger = logging.getLogger(__name__)

class MongoPersistenceProvider(PersistenceProvider):
    def __init__(self):
        super().__init__()
        self.conversation_repository = StepConversationRepository()
        self.converter = MongoDBConverter()
        self.current_conversations = {}  # Stores domain models instead of MongoDB models

    def create_conversation(self, step_name: str, llm_model: Optional[str] = None) -> StepConversation:
        """Create a new empty conversation with optional llm_model."""
        try:
            mongo_conversation = self.conversation_repository.create_conversation(step_name, llm_model)
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
        token_count: Optional[int] = None,
        cost: Optional[float] = None,
        original_message: Optional[str] = None, 
        context_paths: Optional[List[str]] = None,
        step_conversation_id: Optional[str] = None
    ) -> StepConversation:
        """Store a message and return the updated conversation."""
        try:
            if token_count is not None and token_count < 0:
                raise ValueError("token_count cannot be negative")
            if cost is not None and cost < 0:
                raise ValueError("cost cannot be negative")

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
            new_message = Message(
                role=role,
                message=message,
                timestamp=datetime.utcnow(),
                original_message=original_message,
                context_paths=context_paths or [],
                token_count=token_count,
                cost=cost
            )
            domain_conv.messages.append(new_message)

            # Persist the updated conversation to the database
            mongo_conv = self.converter.to_mongo_conversation(domain_conv)
            self.conversation_repository.add_message(
                conversation_id=ObjectId(step_conversation_id),
                role=role,
                message=message,
                token_count=token_count,
                cost=cost,
                original_message=original_message,
                context_paths=context_paths
            )

            logger.info(f"Added message to conversation ID: {step_conversation_id}")
            if token_count is not None:
                logger.info(f"Token count: {token_count}")
            if cost is not None:
                logger.info(f"Cost: {cost}")

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

    def update_last_user_message_usage(
        self,
        step_conversation_id: str,
        token_count: int,
        cost: float
    ) -> StepConversation:
        """
        Update the token count and cost for the last user message in the conversation.
        """
        try:
            if token_count < 0:
                raise ValueError("token_count cannot be negative")
            if cost < 0:
                raise ValueError("cost cannot be negative")

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

            # Find the last user message
            last_user_message = None
            for msg in reversed(domain_conv.messages):
                if msg.role.lower() == "user":
                    last_user_message = msg
                    break

            if not last_user_message:
                logger.error("No user message found to update token usage.")
                raise ValueError("No user message found in the conversation to update token usage.")

            # Update token_count and cost
            last_user_message.token_count = token_count
            last_user_message.cost = cost

            # If the message has an underlying MongoDB _id, update it directly
            # Otherwise, we do a full conversation replace
            # If we want partial update, we can call the new repository method (update_token_usage) 
            # but we need the actual message_id from last_user_message.message_id.

            # If message_id is present (and stored as an ObjectId), we can attempt repository-level partial update
            message_id = last_user_message.message_id
            if message_id:
                try:
                    # Attempt partial update via the new repository method
                    conversation_object_id = ObjectId(step_conversation_id)
                    # We assume message_id is a valid ObjectId string
                    self.conversation_repository.update_token_usage(
                        conversation_id=conversation_object_id,
                        message_id=message_id,
                        token_count=token_count,
                        cost=cost
                    )
                except Exception as e:
                    logger.warning(
                        f"Partial update via repository failed or invalid message_id. "
                        f"Falling back to full conversation replace. Error: {e}"
                    )
                    updated_mongo_conv = self.converter.to_mongo_conversation(domain_conv)
                    self.conversation_repository.collection.replace_one(
                        {"_id": ObjectId(step_conversation_id)},
                        updated_mongo_conv.to_dict(),
                        session=self.conversation_repository.session
                    )
            else:
                # Fallback to full conversation replace if we can't do partial
                updated_mongo_conv = self.converter.to_mongo_conversation(domain_conv)
                self.conversation_repository.collection.replace_one(
                    {"_id": ObjectId(step_conversation_id)},
                    updated_mongo_conv.to_dict(),
                    session=self.conversation_repository.session
                )

            # Update cache
            self.current_conversations[step_conversation_id] = domain_conv
            logger.info(f"Updated token usage for the last user message in conversation {step_conversation_id}")
            return domain_conv
        except ConversationNotFoundError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Failed to update token usage for the last user message in conversation '{step_conversation_id}': {str(e)}")
            raise
