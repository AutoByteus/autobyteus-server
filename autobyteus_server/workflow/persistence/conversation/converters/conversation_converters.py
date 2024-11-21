from autobyteus_server.workflow.persistence.conversation.domain.models import (
    Message as DomainMessage,
    StepConversation as DomainStepConversation,
    ConversationHistory as DomainConversationHistory,
)
from autobyteus_server.api.graphql.types.conversation_types import (
    Message as GraphQLMessage,
    StepConversation as GraphQLStepConversation,
    ConversationHistory as GraphQLConversationHistory,
)

class MessageConverter:
    @staticmethod
    def to_graphql(domain_message: DomainMessage) -> GraphQLMessage:
        return GraphQLMessage(
            message_id=domain_message.message_id,
            role=domain_message.role,
            message=domain_message.message,
            timestamp=domain_message.timestamp.isoformat(),
            context_paths=domain_message.context_paths,
            original_message=domain_message.original_message,
            cost=domain_message.cost  # Include cost
        )

class StepConversationConverter:
    @staticmethod
    def to_graphql(domain_conversation: DomainStepConversation) -> GraphQLStepConversation:
        messages = [
            MessageConverter.to_graphql(msg)
            for msg in domain_conversation.messages
        ]
        return GraphQLStepConversation(
            step_conversation_id=domain_conversation.step_conversation_id,
            step_name=domain_conversation.step_name,
            created_at=domain_conversation.created_at.isoformat(),
            messages=messages,
            total_cost=domain_conversation.total_cost,  # Include total_cost
        )

class ConversationHistoryConverter:
    @staticmethod
    def to_graphql(domain_history: DomainConversationHistory) -> GraphQLConversationHistory:
        conversations = [
            StepConversationConverter.to_graphql(conv)
            for conv in domain_history.conversations
        ]
        return GraphQLConversationHistory(
            conversations=conversations,
            total_conversations=domain_history.total_conversations,
            total_pages=domain_history.total_pages,
            current_page=domain_history.current_page,
        )