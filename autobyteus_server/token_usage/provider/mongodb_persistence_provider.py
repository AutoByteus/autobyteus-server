
from datetime import datetime
import logging
from typing import Any, List, Optional

from autobyteus_server.token_usage.models.sql.token_usage_record import TokenUsageRecord
from autobyteus_server.token_usage.provider.provider import PersistenceProvider
from autobyteus_server.token_usage.repositories.mongodb.token_usage_record_repository import (
    MongoTokenUsageRecordRepository
)
from autobyteus_server.token_usage.converters.mongodb_converter import MongoDBConverter

logger = logging.getLogger(__name__)

class MongoPersistenceProvider(PersistenceProvider):
    def __init__(self):
        super().__init__()
        self.record_repository = MongoTokenUsageRecordRepository()
        self.converter = MongoDBConverter()

    def create_token_usage_record(
        self,
        conversation_id: str,
        conversation_type: str,
        role: str,
        token_count: int,
        cost: float
    ) -> TokenUsageRecord:
        """
        Create and store a new token usage record.
        """
        try:
            domain_record = TokenUsageRecord(
                conversation_id=conversation_id,
                conversation_type=conversation_type,
                role=role,
                token_count=token_count,
                cost=cost,
                created_at=None  # Let the model handle the default
            )
            mongo_record = self.converter.to_mongo_model(domain_record)
            created_record = self.record_repository.create_token_usage_record(
                conversation_id=mongo_record.conversation_id,
                conversation_type=mongo_record.conversation_type,
                role=mongo_record.role,
                token_count=mongo_record.token_count,
                cost=mongo_record.cost
            )
            return self.converter.to_domain_model(created_record)
        except Exception as e:
            logger.error(f"Failed to create token usage record: {str(e)}")
            raise

    def get_token_usage_records(
        self,
        conversation_id: Optional[str] = None,
        conversation_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> List[TokenUsageRecord]:
        """
        Retrieve token usage records with optional filtering and pagination.
        """
        try:
            if conversation_id:
                mongo_records = self.record_repository.get_usage_records_by_conversation_id(conversation_id)
            elif conversation_type:
                # Assuming there's a method to get by conversation_type
                mongo_records = self.record_repository.get_usage_records_by_conversation_type(conversation_type)
            else:
                mongo_records = self.record_repository.get_all_usage_records(page, page_size)
            return self.converter.to_domain_models(mongo_records)
        except Exception as e:
            logger.error(f"Failed to retrieve token usage records: {str(e)}")
            raise

    def get_total_cost_in_period(self, start_date: datetime, end_date: datetime) -> float:
        """
        Retrieve the total cost of token usage within a specified period.
        """
        try:
            return self.record_repository.get_total_cost_in_period(start_date, end_date)
        except Exception as e:
            logger.error(f"Failed to calculate total cost in period: {str(e)}")
            raise
