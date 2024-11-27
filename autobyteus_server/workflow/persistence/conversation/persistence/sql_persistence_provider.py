from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from autobyteus_server.workflow.persistence.conversation.persistence.provider import PersistenceProvider
from autobyteus_server.workflow.persistence.conversation.repositories.sql.step_conversation_repository import StepConversationRepository
from autobyteus_server.workflow.persistence.conversation.repositories.sql.step_conversation_message_repository import StepConversationMessageRepository
from autobyteus_server.workflow.persistence.conversation.repositories.sql.cost_entry_repository import CostEntryRepository
from autobyteus_server.workflow.persistence.conversation.converters.sql_converter import SQLConverter
from autobyteus_server.workflow.persistence.conversation.domain.models import StepConversation, ConversationHistory, Message
import logging

logger = logging.getLogger(__name__)

class SqlPersistenceProvider(PersistenceProvider):
    """
    Persistence provider supporting SQL-based databases like PostgreSQL and SQLite.
    """
    def __init__(self):
        super().__init__()
        self.conversation_repository = StepConversationRepository()
        self.message_repository = StepConversationMessageRepository()
        self.cost_entry_repository = CostEntryRepository()
        self.converter = SQLConverter()
        self.current_conversations = {}

    def create_conversation(self, step_name: str) -> StepConversation:
        """Create a new empty conversation."""
        try:
            sql_conversation = self.conversation_repository.create_step_conversation(step_name)
            domain_conversation = StepConversation(
                step_conversation_id=sql_conversation.step_conversation_id,
                step_name=sql_conversation.step_name,
                created_at=sql_conversation.created_at,
                messages=[],
                total_cost=0.0,
            )
            self.current_conversations[domain_conversation.step_conversation_id] = domain_conversation
            logger.info(f"Created new conversation with ID: {domain_conversation.step_conversation_id}")
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
                    sql_conv = self.conversation_repository.get_by_step_conversation_id(conversation_id)
                    if not sql_conv:
                        logger.error(f"Conversation with ID {conversation_id} not found in the database.")
                        raise ValueError(f"Conversation with ID {conversation_id} not found")
                    domain_conv = StepConversation(
                        step_conversation_id=sql_conv.step_conversation_id,
                        step_name=sql_conv.step_name,
                        created_at=sql_conv.created_at,
                        messages=[],
                        total_cost=sql_conv.total_cost,
                    )
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
                message_id=str(uuid4())
            )
            domain_conv.messages.append(new_message)
            domain_conv.total_cost += cost

            # Persist the message to the database
            sql_conv = self.conversation_repository.get_by_step_conversation_id(conversation_id)
            if not sql_conv:
                logger.error(f"Conversation with ID {conversation_id} not found in the database.")
                raise ValueError(f"Conversation with ID {conversation_id} not found")

            sql_message = self.message_repository.create_message(
                step_conversation_id=sql_conv.id,
                role=role,
                message=message,
                original_message=original_message,
                context_paths=context_paths,
                cost=cost,
            )

            # Create a cost entry
            self.cost_entry_repository.create_cost_entry(
                role=role,
                step_name=step_name,
                cost=cost,
                timestamp=datetime.utcnow(),
                conversation_id=sql_conv.id,
                message_id=sql_message.id
            )

            # Update the total cost in the conversation
            sql_conv.total_cost += cost
            self.conversation_repository.update(sql_conv)

            logger.info(f"Added message to conversation ID: {conversation_id}")

            self.current_conversations[conversation_id] = domain_conv

            return domain_conv
        except Exception as e:
            logger.error(f"Failed to store message in conversation '{conversation_id}': {str(e)}")
            raise

    def get_conversation_history(self, step_name: str, page: int = 1, page_size: int = 10) -> ConversationHistory:
        """
        Retrieve paginated conversations by step name.
        """
        try:
            result = self.conversation_repository.get_conversations_by_step_name(step_name, page, page_size)
            
            conversations = []
            for sql_conv in result["conversations"]:
                messages = self.message_repository.get_messages_by_step_conversation_id(sql_conv.id)
                conversations.append(self.converter.to_domain_conversation(sql_conv, messages))
            
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
        Calculate total cost from the cost_entries table.
        """
        try:
            total_cost = self.cost_entry_repository.get_total_cost(
                start_date=start_date,
                end_date=end_date,
                step_name=step_name
            )
            return total_cost
        except Exception as e:
            logger.error(f"Error calculating total cost: {str(e)}")
            raise

    def delete_conversation(self, conversation_id: str) -> None:
        """
        Delete a conversation without affecting the cost entries.
        """
        try:
            sql_conv = self.conversation_repository.get_by_step_conversation_id(conversation_id)
            if not sql_conv:
                logger.error(f"Conversation with ID {conversation_id} not found.")
                raise ValueError(f"Conversation with ID {conversation_id} not found")
            self.conversation_repository.delete(sql_conv)
            logger.info(f"Deleted conversation with ID: {conversation_id}")
        except Exception as e:
            logger.error(f"Error deleting conversation '{conversation_id}': {str(e)}")
            raise