from autobyteus_server.prompt_engineering.domain.models import Prompt as DomainPrompt
from autobyteus_server.prompt_engineering.models.mongodb.prompt import Prompt as MongoPrompt

class MongoDBConverter:
    @staticmethod
    def to_domain_prompt(mongo_prompt: MongoPrompt) -> DomainPrompt:
        return DomainPrompt(
            id=str(mongo_prompt._id) if hasattr(mongo_prompt, "_id") else None,
            name=mongo_prompt.name,
            category=mongo_prompt.category,
            prompt_text=mongo_prompt.prompt_text,
            created_at=mongo_prompt.created_at,
            updated_at=mongo_prompt.updated_at,
            parent_id=mongo_prompt.parent_id,
            is_active=mongo_prompt.is_active
        )

    @staticmethod
    def to_mongo_prompt(domain_prompt: DomainPrompt) -> MongoPrompt:
        return MongoPrompt(
            name=domain_prompt.name,
            category=domain_prompt.category,
            prompt_text=domain_prompt.prompt_text,
            created_at=domain_prompt.created_at,
            updated_at=domain_prompt.updated_at,
            parent_id=domain_prompt.parent_id,
            is_active=domain_prompt.is_active
        )
