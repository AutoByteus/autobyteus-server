import os
from typing import Dict, Optional
from autobyteus.prompt.prompt_template import PromptTemplate

class PromptTemplateManager:
    DEFAULT_FALLBACK_PROMPT_TEMPLATE = "claude_3_5_sonnet"

    def __init__(self):
        self.templates: Dict[str, Dict[str, PromptTemplate]] = {}

    def get_template(self, step_name: str, llm_model: str, prompt_dir: str) -> Optional[PromptTemplate]:
        """
        Get the prompt template for the given step and LLM model.

        If the template for the specified model is not found, it will try to use the default
        fallback prompt template (currently set to CLAUDE_3_5_SONNET). If that's also not 
        available, it will fall back to the 'default' template.

        Templates are loaded on-demand when requested.

        Args:
            step_name (str): The name of the step.
            llm_model (str): The LLM model name (enum name).
            prompt_dir (str): The directory where prompt templates are stored.

        Returns:
            Optional[PromptTemplate]: The prompt template if found, None otherwise.
        """
        model_name = self._process_model_name(llm_model)

        # Try to get or load the template for the specified model
        template = self._get_or_load_template(step_name, model_name, prompt_dir)

        # If not found, try to get or load the default fallback prompt template
        if template is None:
            fallback_model_name = self.DEFAULT_FALLBACK_PROMPT_TEMPLATE
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

    def _process_model_name(self, model_name: str) -> str:
        """
        Process the input model name by removing the '_API' or '_RPA' suffix and converting to lowercase.

        Args:
            model_name (str): The input model name (enum name).

        Returns:
            str: The processed model name.
        """
        if model_name.endswith('_API') or model_name.endswith('_RPA'):
            model_name = model_name[:-4]
        return model_name.lower()