
import logging
from bson import ObjectId
from repository_mongodb import BaseRepository
from typing import List
from datetime import datetime
from autobyteus_server.token_usage.models.mongodb.token_usage_record import MongoTokenUsageRecord

logger = logging.getLogger(__name__)

class MongoTokenUsageRecordRepository(BaseRepository[MongoTokenUsageRecord]):
    def create_token_usage_record(
        self,
        conversation_id: str,         # Updated parameter
        conversation_type: str,       # New parameter
        role: str,
        token_count: int,
        cost: float
    ) -> MongoTokenUsageRecord:
        """
        Create and insert a new token usage record.
        """
        try:
            record = MongoTokenUsageRecord(
                conversation_id=conversation_id,          # Updated field
                conversation_type=conversation_type,      # Initialize new attribute
                role=role,
                token_count=token_count,
                cost=cost
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

    def get_usage_records_by_conversation_type(self, conversation_type: str) -> List[MongoTokenUsageRecord]:
        """
        Retrieve all usage records by conversation type.
        """
        try:
            data = self.collection.find({"conversation_type": conversation_type}, session=self.session)
            return [MongoTokenUsageRecord.from_dict(doc) for doc in data]
        except Exception as e:
            logger.error(f"Error retrieving token usage records for conversation type {conversation_type}: {str(e)}")
            raise

    def get_all_usage_records(self, page: int, page_size: int) -> List[MongoTokenUsageRecord]:
        """
        Retrieve all usage records with pagination.
        """
        try:
            skip_count = (page - 1) * page_size
            cursor = self.collection.find().skip(skip_count).limit(page_size).sort("created_at", 1)
            return [MongoTokenUsageRecord.from_dict(doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Error retrieving all token usage records: {str(e)}")
            raise
