import os
import glob
import json
from datetime import datetime
from typing import List, Optional
from autobyteus_server.workflow.persistence.conversation.persistence.provider import PersistenceProvider
from autobyteus_server.workflow.persistence.conversation.domain.models import Message, StepConversation, ConversationHistory

class FileBasedPersistenceProvider(PersistenceProvider):
    def __init__(self):
        super().__init__()

    def create_conversation(self, step_name: str) -> StepConversation:
        """Create a new conversation file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = ''.join(c if c.isalnum() else '_' for c in step_name)
        file_path = f"conversations/{safe_name}_{timestamp}.txt"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        open(file_path, 'a').close()  # Create empty file
        
        return StepConversation(
            step_conversation_id=file_path,
            step_name=step_name,
            created_at=datetime.now(),
            messages=[]
        )

    def store_message(
        self, 
        step_name: str, 
        role: str, 
        message: str, 
        original_content: Optional[str] = None,  # Use original_content in domain model
        context_paths: Optional[List[str]] = None,
        conversation_id: Optional[str] = None  # New parameter
    ) -> StepConversation:
        """Store a message in the specified conversation and return the conversation."""
        if conversation_id:
            file_path = conversation_id
        else:
            # Create a new conversation if conversation_id is not provided
            conversation = self.create_conversation(step_name)
            file_path = conversation.step_conversation_id

        with open(file_path, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message_data = {
                "timestamp": timestamp,
                "role": role,
                "message": message,
                "original_message": original_content,      # Map original_content to original_message in DB
                "context_paths": context_paths
            }
            f.write(json.dumps(message_data) + "\n")
        
        # Retrieve updated conversation
        messages = []
        with open(file_path, "r") as f:
            for line in f:
                data = json.loads(line.strip())
                messages.append(Message(
                    role=data["role"],
                    message=data["message"],  # Mapped message
                    timestamp=datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S"),
                    original_message=data.get("original_message"),  # Mapped original_message from DB to original_message in domain
                    context_paths=data.get("context_paths", [])
                ))
        
        file_timestamp = datetime.strptime(
            os.path.basename(file_path).split('_')[1].split('.')[0],
            "%Y%m%d_%H%M%S"
        )
        
        return StepConversation(
            step_conversation_id=file_path,
            step_name=step_name,
            created_at=file_timestamp,
            messages=messages
        )

    def get_conversation_history(self, step_name: str, page: int = 1, page_size: int = 10) -> ConversationHistory:
        """
        Retrieve paginated conversations by step name.
        """
        safe_name = ''.join(c if c.isalnum() else '_' for c in step_name)
        pattern = f"conversations/{safe_name}_*.txt"
        all_files = sorted(glob.glob(pattern), reverse=True)
        
        total_conversations = len(all_files)
        total_pages = (total_conversations + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_files = all_files[start_idx:end_idx]
        
        conversations = []
        for file_path in page_files:
            if os.path.exists(file_path):
                messages = []
                with open(file_path, "r") as f:
                    for line in f:
                        data = json.loads(line.strip())
                        messages.append(Message(
                            role=data["role"],
                            message=data["message"],  # Mapped message
                            timestamp=datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S"),
                            original_message=data.get("original_message"),  # Mapped original_message from DB to original_message in domain
                            context_paths=data.get("context_paths", [])
                        ))
                
                file_timestamp = datetime.strptime(
                    os.path.basename(file_path).split('_')[1].split('.')[0],
                    "%Y%m%d_%H%M%S"
                )
                
                conversations.append(StepConversation(
                    step_conversation_id=file_path,
                    step_name=step_name,
                    created_at=file_timestamp,
                    messages=messages
                ))
        
        return ConversationHistory(
            conversations=conversations,
            total_conversations=total_conversations,
            total_pages=total_pages,
            current_page=page
        )