
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from repository_mongodb import BaseRepository
from bson import ObjectId
from autobyteus_server.ai_terminal.persistence.models.mongodb.conversation import AiTerminalConversation, Message

logger = logging.getLogger(__name__)


class ConversationNotFoundError(Exception):
    """Raised when a conversation is not found."""
    pass


class AiTerminalConversationRepository(BaseRepository[AiTerminalConversation]):
    """MongoDB repository for AI Terminal conversations."""

    def create_conversation(self, conversation_id: str) -> AiTerminalConversation:
        """Create a new conversation."""
        try:
            conversation = AiTerminalConversation(conversation_id=conversation_id)
            result = self.collection.insert_one(conversation.to_dict(), session=self.session)
            conversation._id = result.inserted_id
            logger.info(f"Created new AI Terminal conversation: {conversation_id}")
            return conversation
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise

    def find_by_conversation_id(self, conversation_id: str) -> Optional[AiTerminalConversation]:
        """Find a conversation by conversation_id."""
        try:
            data = self.collection.find_one({"conversation_id": conversation_id}, session=self.session)
            if data:
                return AiTerminalConversation.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Error finding conversation: {str(e)}")
            raise

    def add_message(
        self,
        conversation_id: str,
        role: str,
        message: str,
        token_count: Optional[int] = None,
        cost: Optional[float] = None
    ) -> Optional[AiTerminalConversation]:
        """Add a new message to an existing conversation."""
        try:
            new_message = Message(
                role=role,
                message=message,
                token_count=token_count,
                cost=cost
            ).to_dict()

            result = self.collection.update_one(
                {"conversation_id": conversation_id},
                {"$push": {"messages": new_message}},
                session=self.session
            )
            
            if result.modified_count == 0:
                return None

            updated = self.collection.find_one({"conversation_id": conversation_id}, session=self.session)
            if not updated:
                return None
                
            return AiTerminalConversation.from_dict(updated)
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            raise

    def list_conversations(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """List conversations with pagination."""
        try:
            cursor = self.collection.find(
                {},
                session=self.session
            ).sort("created_at", -1).skip(skip).limit(limit)
            
            total_count = self.collection.count_documents({}, session=self.session)
            
            conversations = [AiTerminalConversation.from_dict(doc) for doc in cursor]
            
            return {
                "conversations": conversations,
                "total_conversations": total_count,
                "total_pages": (total_count + limit - 1) // limit,
                "current_page": (skip // limit) + 1
            }
        except Exception as e:
            logger.error(f"Error listing conversations: {str(e)}")
            raise
