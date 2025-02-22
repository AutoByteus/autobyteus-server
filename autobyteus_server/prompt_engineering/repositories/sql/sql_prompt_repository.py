import logging
from datetime import datetime
from typing import List, Optional
from repository_sqlalchemy import BaseRepository
from autobyteus_server.prompt_engineering.models.sql.prompt import Prompt as SQLPrompt
from autobyteus_server.prompt_engineering.domain.models import Prompt as DomainPrompt

logger = logging.getLogger(__name__)

class SQLPromptRepository(BaseRepository[SQLPrompt]):
    def create_prompt(self, prompt: SQLPrompt) -> SQLPrompt:
        try:
            # Directly use the SQLPrompt instance provided
            created_prompt = self.create(prompt)
            prompt.id = created_prompt.id
            return prompt
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to create prompt: {str(e)}")
            raise

    def get_all_active_prompts(self) -> List[SQLPrompt]:
        try:
            sql_prompts = self.session.query(SQLPrompt).filter(SQLPrompt.is_active == True).all()
            return sql_prompts
        except Exception as e:
            logger.error(f"Failed to retrieve active prompts: {str(e)}")
            raise

    def update_prompt(self, prompt: DomainPrompt) -> DomainPrompt:
        try:
            if prompt.id is None:
                raise ValueError("Prompt ID is required for update")
            sql_prompt = self.find_by_id(int(prompt.id))
            if not sql_prompt:
                raise ValueError("Prompt not found")
            update_data = {
                "is_active": prompt.is_active,
                "updated_at": datetime.utcnow()
            }
            updated_sql_prompt = self.update(sql_prompt, update_data)
            return DomainPrompt(
                id=str(updated_sql_prompt.id),
                name=updated_sql_prompt.name,
                category=updated_sql_prompt.category,
                prompt_text=updated_sql_prompt.prompt_text,
                created_at=updated_sql_prompt.created_at,
                updated_at=updated_sql_prompt.updated_at,
                parent_id=str(updated_sql_prompt.parent_id) if updated_sql_prompt.parent_id is not None else None,
                is_active=updated_sql_prompt.is_active
            )
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to update prompt: {str(e)}")
            raise

    def get_prompt_by_id(self, prompt_id: str) -> Optional[SQLPrompt]:
        try:
            sql_prompt = self.find_by_id(int(prompt_id))
            return sql_prompt
        except Exception as e:
            logger.error(f"Failed to get prompt by id: {str(e)}")
            raise
