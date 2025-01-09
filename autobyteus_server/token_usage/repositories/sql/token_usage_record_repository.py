from repository_sqlalchemy import BaseRepository
from typing import List, Optional
import logging
from autobyteus_server.token_usage.models.sql.token_usage_record import TokenUsageRecord
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

logger = logging.getLogger(__name__)

class TokenUsageRecordRepository(BaseRepository[TokenUsageRecord]):
    
    def create_usage_record(
        self,
        conversation_id: str,
        conversation_type: str,
        role: str,
        token_count: int,
        cost: float,
        llm_model: Optional[str] = None
    ) -> TokenUsageRecord:
        """
        Create a usage record entry with token counts and cost.
        """
        try:
            record = TokenUsageRecord(
                conversation_id=conversation_id,
                conversation_type=conversation_type,
                role=role,
                token_count=token_count,
                cost=cost,
                llm_model=llm_model
            )
            return self.create(record)
        except Exception as e:
            logger.error(f"Error creating usage record: {str(e)}")
            raise

    def get_usage_records_by_conversation_id(self, conversation_id: str) -> List[TokenUsageRecord]:
        """
        Retrieve usage records by conversation ID.
        """
        try:
            return self.session.query(self.model)\
                .filter_by(conversation_id=conversation_id)\
                .order_by(self.model.created_at)\
                .all()
        except Exception as e:
            logger.error(f"Error retrieving usage records for conversation {conversation_id}: {str(e)}")
            raise

    def get_total_cost_in_period(self, start_date, end_date) -> float:
        """
        Returns the sum of costs in the specified time range.
        """
        try:
            result = self.session.query(self.model).filter(
                self.model.created_at >= start_date,
                self.model.created_at <= end_date
            ).all()

            total_cost = sum(record.cost for record in result)
            return total_cost
        except Exception as e:
            logger.error(f"Error calculating total cost in period: {str(e)}")
            raise

    def get_usage_records_in_period(
        self,
        start_date: datetime,
        end_date: datetime,
        llm_model: Optional[str] = None
    ) -> List[TokenUsageRecord]:
        """
        Retrieve usage records within a specified time range,
        optionally filtering by llm_model.
        """
        try:
            query = self.session.query(self.model).filter(
                self.model.created_at >= start_date,
                self.model.created_at <= end_date
            )
            if llm_model:
                query = query.filter(self.model.llm_model == llm_model)
            return query.order_by(self.model.created_at).all()
        except Exception as e:
            logger.error(f"Error retrieving usage records in period: {str(e)}")
            raise
