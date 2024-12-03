import logging
from datetime import datetime
from typing import List, Optional
from pymongo import MongoClient
from autobyteus_server.workflow.persistence.conversation.models.mongodb.cost_entry import CostEntry

logger = logging.getLogger(__name__)

class CostEntryRepository:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client['autobyteus']
        self.collection = self.db['cost_entries']

    def create_cost_entry(
        self,
        role: str,
        step_name: str,
        cost: float,
        timestamp: datetime,
        conversation_id: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> CostEntry:
        try:
            cost_entry = CostEntry(
                role=role,
                step_name=step_name,
                cost=cost,
                timestamp=timestamp,
                conversation_id=conversation_id,
                message_id=message_id
            )
            result = self.collection.insert_one(cost_entry.to_dict())
            cost_entry._id = result.inserted_id
            return cost_entry
        except Exception as e:
            logger.error(f"Error creating cost entry: {str(e)}")
            raise

    def get_total_cost(self, start_date: datetime, end_date: datetime, step_name: Optional[str] = None) -> float:
        try:
            query = {
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }
            if step_name:
                query["step_name"] = step_name
            pipeline = [
                {"$match": query},
                {"$group": {"_id": None, "total_cost": {"$sum": "$cost"}}}
            ]
            result = list(self.collection.aggregate(pipeline))
            total_cost = result[0]["total_cost"] if result else 0.0
            return total_cost
        except Exception as e:
            logger.error(f"Error calculating total cost: {str(e)}")
            raise

    def get_cost_entries(self, start_date: datetime, end_date: datetime, step_name: Optional[str] = None) -> List[CostEntry]:
        try:
            query = {
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }
            if step_name:
                query["step_name"] = step_name
            cursor = self.collection.find(query)
            return [CostEntry.from_dict(doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Error retrieving cost entries: {str(e)}")
            raise