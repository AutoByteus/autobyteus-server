
import pytest
import os
from unittest.mock import patch, MagicMock
from autobyteus_server.workflow.persistence.conversation.provider.persistence_proxy import PersistenceProxy
from autobyteus_server.workflow.persistence.conversation.provider.mongo_persistence_provider import MongoPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.provider.sql_persistence_provider import SqlPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.domain.models import ConversationHistory

@pytest.fixture
def persistence_proxy():
    return PersistenceProxy()

def test_default_provider_initialization(persistence_proxy):
    """Test that the default provider is MongoPersistenceProvider."""
    with patch.dict(os.environ, {}, clear=True):
        provider = persistence_proxy.provider
        assert isinstance(provider, MongoPersistenceProvider)

def test_mongodb_provider_initialization(persistence_proxy):
    """Test that MongoPersistenceProvider is initialized when specified."""
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "mongodb"}, clear=True):
        provider = persistence_proxy.provider
        assert isinstance(provider, MongoPersistenceProvider)

def test_sql_provider_initialization(persistence_proxy):
    """Test that SqlPersistenceProvider is initialized when specified."""
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "postgresql"}, clear=True):
        provider = persistence_proxy.provider
        assert isinstance(provider, SqlPersistenceProvider)
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "sqlite"}, clear=True):
        provider = persistence_proxy.provider
        assert isinstance(provider, SqlPersistenceProvider)

def test_unsupported_provider_raises_error(persistence_proxy):
    """Test that unsupported provider raises ValueError."""
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "unsupported"}, clear=True):
        with patch('autobyteus_server.workflow.persistence.conversation.provider.persistence_proxy.PersistenceProviderRegistry.get_provider_class') as mock_get_provider_class:
            mock_get_provider_class.return_value = None
            with pytest.raises(ValueError) as exc_info:
                _ = persistence_proxy.provider
            assert "Unsupported persistence provider" in str(exc_info.value)

def test_provider_initialization_failure(persistence_proxy):
    """Test that if provider initialization fails, it raises the exception without fallback."""
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "mongodb"}, clear=True):
        with patch.object(MongoPersistenceProvider, '__init__', side_effect=Exception("Initialization Failed")):
            with pytest.raises(Exception) as exc_info:
                _ = persistence_proxy.provider
            assert "Initialization Failed" in str(exc_info.value)

def test_create_conversation(persistence_proxy):
    """Test creating a conversation through the proxy."""
    with patch.object(MongoPersistenceProvider, 'create_conversation', return_value="mock_conversation") as mock_create:
        result = persistence_proxy.create_conversation("test_step")
        mock_create.assert_called_once_with("test_step")
        assert result == "mock_conversation"

def test_store_message(persistence_proxy):
    """Test storing a message through the proxy."""
    with patch.object(MongoPersistenceProvider, 'store_message', return_value="mock_conversation") as mock_store:
        result = persistence_proxy.store_message("test_step", "user", "Hello", token_count=10, cost=0.05)
        mock_store.assert_called_once_with(
            "test_step",
            "user",
            "Hello",
            token_count=10,
            cost=0.05,
            original_message=None,
            context_paths=None,
            conversation_id=None
        )
        assert result == "mock_conversation"

def test_store_message_with_conversation_id(persistence_proxy):
    """Test storing a message with a specified conversation_id through the proxy."""
    with patch.object(MongoPersistenceProvider, 'store_message', return_value="mock_conversation") as mock_store:
        result = persistence_proxy.store_message(
            "test_step",
            "assistant",
            "Hi there!",
            token_count=5,
            cost=0.02,
            conversation_id="mock_conversation_id"
        )
        mock_store.assert_called_once_with(
            "test_step",
            "assistant",
            "Hi there!",
            token_count=5,
            cost=0.02,
            original_message=None,
            context_paths=None,
            conversation_id="mock_conversation_id"
        )
        assert result == "mock_conversation"

def test_get_conversation_history(persistence_proxy):
    """Test retrieving conversation history through the proxy."""
    mock_history = ConversationHistory(conversations=[], total_conversations=0, total_pages=0, current_page=1)
    with patch.object(MongoPersistenceProvider, 'get_conversation_history', return_value=mock_history) as mock_get_history:
        result = persistence_proxy.get_conversation_history("test_step", page=1, page_size=10)
        mock_get_history.assert_called_once_with("test_step", 1, 10)
        assert result == mock_history

def test_register_provider(persistence_proxy):
    """Test registering a new provider through the proxy."""
    class NewProvider:
        pass

    with patch.object(PersistenceProxy, '_registry', autospec=True) as mock_registry:
        persistence_proxy.register_provider("new_provider", NewProvider)
        mock_registry.register_provider.assert_called_once_with("new_provider", NewProvider)
        # Ensure provider instance is reset
        assert persistence_proxy._provider is None

def test_update_last_user_message_usage_through_proxy(persistence_proxy):
    """Test updating the last user message usage through the proxy."""
    with patch.object(MongoPersistenceProvider, 'update_last_user_message_usage', return_value="updated_conversation") as mock_update:
        result = persistence_proxy.update_last_user_message_usage(
            step_conversation_id="mock_conversation_id",
            token_count=25,
            cost=0.025
        )
        mock_update.assert_called_once_with(
            "mock_conversation_id",
            25,
            0.025
        )
        assert result == "updated_conversation"

def test_update_last_user_message_usage_proxy_error(persistence_proxy):
    """Test that errors during updating last user message usage are propagated through the proxy."""
    with patch.object(MongoPersistenceProvider, 'update_last_user_message_usage', side_effect=ValueError("Invalid update")):
        with pytest.raises(ValueError) as exc_info:
            persistence_proxy.update_last_user_message_usage(
                step_conversation_id="invalid_id",
                token_count=10,
                cost=0.01
            )
        assert "Invalid update" in str(exc_info.value)
