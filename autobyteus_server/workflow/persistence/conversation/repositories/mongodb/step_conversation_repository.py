import logging
from repository_mongodb import BaseRepository
from bson import ObjectId
from typing import List, Optional, Dict, Any
from autobyteus_server.workflow.persistence.conversation.models.mongodb.conversation import StepConversation

logger = logging.getLogger(__name__)

class ConversationNotFoundError(Exception):
    """Raised when a conversation is not found by its ID."""
    pass

class StepConversationRepository(BaseRepository[StepConversation]):
    def create_conversation(self, step_name: str) -> StepConversation:
        """Create a new conversation."""
        try:
            conversation = StepConversation(step_name=step_name)
            result = self.collection.insert_one(conversation.to_dict(), session=self.session)
            conversation._id = result.inserted_id  # Assign the generated _id back to the instance
            return conversation
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise

    def add_message(
        self,
        conversation_id: ObjectId,
        role: str,
        message: str,
        original_message: Optional[str] = None,
        context_paths: Optional[List[str]] = None
    ) -> StepConversation:
        """
        Add a message to an existing conversation.
        
        Args:
            conversation_id (ObjectId): MongoDB _id of the conversation
            role (str): Role of the message sender
            message (str): Message content
            original_message (Optional[str]): Original message if applicable
            context_paths (Optional[List[str]]): List of context file paths
        """
        try:
            conversation = self.get_conversation_by_id(conversation_id)
            conversation.add_message(role=role, message=message, original_message=original_message, context_paths=context_paths)
            
            # Update the entire conversation document
            self.collection.replace_one(
                {"_id": conversation_id},
                conversation.to_dict(),
                session=self.session
            )
            logger.info(f"Added message to conversation ID: {conversation_id}")
            return conversation
        except ConversationNotFoundError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Error adding message to conversation: {str(e)}")
            raise

    def get_conversation_by_id(
        self,
        conversation_id: ObjectId,
        skip_messages: int = 0,
        limit_messages: Optional[int] = None
    ) -> StepConversation:
        """
        Get a conversation by ID with optional message pagination.
        
        Args:
            conversation_id (ObjectId): MongoDB _id of the conversation
            skip_messages (int): Number of messages to skip
            limit_messages (Optional[int]): Maximum number of messages to return

        Raises:
            ConversationNotFoundError: If the conversation with the given ID is not found
        """
        try:
            data = self.collection.find_one(
                {"_id": conversation_id},
                session=self.session
            )
            if not data:
                logger.error(f"Conversation not found with ID: {conversation_id}")
                raise ConversationNotFoundError(f"Conversation with ID {conversation_id} not found")

            conversation = StepConversation.from_dict(data)
            # Apply message pagination if requested
            if skip_messages > 0 or limit_messages is not None:
                conversation.messages = conversation.get_messages(
                    skip=skip_messages,
                    limit=limit_messages
                )
            logger.info(f"Retrieved conversation ID: {conversation_id} with {len(conversation.messages)} messages")
            return conversation
        except ConversationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving conversation: {str(e)}")
            raise

    def get_conversations_by_step_name(
        self,
        step_name: str,
        page: int,
        page_size: int
    ) -> Dict[str, Any]:
        """Get paginated conversations by step name."""
        try:
            skip = (page - 1) * page_size
            
            cursor = self.collection.find(
                {"step_name": step_name},
                session=self.session
            ).sort("created_at", -1).skip(skip).limit(page_size)
            
            total_count = self.collection.count_documents(
                {"step_name": step_name},
                session=self.session
            )
            
            conversations = [StepConversation.from_dict(data) for data in cursor]
            
            return {
                "conversations": conversations,
                "total_conversations": total_count,
                "total_pages": (total_count + page_size - 1) // page_size,
                "current_page": page
            }
        except Exception as e:
            logger.error(f"Error retrieving conversations: {str(e)}")
            raise

    def get_all_conversations(self) -> List[StepConversation]:
        """
        Retrieve all conversations from the repository.
        
        Returns:
            List[StepConversation]: A list of all StepConversation instances.
        """
        try:
            data = self.collection.find({}, session=self.session)
            return [StepConversation.from_dict(item) for item in data]
        except Exception as e:
            logger.error(f"Error retrieving all conversations: {str(e)}")
            raise