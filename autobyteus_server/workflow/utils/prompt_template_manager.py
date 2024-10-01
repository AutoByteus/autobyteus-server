import os
from typing import Dict, Optional
from autobyteus.prompt.prompt_template import PromptTemplate
from autobyteus.llm.models import LLMModel

class PromptTemplateManager:
    def __init__(self):
        self.templates: Dict[str, Dict[str, PromptTemplate]] = {}

    def load_templates(self, template_dir: str, step_name: str) -> None:
        step_template_file = os.path.join(template_dir, f"{step_name}.prompt")
        if os.path.exists(step_template_file):
            with open(step_template_file, 'r') as file:
                template_content = file.read()
            if step_name not in self.templates:
                self.templates[step_name] = {}
            self.templates[step_name]['default'] = PromptTemplate(template=template_content)

        # Load model-specific templates if they exist
        for model_name in os.listdir(template_dir):
            model_template_file = os.path.join(template_dir, model_name, f"{step_name}.prompt")
            if os.path.exists(model_template_file):
                with open(model_template_file, 'r') as file:
                    template_content = file.read()
                if step_name not in self.templates:
                    self.templates[step_name] = {}
                self.templates[step_name][model_name.lower()] = PromptTemplate(template=template_content)

    def get_template(self, step_name: str, llm_model: LLMModel) -> Optional[PromptTemplate]:
        if step_name not in self.templates:
            return None

        model_name = llm_model.name.lower()
        
        # Remove '-api' suffix if present
        if model_name.endswith('-api'):
            model_name = model_name[:-4]
        
        return self.templates[step_name].get(model_name, self.templates[step_name].get('default'))