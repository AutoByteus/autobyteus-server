from autobyteus_server.prompt_engineering.domain.models import Prompt as DomainPrompt
from autobyteus_server.prompt_engineering.models.sql.prompt import Prompt as SQLPrompt

class SQLConverter:
    @staticmethod
    def to_domain_prompt(sql_prompt: SQLPrompt) -> DomainPrompt:
        return DomainPrompt(
            id=str(sql_prompt.id) if sql_prompt.id is not None else None,
            name=sql_prompt.name,
            category=sql_prompt.category,
            prompt_text=sql_prompt.prompt_text,
            created_at=sql_prompt.created_at,
            updated_at=sql_prompt.updated_at,
            parent_id=str(sql_prompt.parent_id) if sql_prompt.parent_id is not None else None,
            is_active=sql_prompt.is_active
        )

    @staticmethod
    def to_sql_prompt(domain_prompt: DomainPrompt) -> SQLPrompt:
        return SQLPrompt(
            name=domain_prompt.name,
            category=domain_prompt.category,
            prompt_text=domain_prompt.prompt_text,
            created_at=domain_prompt.created_at,
            updated_at=domain_prompt.updated_at,
            parent_id=int(domain_prompt.parent_id) if domain_prompt.parent_id is not None else None,
            is_active=domain_prompt.is_active
        )
