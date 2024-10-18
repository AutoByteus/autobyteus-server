import os
from typing import Dict, Optional
from autobyteus.prompt.prompt_template import PromptTemplate
from autobyteus.llm.models import LLMModel

class PromptTemplateManager:
    DEFAULT_FALLBACK_PROMPT_TEMPLATE = LLMModel.CLAUDE_3_5_SONNET.name

    def __init__(self):
        self.templates: Dict[str, Dict[str, PromptTemplate]] = {}

    def get_template(self, step_name: str, llm_model: LLMModel, prompt_dir: str) -> Optional[PromptTemplate]:
        """
        Get the prompt template for the given step and LLM model.

        If the template for the specified model is not found, it will try to use the default
        fallback prompt template (currently set to CLAUDE_3_5_SONNET). If that's also not 
        available, it will fall back to the 'default' template.

        Templates are loaded on-demand when requested.

        Args:
            step_name (str): The name of the step.
            llm_model (LLMModel): The LLM model.
            prompt_dir (str): The directory where prompt templates are stored.

        Returns:
            Optional[PromptTemplate]: The prompt template if found, None otherwise.
        """
        model_name = llm_model.name.lower()

        # Remove '-api' suffix if present
        if model_name.endswith('-api'):
            model_name = model_name[:-4]

        # Try to get or load the template for the specified model
        template = self._get_or_load_template(step_name, model_name, prompt_dir)

        # If not found, try to get or load the default fallback prompt template
        if template is None:
            fallback_model_name = self.DEFAULT_FALLBACK_PROMPT_TEMPLATE.lower()
            template = self._get_or_load_template(step_name, fallback_model_name, prompt_dir)

        # If still not found, fall back to the 'default' template
        if template is None:
            template = self._get_or_load_template(step_name, 'default', prompt_dir)

        return template

    def _get_or_load_template(self, step_name: str, model_name: str, prompt_dir: str) -> Optional[PromptTemplate]:
        """
        Get a template from the cache or load it if not present.

        Args:
            step_name (str): The name of the step.
            model_name (str): The name of the model.
            prompt_dir (str): The directory where prompt templates are stored.

        Returns:
            Optional[PromptTemplate]: The prompt template if found or loaded, None otherwise.
        """
        if step_name not in self.templates:
            self.templates[step_name] = {}

        if model_name not in self.templates[step_name]:
            template = self._load_template(step_name, model_name, prompt_dir)
            if template:
                self.templates[step_name][model_name] = template

        return self.templates[step_name].get(model_name)

    def _load_template(self, step_name: str, model_name: str, prompt_dir: str) -> Optional[PromptTemplate]:
        """
        Load a template from file.

        Args:
            step_name (str): The name of the step.
            model_name (str): The name of the model.
            prompt_dir (str): The directory where prompt templates are stored.

        Returns:
            Optional[PromptTemplate]: The loaded prompt template if file exists, None otherwise.
        """
        if model_name == 'default':
            template_file = os.path.join(prompt_dir, f"{step_name}.prompt")
        else:
            template_file = os.path.join(prompt_dir, model_name, f"{step_name}.prompt")

        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as file:
                template_content = file.read()
            return PromptTemplate(template=template_content)

        return None