from datetime import datetime
from typing import List
from bson import ObjectId

from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation
from autobyteus_server.workflow.persistence.conversation.models.mongodb.conversation import StepConversation as MongoStepConversation
from autobyteus_server.workflow.persistence.conversation.models.mongodb.conversation import Message as MongoMessage

class MongoDBConverter:
    @staticmethod
    def to_domain_message(mongo_message: MongoMessage) -> Message:
        return Message(
            role=mongo_message.role,
            message=mongo_message.message,  # Mapped message
            timestamp=mongo_message.timestamp,
            message_id=str(mongo_message.id),
            original_message=mongo_message.original_message,  # Mapped original_message
            context_paths=mongo_message.context_paths
        )

    @staticmethod
    def to_domain_conversation(mongo_conv: MongoStepConversation, messages: List[MongoMessage]) -> StepConversation:
        domain_messages = [MongoDBConverter.to_domain_message(msg) for msg in messages]
        return StepConversation(
            step_conversation_id=str(mongo_conv.step_conversation_id),
            step_name=mongo_conv.step_name,
            created_at=mongo_conv.created_at,
            messages=domain_messages
        )