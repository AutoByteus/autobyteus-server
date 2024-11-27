import os
import glob
import json
from datetime import datetime
from typing import List, Optional
import uuid
from autobyteus_server.workflow.persistence.conversation.persistence.provider import PersistenceProvider
from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation, ConversationHistory
import logging

logger = logging.getLogger(__name__)

class FileBasedPersistenceProvider(PersistenceProvider):
    def __init__(self):
        self.storage_dir = "conversation_data"
        os.makedirs(self.storage_dir, exist_ok=True)

    def create_conversation(self, step_name: str) -> StepConversation:
        """Create a new conversation file."""
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = ''.join(c if c.isalnum() else '_' for c in step_name)
        file_path = f"conversations/{safe_name}_{timestamp}.txt"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        open(file_path, 'a').close()
        conversation = StepConversation(
            step_conversation_id=conversation_id,
            step_name=step_name,
            created_at=datetime.utcnow(),
            messages=[],
            total_cost=0.0,
        )
        self._save_conversation(conversation)
        return conversation

    def store_message(
        self, 
        step_name: str, 
        role: str, 
        message: str, 
        original_content: Optional[str] = None,
        context_paths: Optional[List[str]] = None,
        conversation_id: Optional[str] = None,
        cost: float = 0.0
    ) -> StepConversation:
        """Store a message in the specified conversation and return the conversation."""
        if conversation_id:
            file_path = os.path.join(self.storage_dir, f"{conversation_id}.json")
            if not os.path.exists(file_path):
                conversation = self.create_conversation(step_name)
                file_path = os.path.join(self.storage_dir, f"{conversation.step_conversation_id}.json")
        else:
            conversation = self.create_conversation(step_name)
            file_path = os.path.join(self.storage_dir, f"{conversation.step_conversation_id}.json")

        # Read existing messages or initialize empty list
        try:
            with open(file_path, "r") as f:
                conversation_data = json.load(f)
                messages = conversation_data.get("messages", [])
        except (FileNotFoundError, json.JSONDecodeError):
            messages = []

        # Add new message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_message = {
            "timestamp": timestamp,
            "role": role,
            "message": message,
            "original_message": original_content,
            "context_paths": context_paths or [],
            "cost": cost
        }
        messages.append(new_message)

        # Save updated conversation data
        conversation_data = {
            "step_name": step_name,
            "created_at": messages[0]["timestamp"] if messages else timestamp,
            "messages": messages
        }
        with open(file_path, "w") as f:
            json.dump(conversation_data, f, indent=2)

        # Convert to domain model
        message_objects = [
            Message(
                role=msg["role"],
                message=msg["message"],
                timestamp=datetime.strptime(msg["timestamp"], "%Y-%m-%d %H:%M:%S"),
                original_message=msg.get("original_message"),
                context_paths=msg.get("context_paths", []),
                cost=msg.get("cost", 0.0)
            ) for msg in messages
        ]

        created_at = datetime.strptime(conversation_data["created_at"], "%Y-%m-%d %H:%M:%S")
        
        return StepConversation(
            step_conversation_id=conversation_id or os.path.splitext(os.path.basename(file_path))[0],
            step_name=step_name,
            created_at=created_at,
            messages=message_objects
        )

    def get_conversation_history(self, step_name: str, page: int = 1, page_size: int = 10) -> ConversationHistory:
        """
        Retrieve paginated conversations by step name.
        """
        # Look for conversation files in the storage directory
        all_files = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.storage_dir, filename), 'r') as f:
                        data = json.load(f)
                        if data.get('step_name') == step_name:
                            all_files.append((filename, data))
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # Sort by created_at timestamp, newest first
        all_files.sort(key=lambda x: x[1].get('created_at', ''), reverse=True)
        
        total_conversations = len(all_files)
        total_pages = (total_conversations + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_files = all_files[start_idx:end_idx]
        
        conversations = []
        for filename, data in page_files:
            try:
                messages = [
                    Message(
                        role=msg["role"],
                        message=msg["message"],
                        timestamp=datetime.strptime(msg["timestamp"], "%Y-%m-%d %H:%M:%S"),
                        original_message=msg.get("original_message"),
                        context_paths=msg.get("context_paths", []),
                        cost=msg.get("cost", 0.0)
                    ) for msg in data.get("messages", [])
                ]
                
                created_at = datetime.strptime(data["created_at"], "%Y-%m-%d %H:%M:%S")
                
                conversations.append(StepConversation(
                    step_conversation_id=os.path.splitext(filename)[0],
                    step_name=step_name,
                    created_at=created_at,
                    messages=messages,
                    total_cost=sum(msg.get("cost", 0.0) for msg in data.get("messages", []))
                ))
            except (KeyError, ValueError) as e:
                logger.error(f"Error processing conversation file {filename}: {str(e)}")
                continue
        
        return ConversationHistory(
            conversations=conversations,
            total_conversations=total_conversations,
            total_pages=total_pages,
            current_page=page
        )

    def get_total_cost(
        self,
        step_name: Optional[str],
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        """
        Calculate total cost of conversations within the given date range.
        """
        total_cost = 0.0
        for filename in os.listdir(self.storage_dir):
            if not filename.endswith('.json'):
                continue
            
            try:
                with open(os.path.join(self.storage_dir, filename), 'r') as f:
                    data = json.load(f)
                    
                    # Skip if step_name doesn't match (when specified)
                    if step_name and data.get('step_name') != step_name:
                        continue
                    
                    # Convert created_at string to datetime
                    created_at = datetime.strptime(data.get('created_at', ''), "%Y-%m-%d %H:%M:%S")
                    
                    # Check if conversation is within date range
                    if start_date <= created_at <= end_date:
                        # Sum up costs from all messages
                        conversation_cost = sum(
                            msg.get('cost', 0.0) 
                            for msg in data.get('messages', [])
                        )
                        total_cost += conversation_cost
                    
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.error(f"Error processing file {filename} for cost calculation: {str(e)}")
                continue
            
        return total_cost

    def _save_conversation(self, conversation: StepConversation):
        with open(
            os.path.join(self.storage_dir, f"{conversation.step_conversation_id}.json"), 'w'
        ) as f:
            json.dump(conversation.__dict__, f, default=str)

    def _load_conversation(self, conversation_id: str) -> Optional[StepConversation]:
        try:
            with open(
                os.path.join(self.storage_dir, f"{conversation_id}.json"), 'r'
            ) as f:
                data = json.load(f)
                return StepConversation(**data)
        except FileNotFoundError:
            return None