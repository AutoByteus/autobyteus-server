from typing import TYPE_CHECKING, List, Optional, Dict, Any, Tuple
from abc import ABC
from autobyteus.prompt.prompt_template import PromptTemplate
from autobyteus_server.workflow.utils.unique_id_generator import UniqueIDGenerator
from autobyteus.llm.utils.llm_config import LLMConfig
from autobyteus.events.event_emitter import EventEmitter
from autobyteus_server.workflow.utils.prompt_template_manager import PromptTemplateManager
from autobyteus_server.workflow.persistence.conversation.provider.persistence_proxy import PersistenceProxy
from autobyteus.conversation.user_message import UserMessage
from autobyteus_server.workflow.runtime.workflow_agent_conversation_manager import WorkflowAgentConversationManager

if TYPE_CHECKING:
    from autobyteus_server.workflow.automated_coding_workflow import AutomatedCodingWorkflow

import os
import logging
from urllib.parse import urlparse

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
        self.agent_conversation_manager = WorkflowAgentConversationManager()

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
        context, image_file_paths, text_file_paths = self._construct_context(context_file_paths)

        if not conversation_id:
            # Start of a new conversation
            initial_prompt = self.construct_initial_prompt(requirement, context, llm_model)
            user_message = UserMessage(
                content=initial_prompt,
                file_paths=image_file_paths,
                original_requirement=requirement,
                context_file_paths=text_file_paths
            )

            agent_conversation = self.agent_conversation_manager.create_conversation(
                step_name=self.name,
                workspace_id=self.workflow.workspace.workspace_id,
                step_id=self.id,
                llm_model=llm_model,
                initial_message=user_message,
                tools=self.tools
            )
            conversation_id = agent_conversation.conversation_id

        else:
            # Continue existing conversation
            prompt = self.construct_subsequent_prompt(requirement, context)
            user_message = UserMessage(
                content=prompt,
                file_paths=image_file_paths,
                original_requirement=requirement,
                context_file_paths=text_file_paths
            )
            self.agent_conversation_manager.send_message(conversation_id, user_message)

        return conversation_id

    def _is_url(self, path: str) -> bool:
        """
        Check if a given path is a URL.

        Args:
            path (str): The path to check

        Returns:
            bool: True if the path is a URL, False otherwise
        """
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _construct_context(self, context_file_paths: List[Dict[str, str]]) -> Tuple[str, List[str], List[str]]:
        """
        Constructs context string, list of image paths, and list of text file paths from provided file paths.
        
        Note: For image files, the path can be either:
        1. A relative file path that will be joined with the workspace root path
        2. A complete URL to the image (e.g., from the /rest/files endpoint)

        Args:
            context_file_paths (List[Dict[str, str]]): List of context file paths or URLs

        Returns:
            Tuple[str, List[str], List[str]]: A tuple containing:
                - context: The constructed context string
                - image_file_paths: List of image file paths or URLs
                - text_file_paths: List of text file paths
        """
        context = ""
        image_file_paths = []
        text_file_paths = []
        root_path = self.workflow.workspace.root_path

        for file in context_file_paths:
            path = file['path']
            file_type = file['type']

            if file_type == 'image':
                # For images, keep URL as is, only join with root_path if it's a relative path
                if self._is_url(path):
                    image_file_paths.append(path)
                else:
                    full_path = os.path.join(root_path, path)
                    image_file_paths.append(full_path)
            elif file_type == 'text':
                full_path = os.path.join(root_path, path)
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context += f"File: {path}\n{content}\n\n"
                text_file_paths.append(full_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type} for file: {path}")

        return context, image_file_paths, text_file_paths

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
