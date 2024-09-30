from abc import ABC, abstractmethod
from typing import List, Optional
from autobyteus.prompt.prompt_template import PromptTemplate
from autobyteus_server.workflow.types.base_workflow import BaseWorkflow
from autobyteus_server.workflow.utils.unique_id_generator import UniqueIDGenerator
from autobyteus.llm.models import LLMModel
from autobyteus.events.event_emitter import EventEmitter

class BaseStep(ABC, EventEmitter):
    name: str
    prompt_template: PromptTemplate

    def __init__(self, workflow: BaseWorkflow):
        super().__init__()
        self.id = UniqueIDGenerator.generate_id()
        self.workflow = workflow
        self.llm_model: Optional[LLMModel] = LLMModel.CLAUDE_3_5_SONNET

    @classmethod
    def read_prompt_template(cls, template_path: str):
        with open(template_path, 'r') as file:
            template_content = file.read()
        cls.prompt_template = PromptTemplate(template=template_content)

    def configure_llm_model(self, llm_model: LLMModel):
        """
        Configure the LLM model for this step.
        
        Args:
            llm_model (LLMModel): The LLM model to be used for this step.
        """
        self.llm_model = llm_model

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
            "prompt_template": self.prompt_template.to_dict() if self.prompt_template else None
        }
    
    async def get_latest_response(self) -> Optional[str]:
        pass