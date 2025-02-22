from autobyteus_server.prompt_engineering.repositories.sql.sql_prompt_repository import SQLPromptRepository
from autobyteus_server.prompt_engineering.converters.sql_converter import SQLConverter
from autobyteus_server.prompt_engineering.domain.models import Prompt as DomainPrompt
from typing import List

class SQLProvider:
    def __init__(self):
        self.repository = SQLPromptRepository()
        self.converter = SQLConverter()

    def create_prompt(self, prompt: DomainPrompt) -> DomainPrompt:
        sql_prompt = self.converter.to_sql_prompt(prompt)
        created_sql_prompt = self.repository.create_prompt(sql_prompt)
        return self.converter.to_domain_prompt(created_sql_prompt)

    def get_all_active_prompts(self) -> List[DomainPrompt]:
        sql_prompts = self.repository.get_all_active_prompts()
        return [self.converter.to_domain_prompt(p) for p in sql_prompts]

    def update_prompt(self, prompt: DomainPrompt) -> DomainPrompt:
        updated = self.repository.update_prompt(prompt)
        return self.converter.to_domain_prompt(updated)
    
    def get_prompt_by_id(self, prompt_id: str) -> DomainPrompt:
        sql_prompt = self.repository.get_prompt_by_id(prompt_id)
        if not sql_prompt:
            raise ValueError("Prompt not found")
        return self.converter.to_domain_prompt(sql_prompt)
