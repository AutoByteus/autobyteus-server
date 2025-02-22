import logging
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from repository_mongodb import BaseRepository
from autobyteus_server.prompt_engineering.models.mongodb.prompt import Prompt as MongoPrompt
from autobyteus_server.prompt_engineering.domain.models import Prompt as DomainPrompt

logger = logging.getLogger(__name__)

class MongoDBPromptRepository(BaseRepository[MongoPrompt]):
    def create_prompt(self, prompt: DomainPrompt) -> DomainPrompt:
        try:
            current_time = datetime.utcnow()
            mongo_prompt = MongoPrompt(
                name=prompt.name,
                category=prompt.category,
                prompt_text=prompt.prompt_text,
                created_at=current_time,
                updated_at=current_time,
                parent_id=prompt.parent_id,
                is_active=prompt.is_active
            )
            result = self.collection.insert_one(mongo_prompt.to_dict(), session=self.session)
            mongo_prompt._id = result.inserted_id
            prompt.id = str(mongo_prompt._id)
            return prompt
        except Exception as e:
            logger.error(f"Failed to create prompt: {str(e)}")
            raise

    def get_all_active_prompts(self) -> List[DomainPrompt]:
        try:
            data = self.collection.find({"is_active": True}, session=self.session)
            mongo_prompts = [MongoPrompt.from_dict(item) for item in data]
            return [DomainPrompt(
                id=str(p._id) if hasattr(p, "_id") else None,
                name=p.name,
                category=p.category,
                prompt_text=p.prompt_text,
                created_at=p.created_at,
                updated_at=p.updated_at,
                parent_id=p.parent_id,
                is_active=p.is_active
            ) for p in mongo_prompts]
        except Exception as e:
            logger.error(f"Failed to retrieve active prompts: {str(e)}")
            raise

    def update_prompt(self, prompt: DomainPrompt) -> DomainPrompt:
        try:
            update_fields = {
                "is_active": prompt.is_active,
                "updated_at": datetime.utcnow()
            }
            self.collection.update_one({"_id": prompt.id}, {"$set": update_fields}, session=self.session)
            return prompt
        except Exception as e:
            logger.error(f"Failed to update prompt: {str(e)}")
            raise

    def get_prompt_by_id(self, prompt_id: str) -> Optional[MongoPrompt]:
        try:
            data = self.collection.find_one({"_id": ObjectId(prompt_id)}, session=self.session)
            if data is None:
                return None
            mongo_prompt = MongoPrompt.from_dict(data)
            return mongo_prompt
        except Exception as e:
            logger.error(f"Failed to get prompt by id: {str(e)}")
            raise
