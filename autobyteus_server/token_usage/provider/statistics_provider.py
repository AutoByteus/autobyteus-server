from collections import defaultdict
from datetime import datetime
from typing import Dict, Any, List
from autobyteus.utils.singleton import SingletonMeta
from autobyteus_server.token_usage.provider.persistence_proxy import PersistenceProxy
from autobyteus_server.token_usage.domain.token_usage_record import TokenUsageRecord
from autobyteus_server.token_usage.domain.token_usage_stats import TokenUsageStats

class TokenUsageStatisticsProvider(metaclass=SingletonMeta):
    """
    Provides statistics on token usage using PersistenceProxy.
    """

    def __init__(self):
        self._proxy = PersistenceProxy()

    def get_total_cost(self, start_date: datetime, end_date: datetime) -> float:
        """
        Get the total cost of tokens used in the specified period.
        """
        return self._proxy.get_total_cost_in_period(start_date, end_date)

    def get_statistics_per_model(self, start_date: datetime, end_date: datetime) -> Dict[str, TokenUsageStats]:
        """
        Get total prompt tokens, assistant tokens, and total cost per LLM model in the specified period.
        Returns a dictionary keyed by llm_model with corresponding statistics.
        """
        # Retrieve all usage records in the period regardless of model (filtering later)
        records: List[TokenUsageRecord] = self._proxy.get_usage_records_in_period(start_date, end_date)

        stats: Dict[str, TokenUsageStats] = defaultdict(TokenUsageStats)

        for record in records:
            # Use 'unknown' as key if llm_model is None
            model_key = record.llm_model or "unknown"
            current_stats = stats[model_key]

            if record.role == "user":
                current_stats.prompt_tokens += record.token_count
                current_stats.prompt_token_cost += record.cost
            elif record.role == "assistant":
                current_stats.assistant_tokens += record.token_count
                current_stats.assistant_token_cost += record.cost

            current_stats.total_cost += record.cost

        return dict(stats)
