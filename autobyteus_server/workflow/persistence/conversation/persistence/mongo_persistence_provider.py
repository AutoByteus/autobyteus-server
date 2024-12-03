from datetime import datetime
from typing import Any, List, Optional
from bson import ObjectId
import logging
from autobyteus_server.workflow.persistence.conversation.persistence.provider import PersistenceProvider
from autobyteus_server.workflow.persistence.conversation.repositories.mongodb.step_conversation_repository import ConversationNotFoundError, StepConversationRepository
from autobyteus_server.workflow.persistence.conversation.repositories.mongodb.step_conversation_message_repository import StepConversationMessageRepository
from autobyteus_server.workflow.persistence.conversation.repositories.mongodb.cost_entry_repository import CostEntryRepository
from autobyteus_server.workflow.persistence.conversation.converters.mongodb_converter import MongoDBConverter
from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation, ConversationHistory

logger = logging.getLogger(__name__)

class MongoPersistenceProvider(PersistenceProvider):
    def __init__(self):
        super().__init__()
        self.conversation_repository = StepConversationRepository()
        self.message_repository = StepConversationMessageRepository()
        self.cost_entry_repository = CostEntryRepository()
        self.converter = MongoDBConverter()
        self.current_conversations = {}

    def create_conversation(self, step_name: str) -> StepConversation:
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
        original_message: Optional[str] = None,
        context_paths: Optional[List[str]] = None,
        conversation_id: Optional[str] = None,
        cost: float = 0.0
    ) -> StepConversation:
        try:
            if conversation_id:
                domain_conv = self.current_conversations.get(conversation_id)
                if not domain_conv:
                    conversation_object_id = ObjectId(conversation_id)
                    mongo_conv = self.conversation_repository.get_conversation_by_id(conversation_object_id)
                    if not mongo_conv:
                        logger.error(f"Conversation with ID {conversation_id} not found in the database.")
                        raise ConversationNotFoundError(f"Conversation with ID {conversation_id} not found")
                    domain_conv = self.converter.to_domain_conversation(mongo_conv, mongo_conv.messages)
                    self.current_conversations[conversation_id] = domain_conv
                    logger.info(f"Loaded existing conversation with ID: {conversation_id}")
            else:
                domain_conv = self.create_conversation(step_name)
                conversation_id = domain_conv.step_conversation_id

            # Add message to domain model
            new_message = Message(
                role=role,
                message=message,
                timestamp=datetime.utcnow(),
                original_message=original_message,
                context_paths=context_paths or [],
                cost=cost,
                message_id=str(ObjectId())
            )
            domain_conv.messages.append(new_message)

            # Persist the message to the database
            self.message_repository.create_message(
                conversation_id=ObjectId(conversation_id),
                role=role,
                message=message,
                original_message=original_message,
                context_paths=context_paths,
                cost=cost
            )

            # Update total cost
            total_cost = sum(msg.cost for msg in domain_conv.messages)
            self.conversation_repository.update_total_cost(ObjectId(conversation_id), total_cost)

            # Create a cost entry
            self.cost_entry_repository.create_cost_entry(
                role=role,
                step_name=step_name,
                cost=cost,
                timestamp=datetime.utcnow(),
                conversation_id=conversation_id,
                message_id=new_message.message_id
            )

            logger.info(f"Added message to conversation ID: {conversation_id}")

            self.current_conversations[conversation_id] = domain_conv

            return domain_conv
        except ConversationNotFoundError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Failed to store message in conversation '{conversation_id}': {str(e)}")
            raise

    def get_conversation_history(self, step_name: str, page: int = 1, page_size: int = 10) -> ConversationHistory:
        try:
            result = self.conversation_repository.get_conversations_by_step_name(step_name, page, page_size)
            
            conversations = []
            for mongo_conv in result["conversations"]:
                messages = self.message_repository.get_messages_by_conversation_id(mongo_conv._id)
                domain_conv = self.converter.to_domain_conversation(mongo_conv, messages)
                conversations.append(domain_conv)
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

    def get_total_cost(
        self,
        step_name: Optional[str],
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        """
        Calculate total cost from the cost_entries collection.
        """
        try:
            total_cost = self.cost_entry_repository.get_total_cost(start_date, end_date, step_name)
            return total_cost
        except Exception as e:
            logger.error(f"Error retrieving total cost: {str(e)}")
            raise