from typing import List
from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation
from autobyteus_server.workflow.persistence.conversation.models.sql.conversation import StepConversation as SqlStepConversation
from autobyteus_server.workflow.persistence.conversation.models.sql.conversation_message import StepConversationMessage as SqlMessage
import json
from datetime import datetime

class SQLConverter:
    @staticmethod
    def to_domain_message(sql_message: SqlMessage) -> Message:
        """Convert a SQL message model to a domain Message object."""
        return Message(
            role=sql_message.role,
            message=sql_message.message,
            timestamp=sql_message.timestamp,
            message_id=str(sql_message.id),
            original_message=sql_message.original_message,
            context_paths=json.loads(sql_message.context_paths) if sql_message.context_paths else [],
            token_count=sql_message.token_count,
            cost=sql_message.cost
        )

    @staticmethod
    def to_domain_conversation(sql_conv: SqlStepConversation, messages: List[SqlMessage]) -> StepConversation:
        """Convert a SQL conversation model to a domain StepConversation object."""
        domain_messages = [SQLConverter.to_domain_message(msg) for msg in messages]
        return StepConversation(
            step_conversation_id=sql_conv.step_conversation_id,
            step_name=sql_conv.step_name,
            created_at=sql_conv.created_at,
            messages=domain_messages,
            llm_model=sql_conv.llm_model  # Map llm_model from SQL model
        )

    @staticmethod
    def to_sql_message(domain_msg: Message, conversation_id: int) -> SqlMessage:
        """Convert a domain Message object to a SQL message model."""
        return SqlMessage(
            step_conversation_id=conversation_id,
            role=domain_msg.role,
            message=domain_msg.message,
            original_message=domain_msg.original_message,
            context_paths=json.dumps(domain_msg.context_paths) if domain_msg.context_paths else None,
            timestamp=domain_msg.timestamp,
            token_count=domain_msg.token_count,
            cost=domain_msg.cost
        )

    @staticmethod
    def to_sql_conversation(domain_conv: StepConversation) -> SqlStepConversation:
        """Convert a domain StepConversation object to a SQL conversation model."""
        return SqlStepConversation(
            step_conversation_id=domain_conv.step_conversation_id,
            step_name=domain_conv.step_name,
            created_at=domain_conv.created_at,
            llm_model=domain_conv.llm_model  # Include llm_model in SQL model
        )
