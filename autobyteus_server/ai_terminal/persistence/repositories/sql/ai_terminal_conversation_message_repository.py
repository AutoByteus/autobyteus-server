
import logging
from typing import List, Optional
from repository_sqlalchemy import BaseRepository
from autobyteus_server.ai_terminal.persistence.models.sql.conversation_message import AiTerminalConversationMessage

logger = logging.getLogger(__name__)

class AiTerminalConversationMessageRepository(BaseRepository[AiTerminalConversationMessage]):
    """
    SQL repository for AI Terminal conversation messages.
    """

    def create_message(
        self, 
        conversation_id: int, 
        role: str, 
        message: str,
        token_count: Optional[int] = None,
        cost: Optional[float] = None
    ) -> AiTerminalConversationMessage:
        """
        Create a new conversation message with optional token count and cost.
        """
        try:
            new_message = AiTerminalConversationMessage(
                conversation_id=conversation_id,
                role=role,
                message=message,
                token_count=token_count,
                cost=cost
            )
            return self.create(new_message)
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            raise

    def get_messages_by_conversation_id(self, conversation_id: int) -> List[AiTerminalConversationMessage]:
        """
        Retrieve all messages for a specific conversation, ordered by timestamp.
        """
        try:
            return self.session.query(self.model)\
                .filter_by(conversation_id=conversation_id)\
                .order_by(self.model.timestamp)\
                .all()
        except Exception as e:
            logger.error(f"Error retrieving messages for conversation {conversation_id}: {str(e)}")
            raise

    def update_message(self, message_id: int, new_content: str) -> Optional[AiTerminalConversationMessage]:
        """
        Update the content of an existing message.
        """
        try:
            message = self.session.query(self.model).filter_by(id=message_id).first()
            if message:
                message.message = new_content
                return message
            logger.warning(f"Message with id {message_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error updating message: {str(e)}")
            raise

    def update_token_usage(self, message_id: int, token_count: int, cost: float) -> Optional[AiTerminalConversationMessage]:
        """
        Update token count and cost for a specific message.
        """
        try:
            message = self.session.query(self.model).filter_by(id=message_id).first()
            if message:
                message.token_count = token_count
                message.cost = cost
                logger.info(f"Updated token usage for message {message_id}")
                return message
            logger.warning(f"Message with id {message_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error updating token usage for message {message_id}: {str(e)}")
            raise
