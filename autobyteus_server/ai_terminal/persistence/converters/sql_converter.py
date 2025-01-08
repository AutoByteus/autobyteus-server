from typing import List
from autobyteus_server.ai_terminal.persistence.domain.models import AiTerminalMessage, AiTerminalConversation
from autobyteus_server.ai_terminal.persistence.models.sql.conversation import AiTerminalConversation as SQLConversation
from autobyteus_server.ai_terminal.persistence.models.sql.conversation_message import AiTerminalConversationMessage as SQLMessage
from datetime import datetime

class SQLConverter:
    @staticmethod
    def to_domain_message(sql_message: SQLMessage) -> AiTerminalMessage:
        """Convert a SQL message model to a domain AiTerminalMessage object."""
        return AiTerminalMessage(
            role=sql_message.role,
            message=sql_message.message,
            timestamp=sql_message.timestamp,
            message_id=str(sql_message.id),
            token_count=sql_message.token_count,
            cost=sql_message.cost
        )

    @staticmethod
    def to_domain_conversation(sql_conv: SQLConversation, messages: List[SQLMessage]) -> AiTerminalConversation:
        """Convert a SQL conversation model to a domain AiTerminalConversation object."""
        domain_messages = [SQLConverter.to_domain_message(msg) for msg in messages]
        return AiTerminalConversation(
            conversation_id=sql_conv.conversation_id,
            created_at=sql_conv.created_at,
            messages=domain_messages
        )

    @staticmethod
    def to_sql_message(domain_msg: AiTerminalMessage, conversation_id: int) -> SQLMessage:
        """Convert a domain AiTerminalMessage object to a SQL message model."""
        return SQLMessage(
            conversation_id=conversation_id,
            role=domain_msg.role,
            message=domain_msg.message,
            timestamp=domain_msg.timestamp,
            token_count=domain_msg.token_count,
            cost=domain_msg.cost
        )

    @staticmethod
    def to_sql_conversation(domain_conv: AiTerminalConversation) -> SQLConversation:
        """Convert a domain AiTerminalConversation object to a SQL conversation model."""
        return SQLConversation(
            conversation_id=domain_conv.conversation_id,
            created_at=domain_conv.created_at
        )