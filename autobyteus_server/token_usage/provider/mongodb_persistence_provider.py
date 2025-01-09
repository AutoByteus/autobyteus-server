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
        cost: float,
        llm_model: Optional[str] = None
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
                created_at=None,
                llm_model=llm_model
            )
            mongo_record = self.converter.to_mongo_model(domain_record)
            created_record = self.record_repository.create_token_usage_record(
                conversation_id=mongo_record.conversation_id,
                conversation_type=mongo_record.conversation_type,
                role=mongo_record.role,
                token_count=mongo_record.token_count,
                cost=mongo_record.cost,
                llm_model=mongo_record.llm_model
            )
            return self.converter.to_domain_model(created_record)
        except Exception as e:
            logger.error(f"Failed to create token usage record: {str(e)}")
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

    def get_usage_records_in_period(
        self,
        start_date: datetime,
        end_date: datetime,
        llm_model: Optional[str] = None
    ) -> List[TokenUsageRecord]:
        """
        Retrieve token usage records within a specified time period,
        optionally filtered by llm_model.
        """
        try:
            mongo_records = self.record_repository.get_usage_records_in_period(start_date, end_date, llm_model)
            return self.converter.to_domain_models(mongo_records)
        except Exception as e:
            logger.error(f"Failed to retrieve token usage records in period: {str(e)}")
            raise
