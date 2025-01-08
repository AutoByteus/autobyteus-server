
from datetime import datetime
from typing import List

from bson import ObjectId

from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation
from autobyteus_server.workflow.persistence.conversation.models.mongodb.conversation import StepConversation as MongoStepConversation
from autobyteus_server.workflow.persistence.conversation.models.mongodb.conversation import Message as MongoMessage

class MongoDBConverter:
    @staticmethod
    def to_domain_message(mongo_message: dict) -> Message:
        """
        Convert a MongoDB message dictionary to a domain Message object.

        Args:
            mongo_message (dict): The message data from MongoDB.

        Returns:
            Message: The domain Message object.
        """
        return Message(
            role=mongo_message.get('role'),
            message=mongo_message.get('message'),
            timestamp=mongo_message.get('timestamp'),
            message_id=str(mongo_message.get('_id', '')),
            original_message=mongo_message.get('original_message'),
            context_paths=mongo_message.get('context_paths', []),
            token_count=mongo_message.get('token_count'),
            cost=mongo_message.get('cost')
        )

    @staticmethod
    def to_domain_conversation(mongo_conv: MongoStepConversation, messages: List[dict]) -> StepConversation:
        """
        Convert a MongoDB conversation and its messages to a domain StepConversation object.

        Args:
            mongo_conv (MongoStepConversation): The conversation data from MongoDB.
            messages (List[dict]): List of message dictionaries from MongoDB.

        Returns:
            StepConversation: The domain StepConversation object.
        """
        domain_messages = [MongoDBConverter.to_domain_message(msg) for msg in messages]
        return StepConversation(
            step_conversation_id=str(mongo_conv._id),  # Map MongoDB's _id to domain's step_conversation_id
            step_name=mongo_conv.step_name,
            created_at=mongo_conv.created_at,
            messages=domain_messages
        )
    
    @staticmethod
    def to_mongo_conversation(domain_conv: StepConversation) -> MongoStepConversation:
        """
        Convert a domain StepConversation object to a MongoDB StepConversation model.

        Args:
            domain_conv (StepConversation): The domain StepConversation object.

        Returns:
            MongoStepConversation: The MongoDB StepConversation model.
        """
        mongo_conv = MongoStepConversation(
            step_name=domain_conv.step_name,
            created_at=domain_conv.created_at,
            messages=[{
                "role": msg.role,
                "message": msg.message,
                "timestamp": msg.timestamp,
                "original_message": msg.original_message,
                "context_paths": msg.context_paths,
                "token_count": msg.token_count,
                "cost": msg.cost
            } for msg in domain_conv.messages]
        )
        if domain_conv.step_conversation_id:
            mongo_conv._id = ObjectId(domain_conv.step_conversation_id)
        return mongo_conv
