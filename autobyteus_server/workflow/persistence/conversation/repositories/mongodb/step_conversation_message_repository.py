import logging
from datetime import datetime
from typing import List, Optional
from pymongo import MongoClient
from bson import ObjectId
from autobyteus_server.workflow.persistence.conversation.models.mongodb.conversation import Message

logger = logging.getLogger(__name__)

class StepConversationMessageRepository:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client['autobyteus']
        self.collection = self.db['step_conversation_messages']

    def create_message(
        self,
        conversation_id: ObjectId,
        role: str,
        message: str,
        original_message: Optional[str] = None,
        context_paths: Optional[List[str]] = None,
        cost: float = 0.0
    ) -> Message:
        try:
            new_message = Message(
                role=role,
                message=message,
                timestamp=datetime.utcnow(),
                original_message=original_message,
                context_paths=context_paths or [],
                cost=cost
            )
            message_dict = new_message.to_dict()
            message_dict['conversation_id'] = conversation_id
            result = self.collection.insert_one(message_dict)
            new_message.message_id = str(result.inserted_id)
            return new_message
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            raise

    def get_messages_by_conversation_id(self, conversation_id: ObjectId) -> List[Message]:
        try:
            cursor = self.collection.find({"conversation_id": conversation_id}).sort("timestamp", 1)
            return [Message.from_dict(doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Error retrieving messages for conversation {conversation_id}: {str(e)}")
            raise

    def update_message(self, message_id: str, new_content: str) -> Optional[Message]:
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(message_id)},
                {"$set": {"message": new_content}}
            )
            if result.modified_count:
                doc = self.collection.find_one({"_id": ObjectId(message_id)})
                return Message.from_dict(doc)
            else:
                logger.warning(f"Message with id {message_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error updating message: {str(e)}")
            raise

    def delete_message(self, message_id: str) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(message_id)})
            if result.deleted_count:
                return True
            else:
                logger.warning(f"Message with id {message_id} not found")
                return False
        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")
            raise