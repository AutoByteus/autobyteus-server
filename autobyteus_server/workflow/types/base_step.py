from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from autobyteus.prompt.prompt_template import PromptTemplate
from autobyteus_server.workflow.types.base_workflow import BaseWorkflow
from autobyteus_server.workflow.utils.unique_id_generator import UniqueIDGenerator
from autobyteus.llm.models import LLMModel
from autobyteus.events.event_emitter import EventEmitter
from autobyteus_server.workflow.utils.prompt_template_manager import PromptTemplateManager

class BaseStep(ABC, EventEmitter):
    name: str

    def __init__(self, workflow: BaseWorkflow):
        super().__init__()
        self.id = UniqueIDGenerator.generate_id()
        self.workflow = workflow
        self.llm_model: Optional[LLMModel] = LLMModel.CLAUDE_3_5_SONNET
        self.prompt_template_manager = PromptTemplateManager()

    def load_prompt_templates(self, template_dir: str):
        """
        Load prompt templates from the specified directory.

        Args:
            template_dir (str): The directory containing the prompt template files.
        """
        self.prompt_template_manager.load_templates(template_dir, self.name)

    def configure_llm_model(self, llm_model: LLMModel):
        """
        Configure the LLM model for this step.
        
        Args:
            llm_model (LLMModel): The LLM model to be used for this step.
        """
        self.llm_model = llm_model

    def get_prompt_template(self, llm_model: LLMModel) -> Optional[PromptTemplate]:
        return self.prompt_template_manager.get_template(self.name, llm_model)

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
    def construct_initial_prompt(self, requirement: str, context: str) -> str:
        pass

    @abstractmethod
    async def process_requirement(
        self, 
        requirement: str, 
        context_file_paths: List[str],
        llm_model: Optional[LLMModel] = None
    ) -> None:
        pass

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "prompt_templates": self.get_prompt_templates_dict()
        }
    
    async def get_latest_response(self) -> Optional[str]:
        pass