from repository_sqlalchemy import BaseRepository
from autobyteus_server.workflow.persistence.conversation.models.sql.cost_entry import CostEntry
from datetime import datetime
from typing import List
import logging
from sqlalchemy import func

logger = logging.getLogger(__name__)

class CostEntryRepository(BaseRepository[CostEntry]):
    def __init__(self, session):
        super().__init__(session)

    def create_cost_entry(
        self,
        role: str,
        step_name: str,
        cost: float,
        timestamp: datetime,
        conversation_id: int = None,
        message_id: int = None
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
            return self.create(cost_entry)
        except Exception as e:
            logger.error(f"Error creating cost entry: {str(e)}")
            raise

    def get_total_cost(self, start_date: datetime, end_date: datetime, step_name: str = None) -> float:
        try:
            query = self.session.query(func.sum(self.model.cost)).filter(
                self.model.timestamp >= start_date,
                self.model.timestamp <= end_date
            )
            if step_name:
                query = query.filter(self.model.step_name == step_name)
            total_cost = query.scalar() or 0.0
            return total_cost
        except Exception as e:
            logger.error(f"Error calculating total cost: {str(e)}")
            raise

    def get_cost_entries(self, start_date: datetime, end_date: datetime, step_name: str = None) -> List[CostEntry]:
        try:
            query = self.session.query(self.model).filter(
                self.model.timestamp >= start_date,
                self.model.timestamp <= end_date
            )
            if step_name:
                query = query.filter(self.model.step_name == step_name)
            return query.all()
        except Exception as e:
            logger.error(f"Error retrieving cost entries: {str(e)}")
            raise