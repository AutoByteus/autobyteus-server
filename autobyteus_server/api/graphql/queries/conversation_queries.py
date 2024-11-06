import strawberry
from typing import List
from autobyteus_server.api.graphql.types.conversation_types import ConversationHistory
from autobyteus_server.api.graphql.converters.conversation_converters import ConversationHistoryConverter
from autobyteus_server.workflow.persistence.conversation.persistence.persistence_proxy import PersistenceProxy

persistence_proxy = PersistenceProxy()

@strawberry.type
class Query:
    @strawberry.field
    async def getConversationHistory(
        self,
        stepName: str,
        page: int = 1,
        pageSize: int = 10
    ) -> ConversationHistory:
        """
        Retrieve paginated conversation history for a specific step.
        
        Args:
            stepName (str): The name of the step to get conversation history for
            page (int): Page number (1-based indexing)
            pageSize (int): Number of items per page
            
        Returns:
            ConversationHistory: Paginated conversation history
        """
        if page < 1:
            raise ValueError("Page number must be at least 1.")
        if pageSize < 1 or pageSize > 100:
            raise ValueError("Page size must be between 1 and 100.")        
        try:
            # Get conversation history from persistence layer
            domain_history = persistence_proxy.get_conversation_history(
                step_name=stepName,
                page=page,
                page_size=pageSize
            )
            
            # Convert domain history to GraphQL type using converter
            return ConversationHistoryConverter.to_graphql(domain_history)
            
        except ValueError as e:
            # Re-raise validation errors
            raise e
        except Exception as e:
            error_message = f"Failed to retrieve conversation history: {str(e)}"
            raise Exception(error_message)