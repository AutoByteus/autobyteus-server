from typing import List, Optional
from autobyteus_server.workflow.persistence.conversation.persistence.provider import PersistenceProvider
from autobyteus_server.workflow.persistence.conversation.repositories.sql.step_conversation_repository import StepConversationRepository
from autobyteus_server.workflow.persistence.conversation.repositories.sql.step_conversation_message_repository import StepConversationMessageRepository
from autobyteus_server.workflow.persistence.conversation.converters.sql_converter import SQLConverter
from autobyteus_server.workflow.persistence.conversation.domain.models import StepConversation, ConversationHistory
from sqlalchemy.orm import sessionmaker
from autobyteus_server.infrastructure.database import engine  # Replace with the actual import path for your engine
import logging

logger = logging.getLogger(__name__)

class SqlPersistenceProvider(PersistenceProvider):
    def __init__(self):
        #super().__init__()
        # Create a SQLAlchemy session
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.conversation_repository = StepConversationRepository(self.session)
        self.message_repository = StepConversationMessageRepository(self.session)
        self.converter = SQLConverter()
        self.current_conversations = {}  

    def create_conversation(self, step_name: str) -> StepConversation:
        try:
            sql_conversation = self.conversation_repository.create_step_conversation(step_name)
            self.current_conversations[sql_conversation.step_conversation_id] = sql_conversation
            return self.converter.to_domain_conversation(sql_conversation, [])
        except Exception as e:
            logger.error(f"Error creating conversation for step '{step_name}': {str(e)}")
            raise

    def store_message(
        self, 
        step_name: str, 
        role: str, 
        message: str, 
        original_message: Optional[str] = None,
        context_paths: Optional[List[str]] = None,
        conversation_id: Optional[str] = None
    ) -> StepConversation:
        try:
            sql_conv = None
            if conversation_id:
                sql_conv = self.current_conversations.get(conversation_id)
                if not sql_conv:
                    sql_conv = self.conversation_repository.get_by_step_conversation_id(conversation_id)
                    if not sql_conv:
                        logger.error(f"Conversation with ID {conversation_id} does not exist.")
                        raise ValueError(f"Conversation with ID {conversation_id} does not exist.")
                    self.current_conversations[conversation_id] = sql_conv
            else:
                sql_conv = self.conversation_repository.create_step_conversation(step_name)
                self.current_conversations[sql_conv.step_conversation_id] = sql_conv
            self.message_repository.create_message(
                step_conversation_id=sql_conv.id,  # Use the 'id' attribute here
                role=role,
                message=message,
                original_message=original_message,
                context_paths=context_paths
            )
            messages = self.message_repository.get_messages_by_step_conversation_id(sql_conv.id)  # Use 'id' attribute
            updated_conversation = self.converter.to_domain_conversation(sql_conv, messages)
            return updated_conversation
        except Exception as e:
            logger.error(f"Failed to store message in conversation '{conversation_id}': {str(e)}")
            raise

    def get_conversation_history(self, step_name: str, page: int = 1, page_size: int = 10) -> ConversationHistory:
        try:
            result = self.conversation_repository.get_conversations_by_step_name(step_name, page, page_size)
            conversations = []
            for sql_conv in result["conversations"]:
                messages = self.message_repository.get_messages_by_step_conversation_id(sql_conv.id)  # Use 'id' attribute
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
