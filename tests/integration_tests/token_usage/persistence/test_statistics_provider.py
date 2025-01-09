import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from autobyteus_server.token_usage.provider.statistics_provider import TokenUsageStatisticsProvider
from autobyteus_server.token_usage.domain.token_usage_record import TokenUsageRecord
from autobyteus_server.token_usage.domain.token_usage_stats import TokenUsageStats

@patch("autobyteus_server.token_usage.provider.statistics_provider.PersistenceProxy")
def test_get_total_cost(mock_proxy_class):
    """
    Test the get_total_cost method to ensure it correctly retrieves
    the total cost from the PersistenceProxy.
    """
    mock_proxy_instance = mock_proxy_class.return_value
    mock_proxy_instance.get_total_cost_in_period.return_value = 15.75

    provider = TokenUsageStatisticsProvider()
    start = datetime(2023, 1, 1)
    end = datetime(2023, 1, 2)

    total_cost = provider.get_total_cost(start, end)

    mock_proxy_instance.get_total_cost_in_period.assert_called_once_with(start, end)
    assert total_cost == 15.75

@patch("autobyteus_server.token_usage.provider.statistics_provider.PersistenceProxy")
def test_get_statistics_per_model(mock_proxy_class):
    """
    Test the get_statistics_per_model method to ensure it correctly
    aggregates token usage stats by LLM model.
    """
    mock_proxy_instance = mock_proxy_class.return_value
    now = datetime.utcnow()

    usage_records = [
        TokenUsageRecord(
            conversation_id="conv1",
            conversation_type="WORKFLOW",
            role="user",
            token_count=10,
            cost=1.00,
            created_at=now,
            llm_model="gpt-3.5"
        ),
        TokenUsageRecord(
            conversation_id="conv2",
            conversation_type="WORKFLOW",
            role="assistant",
            token_count=5,
            cost=0.50,
            created_at=now,
            llm_model="gpt-3.5"
        ),
        TokenUsageRecord(
            conversation_id="conv3",
            conversation_type="WORKFLOW",
            role="assistant",
            token_count=20,
            cost=2.00,
            created_at=now,
            llm_model=None  # This should be counted under "unknown"
        )
    ]

    mock_proxy_instance.get_usage_records_in_period.return_value = usage_records

    provider = TokenUsageStatisticsProvider()
    start = now - timedelta(days=1)
    end = now + timedelta(days=1)

    stats = provider.get_statistics_per_model(start, end)
    mock_proxy_instance.get_usage_records_in_period.assert_called_once_with(start, end)

    # We expect two keys: 'gpt-3.5' and 'unknown'
    assert set(stats.keys()) == {"gpt-3.5", "unknown"}

    # Validate stats for 'gpt-3.5'
    gpt_stats = stats["gpt-3.5"]
    assert isinstance(gpt_stats, TokenUsageStats)
    assert gpt_stats.prompt_tokens == 10  # user
    assert gpt_stats.prompt_token_cost == 1.00
    assert gpt_stats.assistant_tokens == 5
    assert gpt_stats.assistant_token_cost == 0.50
    assert gpt_stats.total_cost == 1.50

    # Validate stats for 'unknown' (model=None)
    unknown_stats = stats["unknown"]
    assert isinstance(unknown_stats, TokenUsageStats)
    assert unknown_stats.prompt_tokens == 0
    assert unknown_stats.prompt_token_cost == 0.0
    assert unknown_stats.assistant_tokens == 20
    assert unknown_stats.assistant_token_cost == 2.00
    assert unknown_stats.total_cost == 2.00
