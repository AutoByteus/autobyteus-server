from typing import List, Optional
from autobyteus_server.workflow.persistence.conversation.persistence.provider import PersistenceProvider
from autobyteus_server.workflow.persistence.conversation.repositories.postgres.step_conversation_repository import StepConversationRepository
from autobyteus_server.workflow.persistence.conversation.repositories.postgres.step_conversation_message_repository import StepConversationMessageRepository
from autobyteus_server.workflow.persistence.conversation.converters.postgresql_converter import PostgreSQLConverter
from autobyteus_server.workflow.persistence.conversation.domain.models import StepConversation, ConversationHistory
import json

class PostgresqlPersistenceProvider(PersistenceProvider):
    def __init__(self):
        super().__init__()
        self.conversation_repository = StepConversationRepository()
        self.message_repository = StepConversationMessageRepository()
        self.converter = PostgreSQLConverter()
        self.current_conversations = {}  # Changed to handle multiple conversations

    def create_conversation(self, step_name: str) -> StepConversation:
        """Create a new empty conversation."""
        postgres_conversation = self.conversation_repository.create_step_conversation(step_name)
        self.current_conversations[postgres_conversation.step_conversation_id] = postgres_conversation
        return self.converter.to_domain_conversation(postgres_conversation, [])

    def store_message(
        self, 
        step_name: str, 
        role: str, 
        message: str, 
        original_content: Optional[str] = None,  # Use original_content in domain model
        context_paths: Optional[List[str]] = None,
        conversation_id: Optional[str] = None  # New parameter
    ) -> StepConversation:
        """Store a message and return the updated conversation."""
        if conversation_id:
            # Fixed method call and removed int cast
            postgres_conv = self.conversation_repository.get_by_step_conversation_id(conversation_id)
            if not postgres_conv:
                raise ValueError(f"Conversation with ID {conversation_id} does not exist.")
        else:
            postgres_conv = self.create_conversation(step_name)
            conversation_id = postgres_conv.step_conversation_id  # Ensure step_conversation_id is used

        self.message_repository.create_message(
            step_conversation_id=postgres_conv.id,
            role=role,
            message=message,
            original_message=original_content,  # Map original_content to original_message in DB
            context_paths=context_paths
        )

        # Retrieve updated messages
        messages = self.message_repository.get_messages_by_step_conversation_id(postgres_conv.id)

        updated_conversation = self.converter.to_domain_conversation(postgres_conv, messages)
        self.current_conversations[postgres_conv.step_conversation_id] = postgres_conv

        return updated_conversation

    def get_conversation_history(self, step_name: str, page: int = 1, page_size: int = 10) -> ConversationHistory:
        """
        Retrieve paginated conversations by step name.
        """
        result = self.conversation_repository.get_conversations_by_step_name(step_name, page, page_size)
        
        conversations = []
        for postgres_conv in result["conversations"]:
            messages = self.message_repository.get_messages_by_step_conversation_id(
                postgres_conv.id
            )
            conversations.append(self.converter.to_domain_conversation(postgres_conv, messages))
        
        return ConversationHistory(
            conversations=conversations,
            total_conversations=result["total_conversations"],
            total_pages=result["total_pages"],
            current_page=result["current_page"]
        )