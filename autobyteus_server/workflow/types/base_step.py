from typing import TYPE_CHECKING, List, Optional, Dict, Type
from abc import ABC, abstractmethod
from autobyteus.prompt.prompt_template import PromptTemplate
from autobyteus_server.workflow.utils.unique_id_generator import UniqueIDGenerator
from autobyteus.llm.utils.llm_config import LLMConfig
from autobyteus.events.event_emitter import EventEmitter
from autobyteus_server.workflow.utils.prompt_template_manager import PromptTemplateManager
from autobyteus_server.workflow.persistence.conversation.persistence.persistence_proxy import PersistenceProxy

if TYPE_CHECKING:
    from autobyteus_server.workflow.automated_coding_workflow import AutomatedCodingWorkflow

class BaseStep(ABC, EventEmitter):
    name: str
    def __init__(self, step_id: str):
        self.step_id = step_id

    def __init__(self, workflow: 'AutomatedCodingWorkflow', prompt_dir: str):
        super().__init__()
        self.id = UniqueIDGenerator.generate_id()
        self.workflow = workflow
        self.llm_model: Optional[str] = None
        self.prompt_template_manager = PromptTemplateManager()
        self.prompt_dir = prompt_dir
        self.persistence_proxy = PersistenceProxy()

    def configure_llm_model(self, llm_model: str):
        """
        Configure the LLM model for this step.

        Args:
            llm_model (str): The LLM model to be used for this step.
        """
        self.llm_model = llm_model

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

    @abstractmethod
    def construct_initial_prompt(self, requirement: str, context: str, llm_model: str) -> str:
        pass

    @abstractmethod
    async def process_requirement(
        self,
        requirement: str,
        context_files: List[Dict[str, str]],
        llm_model_name: Optional[str],
        conversation_id: Optional[str],
    ) -> str:
        pass
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "prompt_templates": self.get_prompt_templates_dict()
        }
    
    async def get_latest_response(self) -> Optional[str]:
        pass

    def close_conversation(self, conversation_id: str) -> None:
        """
        Close a specific conversation and clean up its resources.
        This method should be overridden by steps that maintain conversation state.
        
        Args:
            conversation_id (str): The ID of the conversation to close
        """
        pass