
import pytest
import os
from unittest.mock import patch
from datetime import datetime, timedelta
from autobyteus_server.token_usage.provider.persistence_proxy import PersistenceProxy
from autobyteus_server.token_usage.provider.mongodb_persistence_provider import MongoPersistenceProvider
from autobyteus_server.token_usage.provider.sql_persistence_provider import SqlPersistenceProvider
from autobyteus_server.token_usage.domain.token_usage_record import TokenUsageRecord

@pytest.fixture
def token_usage_proxy():
    """
    Provides a PersistenceProxy instance for token usage.
    """
    return PersistenceProxy()

def test_default_provider_initialization(token_usage_proxy):
    """
    Test that the default provider is MongoPersistenceProvider if no environment variable is set.
    """
    with patch.dict(os.environ, {}, clear=True):
        provider = token_usage_proxy.provider
        assert isinstance(provider, MongoPersistenceProvider)

def test_mongodb_provider_initialization(token_usage_proxy):
    """
    Test that MongoPersistenceProvider is initialized when TOKEN_USAGE_PERSISTENCE_PROVIDER=mongodb.
    """
    with patch.dict(os.environ, {"TOKEN_USAGE_PERSISTENCE_PROVIDER": "mongodb"}, clear=True):
        provider = token_usage_proxy.provider
        assert isinstance(provider, MongoPersistenceProvider)

def test_sql_provider_initialization(token_usage_proxy):
    """
    Test that SqlPersistenceProvider is initialized when TOKEN_USAGE_PERSISTENCE_PROVIDER=postgresql or sqlite.
    """
    with patch.dict(os.environ, {"TOKEN_USAGE_PERSISTENCE_PROVIDER": "postgresql"}, clear=True):
        provider = token_usage_proxy.provider
        assert isinstance(provider, SqlPersistenceProvider)
    with patch.dict(os.environ, {"TOKEN_USAGE_PERSISTENCE_PROVIDER": "sqlite"}, clear=True):
        provider = token_usage_proxy.provider
        assert isinstance(provider, SqlPersistenceProvider)

def test_unsupported_provider_raises_error(token_usage_proxy):
    """
    Test that an unsupported provider raises a ValueError.
    """
    with patch.dict(os.environ, {"TOKEN_USAGE_PERSISTENCE_PROVIDER": "unsupported"}, clear=True):
        with patch('autobyteus_server.token_usage.persistence.persistence_proxy.TokenUsageProviderRegistry.get_provider_class') as mock_get_provider_class:
            mock_get_provider_class.return_value = None
            with pytest.raises(ValueError) as exc_info:
                _ = token_usage_proxy.provider
            assert "Unsupported token usage persistence provider" in str(exc_info.value)

def test_provider_initialization_failure(token_usage_proxy):
    """
    Test that if provider initialization fails, it raises the exception without fallback.
    """
    with patch.dict(os.environ, {"TOKEN_USAGE_PERSISTENCE_PROVIDER": "mongodb"}, clear=True):
        with patch.object(MongoPersistenceProvider, '__init__', side_effect=Exception("Initialization Failed")):
            with pytest.raises(Exception) as exc_info:
                _ = token_usage_proxy.provider
            assert "Initialization Failed" in str(exc_info.value)

def test_create_token_usage_record(token_usage_proxy):
    """
    Test creating a token usage record through the proxy.
    """
    with patch.object(MongoPersistenceProvider, 'create_token_usage_record', return_value="mock_record") as mock_create:
        result = token_usage_proxy.create_token_usage_record(
            conversation_id="proxy_test_conversation_id",
            conversation_type="WORKFLOW",
            role="user",
            token_count=10,
            cost=0.05
        )
        mock_create.assert_called_once_with(
            conversation_id="proxy_test_conversation_id",
            conversation_type="WORKFLOW",
            role="user",
            token_count=10,
            cost=0.05
        )
        assert result == "mock_record"

def test_get_token_usage_records(token_usage_proxy):
    """
    Test retrieving token usage records through the proxy.
    """
    mock_records = [TokenUsageRecord(
        token_usage_record_id="abc123",
        conversation_id="proxy_test_conversation_id",
        conversation_type="AI_TERMINAL",
        role="assistant",
        token_count=5,
        cost=0.001,
        created_at=datetime.utcnow()
    )]
    with patch.object(MongoPersistenceProvider, 'get_token_usage_records', return_value=mock_records) as mock_get_records:
        result = token_usage_proxy.get_token_usage_records(conversation_id="proxy_test_conversation_id")
        mock_get_records.assert_called_once_with(
            conversation_id="proxy_test_conversation_id",
            conversation_type=None
        )
        assert len(result) == 1
        assert result[0].conversation_id == "proxy_test_conversation_id"

def test_get_total_cost_in_period(token_usage_proxy):
    """
    Test calculating the total cost in a specified period through the proxy.
    """
    with patch.object(MongoPersistenceProvider, 'get_total_cost_in_period', return_value=1.234) as mock_get_cost:
        now = datetime.utcnow()
        earlier = now - timedelta(days=1)
        result = token_usage_proxy.get_total_cost_in_period(earlier, now)
        mock_get_cost.assert_called_once_with(earlier, now)
        assert result == 1.234

def test_register_provider(token_usage_proxy):
    """
    Test registering a new token usage provider through the proxy.
    """
    class NewTokenUsageProvider:
        pass

    with patch.object(token_usage_proxy, '_registry', autospec=True) as mock_registry:
        token_usage_proxy.register_provider("new_token_provider", NewTokenUsageProvider)
        mock_registry.register_provider.assert_called_once_with("new_token_provider", NewTokenUsageProvider)
