from typing import List
from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation
from autobyteus_server.workflow.persistence.conversation.models.sql.conversation import StepConversation as SqlStepConversation
from autobyteus_server.workflow.persistence.conversation.models.sql.conversation_message import StepConversationMessage as SqlMessage
import json

class SQLConverter:
    @staticmethod
    def to_domain_message(sql_message: SqlMessage) -> Message:
        return Message(
            role=sql_message.role,
            message=sql_message.message,
            timestamp=sql_message.timestamp,
            message_id=str(sql_message.id),
            original_message=sql_message.original_message,
            context_paths=json.loads(sql_message.context_paths) if sql_message.context_paths else []
        )

    @staticmethod
    def to_domain_conversation(sql_conv: SqlStepConversation, messages: List[SqlMessage]) -> StepConversation:
        domain_messages = [SQLConverter.to_domain_message(msg) for msg in messages]
        return StepConversation(
            step_conversation_id=sql_conv.step_conversation_id,
            step_name=sql_conv.step_name,
            created_at=sql_conv.created_at,
            messages=domain_messages
        )