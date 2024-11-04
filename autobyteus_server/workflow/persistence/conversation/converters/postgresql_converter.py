from typing import List
from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation
from autobyteus_server.workflow.persistence.conversation.models.postgres.conversation import StepConversation as PostgresStepConversation
from autobyteus_server.workflow.persistence.conversation.models.postgres.conversation_message import StepConversationMessage as PostgresMessage
import json

class PostgreSQLConverter:
    @staticmethod
    def to_domain_message(postgres_message: PostgresMessage) -> Message:
        return Message(
            role=postgres_message.role,
            message=postgres_message.message,  # Mapped message
            timestamp=postgres_message.timestamp,
            message_id=str(postgres_message.id),
            original_message=postgres_message.original_message,  # Mapped original_message
            context_paths=json.loads(postgres_message.context_paths) if postgres_message.context_paths else []  # Parsed context_paths
        )

    @staticmethod
    def to_domain_conversation(postgres_conv: PostgresStepConversation, messages: List[PostgresMessage]) -> StepConversation:
        domain_messages = [PostgreSQLConverter.to_domain_message(msg) for msg in messages]
        return StepConversation(
            step_conversation_id=postgres_conv.step_conversation_id,
            step_name=postgres_conv.step_name,
            created_at=postgres_conv.created_at,
            messages=domain_messages
        )