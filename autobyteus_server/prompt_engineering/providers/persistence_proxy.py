import os
from typing import List
from autobyteus_server.prompt_engineering.providers.mongodb_provider import MongoDBProvider
from autobyteus_server.prompt_engineering.providers.sql_provider import SQLProvider
from autobyteus_server.prompt_engineering.domain.models import Prompt as DomainPrompt

class PromptPersistenceProvider:
    def __init__(self):
        provider_type = os.getenv('PERSISTENCE_PROVIDER', 'mongodb').lower()
        if provider_type == 'mongodb':
            self.provider = MongoDBProvider()
        elif provider_type in ['postgresql', 'sqlite']:
            self.provider = SQLProvider()
        else:
            raise ValueError(f"Unsupported persistence provider: {provider_type}")

    def create_prompt(self, prompt: DomainPrompt) -> DomainPrompt:
        return self.provider.create_prompt(prompt)

    def get_all_active_prompts(self) -> List[DomainPrompt]:
        return self.provider.get_all_active_prompts()

    def update_prompt(self, prompt: DomainPrompt) -> DomainPrompt:
        return self.provider.update_prompt(prompt)
    
    def get_prompt_by_id(self, prompt_id: str) -> DomainPrompt:
        return self.provider.get_prompt_by_id(prompt_id)
