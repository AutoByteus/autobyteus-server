import logging
from datetime import datetime
from autobyteus_server.prompt_engineering.domain.models import Prompt as DomainPrompt
from autobyteus_server.prompt_engineering.providers.persistence_proxy import PromptPersistenceProvider
from typing import List

logger = logging.getLogger(__name__)

class PromptService:
    def __init__(self):
        self.provider = PromptPersistenceProvider()

    def create_prompt(self, name: str, category: str, prompt_text: str) -> DomainPrompt:
        if not name or not category or not prompt_text:
            raise ValueError("Name, category, and prompt text are required")
        prompt = DomainPrompt(name=name, category=category, prompt_text=prompt_text, is_active=True)
        created_prompt = self.provider.create_prompt(prompt)
        logger.info(f"Prompt created successfully with ID: {created_prompt.id}")
        return created_prompt

    def get_all_active_prompts(self) -> List[DomainPrompt]:
        # Returns only active prompts from the underlying provider
        return self.provider.get_all_active_prompts()

    def update_prompt(self, prompt_id: str, new_prompt_text: str) -> DomainPrompt:
        all_prompts = self.provider.get_all_active_prompts()
        original_prompt = next((p for p in all_prompts if p.id == prompt_id), None)
        if not original_prompt:
            raise ValueError(f"Prompt with ID {prompt_id} not found")
        updated_prompt = DomainPrompt(
            name=original_prompt.name,
            category=original_prompt.category,
            prompt_text=new_prompt_text,
            parent_id=original_prompt.id,
            is_active=False  # New version is inactive by default
        )
        new_version = self.provider.create_prompt(updated_prompt)
        logger.info(f"Prompt updated successfully. New version ID: {new_version.id} linked to parent {original_prompt.id}")
        return new_version

    def mark_active_prompt(self, prompt_id: str) -> DomainPrompt:
        all_prompts = self.provider.get_all_active_prompts()
        target = next((p for p in all_prompts if p.id == prompt_id), None)
        if not target:
            raise ValueError(f"Prompt with ID {prompt_id} not found")
        for prompt in all_prompts:
            if (prompt.name == target.name and prompt.category == target.category 
                and prompt.id != target.id and prompt.is_active):
                prompt.is_active = False
                try:
                    self.provider.update_prompt(prompt)
                    logger.info(f"Prompt ID {prompt.id} deactivated.")
                except Exception as e:
                    logger.error(f"Failed to deactivate prompt ID {prompt.id}: {str(e)}")
        target.is_active = True
        updated_target = self.provider.update_prompt(target)
        logger.info(f"Prompt ID {target.id} is now marked as active.")
        return updated_target

    def get_prompt_by_id(self, prompt_id: str) -> DomainPrompt:
        return self.provider.get_prompt_by_id(prompt_id)
