
from datetime import datetime
from typing import List, Dict

from autobyteus_server.ai_terminal.persistence.domain.models import AiTerminalMessage, AiTerminalConversation
from autobyteus_server.ai_terminal.persistence.models.mongodb.conversation import AiTerminalConversation as MongoAiTerminalConversation
from autobyteus_server.ai_terminal.persistence.models.mongodb.conversation import Message as MongoMessage

class MongoDBConverter:
    @staticmethod
    def to_domain_message(mongo_message: dict) -> AiTerminalMessage:
        """
        Convert a MongoDB message dictionary to a domain AiTerminalMessage object.

        Args:
            mongo_message (dict): The message data from MongoDB.

        Returns:
            AiTerminalMessage: The domain AiTerminalMessage object.
        """
        return AiTerminalMessage(
            role=mongo_message.get('role'),
            message=mongo_message.get('message'),
            timestamp=mongo_message.get('timestamp'),
            message_id=str(mongo_message.get('_id', '')),
            token_count=mongo_message.get('token_count'),
            cost=mongo_message.get('cost')
        )

    @staticmethod
    def to_domain_conversation(mongo_conv: MongoAiTerminalConversation, messages: List[dict]) -> AiTerminalConversation:
        """
        Convert a MongoDB conversation and its messages to a domain AiTerminalConversation object.

        Args:
            mongo_conv (MongoAiTerminalConversation): The conversation data from MongoDB.
            messages (List[dict]): List of message dictionaries from MongoDB.

        Returns:
            AiTerminalConversation: The domain AiTerminalConversation object.
        """
        domain_messages = [MongoDBConverter.to_domain_message(msg) for msg in messages]
        return AiTerminalConversation(
            conversation_id=mongo_conv.conversation_id,
            created_at=mongo_conv.created_at,
            messages=domain_messages
        )
    
    @staticmethod
    def to_mongo_conversation(domain_conv: AiTerminalConversation) -> MongoAiTerminalConversation:
        """
        Convert a domain AiTerminalConversation object to a MongoDB AiTerminalConversation model.

        Args:
            domain_conv (AiTerminalConversation): The domain AiTerminalConversation object.

        Returns:
            MongoAiTerminalConversation: The MongoDB AiTerminalConversation model.
        """
        mongo_conv = MongoAiTerminalConversation(
            conversation_id=domain_conv.conversation_id,
            created_at=domain_conv.created_at,
            messages=[{
                "role": msg.role,
                "message": msg.message,
                "timestamp": msg.timestamp,
                "token_count": msg.token_count,
                "cost": msg.cost
            } for msg in domain_conv.messages]
        )
        return mongo_conv
