from typing import Any, List, Optional

from bson import ObjectId
from autobyteus_server.workflow.persistence.conversation.persistence.provider import PersistenceProvider
from autobyteus_server.workflow.persistence.conversation.repositories.mongodb.step_conversation_repository import StepConversationRepository
from autobyteus_server.workflow.persistence.conversation.converters.mongodb_converter import MongoDBConverter
from autobyteus_server.workflow.persistence.conversation.domain.models import StepConversation, ConversationHistory
from autobyteus.utils.singleton import SingletonMeta

class MongoPersistenceProvider(PersistenceProvider):
    def __init__(self):
        super().__init__()
        self.conversation_repository = StepConversationRepository()
        self.converter = MongoDBConverter()
        self.current_conversations = {}  # Changed to handle multiple conversations

    def create_conversation(self, step_name: str) -> StepConversation:
        """Create a new empty conversation."""
        mongo_conversation = self.conversation_repository.create_conversation(step_name)
        self.current_conversations[mongo_conversation.step_conversation_id] = mongo_conversation
        return self.converter.to_domain_conversation(mongo_conversation, [])

    def store_message(
        self, 
        step_name: str, 
        role: str, 
        message: str, 
        original_message: Optional[str] = None,  # Use original_message in domain model
        context_paths: Optional[List[str]] = None,
        conversation_id: Optional[str] = None  # New parameter
    ) -> StepConversation:
        """Store a message and return the updated conversation."""
        if conversation_id:
            step_conversation_id = ObjectId(conversation_id)
            mongo_conv = self.conversation_repository.get_conversation_by_id(step_conversation_id)
            if not mongo_conv:
                raise ValueError(f"Conversation with ID {conversation_id} does not exist.")
        else:
            mongo_conv = self.create_conversation(step_name)
            step_conversation_id = mongo_conv.step_conversation_id

        updated_conv = self.conversation_repository.add_message(
            step_conversation_id=step_conversation_id,
            role=role,
            message=message,
            original_message=original_message,  # Map original_message to original_message in DB
            context_paths=context_paths
        )

        if updated_conv:
            self.current_conversations[step_conversation_id] = updated_conv

        return self.converter.to_domain_conversation(updated_conv, 
            self.conversation_repository.get_messages_by_step_conversation_id(step_conversation_id)
        )

    def get_conversation_history(self, step_name: str, page: int = 1, page_size: int = 10) -> ConversationHistory:
        """
        Retrieve paginated conversations by step name.
        """
        result = self.conversation_repository.get_conversations_by_step_name(step_name, page, page_size)
        
        conversations = []
        for mongo_conv in result["conversations"]:
            messages = self.conversation_repository.get_messages_by_step_conversation_id(
                mongo_conv.step_conversation_id,
                skip_messages=0,
                limit_messages=None
            )
            conversations.append(self.converter.to_domain_conversation(mongo_conv, messages))
        
        return ConversationHistory(
            conversations=conversations,
            total_conversations=result["total_conversations"],
            total_pages=result["total_pages"],
            current_page=result["current_page"]
        )