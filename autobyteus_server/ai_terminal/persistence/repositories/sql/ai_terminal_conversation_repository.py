
import logging
from typing import Optional, List, Dict, Any
from repository_sqlalchemy import BaseRepository
from autobyteus_server.ai_terminal.persistence.models.sql.conversation import AiTerminalConversation

logger = logging.getLogger(__name__)

class AiTerminalConversationRepository(BaseRepository[AiTerminalConversation]):
    """
    SQL repository for AI Terminal conversations.
    """

    def create_conversation(self) -> AiTerminalConversation:
        """
        Create and persist a new AiTerminalConversation entity.
        """
        try:
            conversation = AiTerminalConversation()
            return self.create(conversation)
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise

    def find_by_conversation_id(self, conversation_id: str) -> Optional[AiTerminalConversation]:
        """
        Find a conversation by its UUID conversation_id.
        """
        try:
            return self.session.query(self.model)\
                .filter_by(conversation_id=conversation_id)\
                .first()
        except Exception as e:
            logger.error(f"Error finding conversation by id: {str(e)}")
            raise

    def list_conversations(self, skip: int, limit: int) -> Dict[str, Any]:
        """
        Return a paginated list of conversations with metadata.
        """
        try:
            query = self.session.query(self.model)\
                .order_by(self.model.created_at.desc())
            
            total = query.count()
            conversations = query.offset(skip).limit(limit).all()
            total_pages = (total + limit - 1) // limit
            current_page = (skip // limit) + 1

            return {
                "conversations": conversations,
                "total": total,
                "total_pages": total_pages,
                "current_page": current_page
            }
        except Exception as e:
            logger.error(f"Error listing conversations: {str(e)}")
            raise
