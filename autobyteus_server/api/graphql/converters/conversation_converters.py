from typing import List, Optional
from autobyteus_server.workflow.persistence.conversation.domain.models import (
    Message as DomainMessage,
    StepConversation as DomainStepConversation,
    ConversationHistory as DomainConversationHistory
)
from autobyteus_server.api.graphql.types.conversation_types import (
    Message as GraphQLMessage,
    StepConversation as GraphQLStepConversation,
    ConversationHistory as GraphQLConversationHistory
)

class MessageConverter:
    """Converts between domain and GraphQL Message types"""
    
    @staticmethod
    def to_graphql(domain_message: DomainMessage) -> GraphQLMessage:
        """Convert domain Message to GraphQL Message"""
        try:
            return GraphQLMessage(
                message_id=domain_message.message_id,
                role=domain_message.role,
                message=domain_message.message,  # Mapped message
                timestamp=domain_message.timestamp.isoformat(),
                context_paths=domain_message.context_paths,       # Mapped context_paths
                original_message=domain_message.original_message  # Mapped original_message
            )
        except Exception as e:
            raise ValueError(f"Failed to convert Message to GraphQL type: {str(e)}")

class StepConversationConverter:
    """Converts between domain and GraphQL StepConversation types"""
    
    @staticmethod
    def to_graphql(domain_conversation: DomainStepConversation) -> GraphQLStepConversation:
        """Convert domain StepConversation to GraphQL StepConversation"""
        try:
            messages = [
                MessageConverter.to_graphql(msg)
                for msg in domain_conversation.messages
            ]
            
            return GraphQLStepConversation(
                step_conversation_id=domain_conversation.step_conversation_id,
                step_name=domain_conversation.step_name,
                created_at=domain_conversation.created_at.isoformat(),
                messages=messages,
                total_cost=domain_conversation.total_cost
            )
        except Exception as e:
            raise ValueError(f"Failed to convert StepConversation to GraphQL type: {str(e)}")

class ConversationHistoryConverter:
    """Converts between domain and GraphQL ConversationHistory types"""
    
    @staticmethod
    def to_graphql(domain_history: DomainConversationHistory) -> GraphQLConversationHistory:
        """Convert domain ConversationHistory to GraphQL ConversationHistory"""
        try:
            conversations = [
                StepConversationConverter.to_graphql(conv)
                for conv in domain_history.conversations
            ]
            
            return GraphQLConversationHistory(
                conversations=conversations,
                total_conversations=domain_history.total_conversations,
                total_pages=domain_history.total_pages,
                current_page=domain_history.current_page
            )
        except Exception as e:
            raise ValueError(f"Failed to convert ConversationHistory to GraphQL type: {str(e)}")