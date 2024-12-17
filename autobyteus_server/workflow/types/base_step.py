from typing import TYPE_CHECKING, List, Optional, Dict, Any, Tuple
from abc import ABC
from autobyteus.prompt.prompt_template import PromptTemplate
from autobyteus_server.workflow.utils.unique_id_generator import UniqueIDGenerator
from autobyteus.llm.utils.llm_config import LLMConfig
from autobyteus.events.event_emitter import EventEmitter
from autobyteus_server.workflow.utils.prompt_template_manager import PromptTemplateManager
from autobyteus_server.workflow.persistence.conversation.persistence.persistence_proxy import PersistenceProxy
from autobyteus.conversation.user_message import UserMessage
from autobyteus_server.workflow.runtime.step_agent_conversation_manager import StepAgentConversationManager

if TYPE_CHECKING:
    from autobyteus_server.workflow.automated_coding_workflow import AutomatedCodingWorkflow

import os
import logging

logger = logging.getLogger(__name__)

class BaseStep(ABC, EventEmitter):
    name: str

    def __init__(self, workflow: 'AutomatedCodingWorkflow', prompt_dir: str):
        super().__init__()
        self.id = UniqueIDGenerator.generate_id()
        self.workflow = workflow
        self.prompt_template_manager = PromptTemplateManager()
        self.prompt_dir = prompt_dir
        self.persistence_proxy = PersistenceProxy()
        self.tools = []
        self.agent_conversation_manager = StepAgentConversationManager()

    def get_prompt_template(self, llm_model: str) -> Optional[PromptTemplate]:
        return self.prompt_template_manager.get_template(self.name, llm_model, self.prompt_dir)

    def get_prompt_templates_dict(self) -> Dict[str, Optional[Dict]]:
        """
        Create a nested dictionary of prompt templates for this step.

        Returns:
            Dict[str, Optional[Dict]]: A dictionary where keys are model names and values are
            dictionaries representing the prompt templates, or None if no templates exist for this step.
        """
        step_templates = self.prompt_template_manager.templates.get(self.name, {})
        return {
            model_name: template.to_dict() if template else None
            for model_name, template in step_templates.items()
        }

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
        """
        Process a requirement either as a new conversation or as part of an existing one.
        
        Args:
            requirement (str): The requirement to process
            context_file_paths (List[Dict[str, str]]): List of context file paths
            llm_model (Optional[str]): The LLM model to use
            conversation_id (Optional[str]): Existing conversation ID if continuing a conversation
            
        Returns:
            str: The conversation ID
        """
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

            self.agent_conversation_manager.create_conversation(
                conversation_id=conversation_id,
                step_name=self.name,
                workspace_id=self.workflow.workspace.workspace_id,
                step_id=self.id,
                llm_model=llm_model,
                initial_message=user_message,
                tools=self.tools
            )
        else:
            # Continue existing conversation
            prompt = self.construct_subsequent_prompt(requirement, context)
            self.agent_conversation_manager.send_message(conversation_id, prompt)

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
            self.agent_conversation_manager.close_conversation(conversation_id)
        except Exception as e:
            raise Exception(f"Failed to close conversation {conversation_id}: {str(e)}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "prompt_templates": self.get_prompt_templates_dict()
        }