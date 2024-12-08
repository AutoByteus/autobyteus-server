import os
import logging
from typing import List, Optional, Dict, Tuple
from autobyteus_server.workflow.runtime.workflow_step_streaming_conversation_manager import WorkflowStepStreamingConversationManager
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus.conversation.user_message import UserMessage

logger = logging.getLogger(__name__)

class SubtaskImplementationStep(BaseStep):
    name = "implementation"

    def __init__(self, workflow):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_dir = os.path.join(current_dir, "prompt")
        super().__init__(workflow, prompt_dir)
        self.tools = []
        self.streaming_conversation_manager = WorkflowStepStreamingConversationManager()

    def construct_initial_prompt(self, requirement: str, context: str, llm_model: str) -> str:
        prompt_template = self.get_prompt_template(llm_model)
        return prompt_template.fill({
            "requirement": requirement,
            "context": context
        })

    def construct_subsequent_prompt(self, requirement: str, context: str) -> str:
        prompt = ""
        if context:
            prompt += f"[Context]\n{context}\n\n"
        prompt += f"{requirement}"
        return prompt
    
    async def process_requirement(
        self, 
        requirement: str, 
        context_file_paths: List[Dict[str, str]],  
        llm_model: Optional[str],
        conversation_id: Optional[str] = None
    ) -> str:
        context, image_file_paths = self._construct_context(context_file_paths)

        if not conversation_id:
            # Start of a new conversation
            initial_prompt = self.construct_initial_prompt(requirement, context, llm_model)
            user_message = UserMessage(content=initial_prompt, file_paths=image_file_paths)
            
            new_conversation = self.persistence_proxy.store_message(
                step_name=self.name,
                role='user',
                message=initial_prompt,
                original_message=requirement,
                context_paths=[file['path'] for file in context_file_paths]
            )
            conversation_id = new_conversation.step_conversation_id

            self.streaming_conversation_manager.create_conversation(
                conversation_id=conversation_id,
                step_name=self.name,
                workspace_id=self.workflow.workspace.id,
                step_id=self.id,
                llm_model=llm_model,
                initial_message=user_message,
                tools=self.tools
            )

            return conversation_id
        else:
            # Continue existing conversation
            prompt = self.construct_subsequent_prompt(requirement, context)
            await self.streaming_conversation_manager.send_message(conversation_id, prompt)

            self.persistence_proxy.store_message(
                step_name=self.name,
                role='user',
                message=prompt,
                original_message=requirement,
                context_paths=[file['path'] for file in context_file_paths],
                conversation_id=conversation_id
            )

            return conversation_id

    def _construct_context(self, context_file_paths: List[Dict[str, str]]) -> Tuple[str, List[str]]:
        """Constructs context string and list of image paths from provided file paths."""
        context = ""
        image_file_paths = []
        root_path = self.workflow.workspace.root_path
        
        for file in context_file_paths:
            path = file['path']
            file_type = file['type']
            full_path = os.path.join(root_path, path)

            if file_type == 'image':
                image_file_paths.append(full_path)
            elif file_type == 'text':
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context += f"File: {path}\n{content}\n\n"
            else:
                raise ValueError(f"Unsupported file type: {file_type} for file: {path}")

        return context, image_file_paths

    def close_conversation(self, conversation_id: str) -> None:
        """Closes a conversation and cleans up associated resources."""
        try:
            self.streaming_conversation_manager.close_conversation(conversation_id)
        except Exception as e:
            raise Exception(f"Failed to close conversation {conversation_id}: {str(e)}")