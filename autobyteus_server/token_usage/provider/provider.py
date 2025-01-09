from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from autobyteus_server.token_usage.domain.token_usage_record import TokenUsageRecord

class PersistenceProvider(ABC):
    """
    Abstract base class for token usage persistence providers.
    """

    @abstractmethod
    def create_token_usage_record(
        self,
        conversation_id: str,
        conversation_type: str,
        role: str,
        token_count: int,
        cost: float,
        llm_model: Optional[str] = None
    ) -> TokenUsageRecord:
        pass

    @abstractmethod
    def get_total_cost_in_period(self, start_date: datetime, end_date: datetime) -> float:
        pass

    @abstractmethod
    def get_usage_records_in_period(
        self,
        start_date: datetime,
        end_date: datetime,
        llm_model: Optional[str] = None
    ) -> List[TokenUsageRecord]:
        pass
