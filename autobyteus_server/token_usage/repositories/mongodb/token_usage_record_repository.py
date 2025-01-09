import logging
from bson import ObjectId
from repository_mongodb import BaseRepository
from typing import List, Optional
from datetime import datetime
from autobyteus_server.search.converters.mongo_search_query_converter import MongoSearchQueryConverter
from autobyteus_server.search.search_criteria import SearchCriterion
from autobyteus_server.token_usage.models.mongodb.token_usage_record import MongoTokenUsageRecord

logger = logging.getLogger(__name__)

class MongoTokenUsageRecordRepository(BaseRepository[MongoTokenUsageRecord]):
    def create_token_usage_record(
        self,
        conversation_id: str,
        conversation_type: str,
        role: str,
        token_count: int,
        cost: float,
        llm_model: Optional[str] = None
    ) -> MongoTokenUsageRecord:
        """
        Create and insert a new token usage record.
        """
        try:
            record = MongoTokenUsageRecord(
                conversation_id=conversation_id,
                conversation_type=conversation_type,
                role=role,
                token_count=token_count,
                cost=cost,
                llm_model=llm_model
            )
            result = self.collection.insert_one(record.to_dict(), session=self.session)
            record._id = result.inserted_id
            return record
        except Exception as e:
            logger.error(f"Error creating token usage record: {str(e)}")
            raise

    def get_usage_records_by_conversation_id(self, conversation_id: str) -> List[MongoTokenUsageRecord]:
        """
        Retrieve all usage records by conversation ID.
        """
        try:
            data = self.collection.find({"conversation_id": conversation_id}, session=self.session)
            return [MongoTokenUsageRecord.from_dict(doc) for doc in data]
        except Exception as e:
            logger.error(f"Error retrieving token usage records for conversation {conversation_id}: {str(e)}")
            raise

    def get_total_cost_in_period(self, start_date: datetime, end_date: datetime) -> float:
        """
        Returns the sum of costs in the specified time range.
        """
        try:
            cursor = self.collection.find({
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }, session=self.session)
            records = [MongoTokenUsageRecord.from_dict(doc) for doc in cursor]
            return sum(r.cost for r in records)
        except Exception as e:
            logger.error(f"Error calculating total cost in period: {str(e)}")
            raise

    def search_records(
        self,
        criteria: List[SearchCriterion]
    ) -> List[MongoTokenUsageRecord]:
        converter = MongoSearchQueryConverter(
            collection=self.collection,
            session=self.session,
            model_class=self.model
        )
        cursor = converter.apply_criteria(criteria)
        return [self.model.from_dict(doc) for doc in cursor]

    def get_usage_records_in_period(
        self,
        start_date: datetime,
        end_date: datetime,
        llm_model: Optional[str] = None
    ) -> List[MongoTokenUsageRecord]:
        """
        Retrieve usage records within a specified time range,
        optionally filtering by llm_model.
        """
        try:
            query = {
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            if llm_model:
                query["llm_model"] = llm_model
            data = self.collection.find(query, session=self.session)
            return [MongoTokenUsageRecord.from_dict(doc) for doc in data]
        except Exception as e:
            logger.error(f"Error retrieving token usage records in period: {str(e)}")
            raise
