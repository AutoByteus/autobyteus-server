import strawberry
from datetime import datetime
from typing import List

from autobyteus_server.token_usage.provider.statistics_provider import TokenUsageStatisticsProvider
from autobyteus_server.api.graphql.types.token_usage_stats_types import UsageStatistics

@strawberry.type
class TokenUsageStatisticsQuery:
    @strawberry.field
    def total_cost_in_period(self, start_time: datetime, end_time: datetime) -> float:
        """
        Get the total cost of tokens in a specified time period.
        """
        stats_provider = TokenUsageStatisticsProvider()
        return stats_provider.get_total_cost(start_time, end_time)

    @strawberry.field
    def usage_statistics_in_period(self, start_time: datetime, end_time: datetime) -> List[UsageStatistics]:
        """
        Get usage statistics per LLM model within a specified time period.
        """
        stats_provider = TokenUsageStatisticsProvider()
        stats = stats_provider.get_statistics_per_model(start_time, end_time)
        return [
            UsageStatistics(
                llm_model=model,
                prompt_tokens=data.prompt_tokens,
                assistant_tokens=data.assistant_tokens,
                prompt_cost=data.prompt_token_cost,
                assistant_cost=data.assistant_token_cost,
                total_cost=data.total_cost
            ) for model, data in stats.items()
        ]
