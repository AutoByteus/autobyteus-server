from sqlalchemy import func
from repository_sqlalchemy import BaseRepository
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from autobyteus_server.workflow.persistence.conversation.models.sql.conversation import StepConversation

logger = logging.getLogger(__name__)

class StepConversationRepository(BaseRepository[StepConversation]):
    def create_step_conversation(self, step_name: str) -> StepConversation:
        try:
            conversation = StepConversation(
                step_name=step_name
            )
            return self.create(conversation)
        except Exception as e:
            logger.error(f"Error creating step conversation: {str(e)}")
            raise

    def get_by_id(self, id: int) -> Optional[StepConversation]:
        """
        Retrieve a step conversation by its internal database ID.
        """
        try:
            return self.session.query(self.model).filter_by(id=id).first()
        except Exception as e:
            logger.error(f"Error retrieving step conversation by id: {str(e)}")
            raise

    def get_by_step_conversation_id(self, step_conversation_id: str) -> Optional[StepConversation]:
        """
        Retrieve a step conversation by its UUID step_conversation_id.
        """
        try:
            return self.session.query(self.model).filter_by(step_conversation_id=step_conversation_id).first()
        except Exception as e:
            logger.error(f"Error retrieving step conversation by step_conversation_id: {str(e)}")
            raise

    def get_conversations_by_step_name(self, step_name: str, page: int, page_size: int) -> Dict[str, Any]:
        try:
            skip = (page - 1) * page_size
            conversations_query = self.session.query(self.model).filter_by(step_name=step_name).order_by(self.model.created_at.desc())
            total_conversations = conversations_query.count()
            conversations = conversations_query.offset(skip).limit(page_size).all()
            total_pages = (total_conversations + page_size - 1) // page_size
            current_page = page

            return {
                "conversations": conversations,
                "total_conversations": total_conversations,
                "total_pages": total_pages,
                "current_page": current_page
            }
        except Exception as e:
            logger.error(f"Error retrieving paginated step conversations by name: {str(e)}")
            raise

    def update(self, conversation: StepConversation) -> StepConversation:
        """
        Update an existing step conversation.
        """
        try:
            self.session.merge(conversation)
            self.session.commit()
            return conversation
        except Exception as e:
            logger.error(f"Error updating step conversation: {str(e)}")
            raise