from repository_sqlalchemy import BaseRepository
from typing import Dict, Any, List, Optional
import json
import logging
from autobyteus_server.workflow.persistence.conversation.models.sql.conversation_message import StepConversationMessage

logger = logging.getLogger(__name__)

class StepConversationMessageRepository(BaseRepository[StepConversationMessage]):
    def create_message(
        self,
        step_conversation_id: int,
        role: str,
        message: str,
        original_message: Optional[str] = None,
        context_paths: Optional[List[str]] = None,
        cost: float = 0.0
    ) -> StepConversationMessage:
        """
        Create a new step conversation message.
        """
        try:
            context_paths_json = json.dumps(context_paths) if context_paths else None
            new_message = StepConversationMessage(
                step_conversation_id=step_conversation_id,
                role=role,
                message=message,
                original_message=original_message,
                context_paths=context_paths_json,
                cost=cost
            )
            return self.create(new_message)
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            raise

    def get_messages_by_step_conversation_id(self, step_conversation_id: int) -> List[StepConversationMessage]:
        """
        Retrieve all messages for a specific step conversation.
        """
        try:
            return self.session.query(self.model)\
                .filter_by(step_conversation_id=step_conversation_id)\
                .order_by(self.model.timestamp)\
                .all()
        except Exception as e:
            logger.error(f"Error retrieving messages for step conversation {step_conversation_id}: {str(e)}")
            raise

    def update_message(self, message_id: int, new_content: str) -> Optional[StepConversationMessage]:
        """
        Update the content of an existing message.
        """
        try:
            message = self.session.query(self.model).filter_by(id=message_id).first()
            if message:
                message.message = new_content
                return message
            else:
                logger.warning(f"Message with id {message_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error updating message: {str(e)}")
            raise

    def delete_message(self, message_id: int) -> bool:
        """
        Delete a message by its ID.
        """
        try:
            message = self.session.query(self.model).filter_by(id=message_id).first()
            if message:
                self.delete(message)
                return True
            else:
                logger.warning(f"Message with id {message_id} not found")
                return False
        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")
            raise