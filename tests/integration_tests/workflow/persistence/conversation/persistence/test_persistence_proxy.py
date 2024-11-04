import pytest
import os
from unittest.mock import patch, MagicMock
from autobyteus_server.workflow.persistence.conversation.persistence.persistence_proxy import PersistenceProxy
from autobyteus_server.workflow.persistence.conversation.persistence.file_based_persistence_provider import FileBasedPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.persistence.mongo_persistence_provider import MongoPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.persistence.postgresql_persistence_provider import PostgresqlPersistenceProvider

@pytest.fixture
def persistence_proxy():
    return PersistenceProxy()

def test_default_provider_initialization(persistence_proxy):
    """Test that the default provider is FileBasedPersistenceProvider."""
    with patch.dict(os.environ, {}, clear=True):
        provider = persistence_proxy.provider
        assert isinstance(provider, FileBasedPersistenceProvider)

def test_mongodb_provider_initialization(persistence_proxy):
    """Test that MongoPersistenceProvider is initialized when specified."""
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "mongodb"}, clear=True):
        provider = persistence_proxy.provider
        assert isinstance(provider, MongoPersistenceProvider)

def test_postgresql_provider_initialization(persistence_proxy):
    """Test that PostgresqlPersistenceProvider is initialized when specified."""
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "postgresql"}, clear=True):
        provider = persistence_proxy.provider
        assert isinstance(provider, PostgresqlPersistenceProvider)

def test_unsupported_provider_fallback(persistence_proxy):
    """Test that unsupported provider raises ValueError."""
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "unsupported"}, clear=True):
        with patch('autobyteus_server.workflow.persistence.conversation.persistence.persistence_proxy.PersistenceProviderRegistry.get_provider_class') as mock_get_provider_class:
            mock_get_provider_class.return_value = None
            with pytest.raises(ValueError) as exc_info:
                _ = persistence_proxy.provider
            assert "Unsupported persistence provider" in str(exc_info.value)

def test_provider_initialization_failure_fallback(persistence_proxy):
    """Test that if provider initialization fails, it falls back to FileBasedPersistenceProvider."""
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "mongodb"}, clear=True):
        with patch.object(MongoPersistenceProvider, '__init__', side_effect=Exception("Initialization Failed")):
            with patch('autobyteus_server.workflow.persistence.conversation.persistence.persistence_proxy.FileBasedPersistenceProvider') as mock_file_provider:
                mock_file_provider.return_value = FileBasedPersistenceProvider()
                provider = persistence_proxy.provider
                assert isinstance(provider, FileBasedPersistenceProvider)

def test_create_conversation(persistence_proxy):
    """Test creating a conversation through the proxy."""
    with patch.object(FileBasedPersistenceProvider, 'create_conversation', return_value="mock_conversation") as mock_create:
        result = persistence_proxy.create_conversation("test_step")
        mock_create.assert_called_once_with("test_step")
        assert result == "mock_conversation"

def test_store_message(persistence_proxy):
    """Test storing a message through the proxy."""
    with patch.object(FileBasedPersistenceProvider, 'store_message') as mock_store:
        persistence_proxy.store_message("test_step", "user", "Hello")
        mock_store.assert_called_once_with("test_step", "user", "Hello", conversation_id=None)

def test_store_message_with_conversation_id(persistence_proxy):
    """Test storing a message with a specified conversation_id through the proxy."""
    with patch.object(FileBasedPersistenceProvider, 'store_message') as mock_store:
        persistence_proxy.store_message("test_step", "assistant", "Hi there!", conversation_id="mock_conversation_id")
        mock_store.assert_called_once_with("test_step", "assistant", "Hi there!", conversation_id="mock_conversation_id")

def test_get_conversation_history(persistence_proxy):
    """Test retrieving conversation history through the proxy."""
    mock_history = {"conversations": [], "total_conversations": 0, "total_pages": 0, "current_page": 1}
    with patch.object(FileBasedPersistenceProvider, 'get_conversation_history', return_value=mock_history) as mock_get_history:
        result = persistence_proxy.get_conversation_history("test_step", page=1, page_size=10)
        mock_get_history.assert_called_once_with("test_step", 1, 10)
        assert result == mock_history

def test_register_provider(persistence_proxy):
    """Test registering a new provider through the proxy."""
    class NewProvider:
        pass

    with patch.object(PersistenceProxy, 'provider', new_callable=MagicMock):
        persistence_proxy.register_provider("new_provider", NewProvider)
        registry = persistence_proxy._registry
        assert registry.get_provider_class("new_provider") == NewProvider