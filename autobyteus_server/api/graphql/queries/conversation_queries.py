import strawberry
from datetime import datetime, timedelta
from typing import Optional
from autobyteus_server.api.graphql.types.conversation_types import ConversationHistory, Message, StepConversation
from autobyteus_server.workflow.persistence.conversation.persistence.persistence_proxy import PersistenceProxy

@strawberry.type
class Query:
    @strawberry.field
    def get_conversation_history(
        self, step_name: str, page: int, page_size: int
    ) -> ConversationHistory:
        """
        Retrieve conversation history for a given step.

        Args:
            step_name: The name of the step.
            page: The page number.
            page_size: The number of items per page.

        Returns:
            ConversationHistory: The conversation history.
        """
        persistence_proxy = PersistenceProxy()
        conversation_history = persistence_proxy.get_conversation_history(
            step_name, page, page_size)

        # Map domain models to GraphQL types
        conversations = [
            StepConversation(
                step_conversation_id=conv.step_conversation_id,
                step_name=conv.step_name,
                created_at=conv.created_at.isoformat(),
                total_cost=conv.total_cost,
                messages=[
                    Message(
                        message_id=msg.message_id,
                        role=msg.role,
                        message=msg.message,
                        timestamp=msg.timestamp.isoformat(),
                        original_message=msg.original_message,
                        context_paths=msg.context_paths,
                        cost=msg.cost,
                    )
                    for msg in conv.messages
                ],
            )
            for conv in conversation_history.conversations
        ]

        return ConversationHistory(
            conversations=conversations,
            total_conversations=conversation_history.total_conversations,
            total_pages=conversation_history.total_pages,
            current_page=conversation_history.current_page,
        )

    @strawberry.field
    def get_cost_summary(self, step_name: Optional[str], time_frame: str) -> float:
        """
        Get the total cost for a given time frame.

        Args:
            step_name: The name of the step (optional).
            time_frame: The time frame ('week' or 'month').

        Returns:
            float: The total cost.
        """
        persistence_proxy = PersistenceProxy()
        end_date = datetime.utcnow()
        if time_frame == 'week':
            start_date = end_date - timedelta(weeks=1)
        elif time_frame == 'month':
            start_date = end_date - timedelta(days=30)
        else:
            raise ValueError("Invalid time frame. Use 'week' or 'month'.")

        total_cost = persistence_proxy.get_total_cost(
            step_name, start_date, end_date)
        return total_cost

    @strawberry.field
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation by its ID.

        Args:
            conversation_id: The ID of the conversation to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        persistence_proxy = PersistenceProxy()
        try:
            persistence_proxy.delete_conversation(conversation_id)
            return True
        except Exception:
            return False