from autobyteus_server.prompt_engineering.repositories.mongodb.mongodb_prompt_repository import MongoDBPromptRepository
from autobyteus_server.prompt_engineering.converters.mongodb_converter import MongoDBConverter
from autobyteus_server.prompt_engineering.domain.models import Prompt as DomainPrompt
from typing import List

class MongoDBProvider:
    def __init__(self):
        self.repository = MongoDBPromptRepository()
        self.converter = MongoDBConverter()

    def create_prompt(self, prompt: DomainPrompt) -> DomainPrompt:
        mongo_prompt = self.converter.to_mongo_prompt(prompt)
        created_mongo_prompt = self.repository.create_prompt(mongo_prompt)
        return self.converter.to_domain_prompt(created_mongo_prompt)

    def get_all_prompts(self) -> List[DomainPrompt]:
        mongo_prompts = self.repository.get_all_prompts()
        return [self.converter.to_domain_prompt(p) for p in mongo_prompts]

    def update_prompt(self, prompt: DomainPrompt) -> DomainPrompt:
        updated = self.repository.update_prompt(prompt)
        return self.converter.to_domain_prompt(updated)
    
    def get_prompt_by_id(self, prompt_id: str) -> DomainPrompt:
        mongo_prompt = self.repository.get_prompt_by_id(prompt_id)
        if not mongo_prompt:
            raise ValueError("Prompt not found")
        return self.converter.to_domain_prompt(mongo_prompt)
