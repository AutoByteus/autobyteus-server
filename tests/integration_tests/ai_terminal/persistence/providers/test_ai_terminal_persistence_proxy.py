
import pytest
import os
from unittest.mock import patch
from datetime import datetime
from autobyteus_server.ai_terminal.persistence.providers.ai_terminal_persistence_proxy import AiTerminalPersistenceProxy
from autobyteus_server.ai_terminal.persistence.providers.mongo_ai_terminal_provider import MongoAiTerminalProvider
from autobyteus_server.ai_terminal.persistence.providers.sql_ai_terminal_provider import SqlAiTerminalProvider
from autobyteus_server.ai_terminal.persistence.domain.models import AiTerminalConversation

pytestmark = pytest.mark.integration

@pytest.fixture
def ai_terminal_persistence_proxy():
    """
    Provides an AiTerminalPersistenceProxy instance for testing.
    """
    return AiTerminalPersistenceProxy()

def test_default_provider_initialization(ai_terminal_persistence_proxy):
    """
    Test that the default provider is MongoAiTerminalProvider if no environment variable is set.
    """
    with patch.dict(os.environ, {}, clear=True):
        provider = ai_terminal_persistence_proxy.provider
        assert isinstance(provider, MongoAiTerminalProvider)

def test_mongodb_provider_initialization(ai_terminal_persistence_proxy):
    """
    Test that MongoAiTerminalProvider is initialized when PERSISTENCE_PROVIDER=mongodb.
    """
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "mongodb"}, clear=True):
        provider = ai_terminal_persistence_proxy.provider
        assert isinstance(provider, MongoAiTerminalProvider)

def test_sql_provider_initialization(ai_terminal_persistence_proxy):
    """
    Test that SqlAiTerminalProvider is initialized when PERSISTENCE_PROVIDER=postgresql or sqlite.
    """
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "postgresql"}, clear=True):
        provider = ai_terminal_persistence_proxy.provider
        assert isinstance(provider, SqlAiTerminalProvider)
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "sqlite"}, clear=True):
        provider = ai_terminal_persistence_proxy.provider
        assert isinstance(provider, SqlAiTerminalProvider)

def test_unsupported_provider_raises_error(ai_terminal_persistence_proxy):
    """
    Test that an unsupported provider raises a ValueError.
    """
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "unsupported"}, clear=True):
        with patch('autobyteus_server.ai_terminal.persistence.providers.ai_terminal_provider_registry.AiTerminalProviderRegistry.get_provider_class') as mock_get_class:
            mock_get_class.return_value = None
            with pytest.raises(ValueError) as exc_info:
                _ = ai_terminal_persistence_proxy.provider
            assert "Unsupported AI Terminal persistence provider" in str(exc_info.value)

def test_provider_initialization_failure(ai_terminal_persistence_proxy):
    """
    Test that if provider initialization fails, it raises the exception without fallback.
    """
    with patch.dict(os.environ, {"PERSISTENCE_PROVIDER": "mongodb"}, clear=True):
        with patch.object(MongoAiTerminalProvider, '__init__', side_effect=Exception("Initialization Failed")):
            with pytest.raises(Exception) as exc_info:
                _ = ai_terminal_persistence_proxy.provider
            assert "Initialization Failed" in str(exc_info.value)

def test_create_conversation(ai_terminal_persistence_proxy):
    """
    Test creating a conversation through AiTerminalPersistenceProxy.
    """
    with patch.object(MongoAiTerminalProvider, 'create_conversation', return_value="mock_conversation") as mock_create:
        result = ai_terminal_persistence_proxy.create_conversation()
        mock_create.assert_called_once()
        assert result == "mock_conversation"

def test_store_message(ai_terminal_persistence_proxy):
    """
    Test storing a message through AiTerminalPersistenceProxy.
    """
    mock_conversation = AiTerminalConversation(conversation_id="mock_id", created_at=datetime.utcnow(), messages=[])
    with patch.object(MongoAiTerminalProvider, 'store_message', return_value=mock_conversation) as mock_store:
        result = ai_terminal_persistence_proxy.store_message(
            conversation_id="mock_id",
            role="user",
            message="Test message",
            token_count=5,
            cost=0.001
        )
        mock_store.assert_called_once_with(
            conversation_id="mock_id",
            role="user",
            message="Test message",
            token_count=5,
            cost=0.001
        )
        assert result.conversation_id == "mock_id"

def test_get_conversation_history(ai_terminal_persistence_proxy):
    """
    Test retrieving conversation history through AiTerminalPersistenceProxy.
    """
    mock_conversation = AiTerminalConversation(conversation_id="mock_id", created_at=datetime.utcnow(), messages=[])
    with patch.object(MongoAiTerminalProvider, 'get_conversation_history', return_value=mock_conversation) as mock_history:
        result = ai_terminal_persistence_proxy.get_conversation_history("mock_id")
        mock_history.assert_called_once_with("mock_id")
        assert result.conversation_id == "mock_id"

def test_list_conversations(ai_terminal_persistence_proxy):
    """
    Test listing conversations through AiTerminalPersistenceProxy.
    """
    with patch.object(MongoAiTerminalProvider, 'list_conversations', return_value="mock_history") as mock_list:
        result = ai_terminal_persistence_proxy.list_conversations(page=2, page_size=5)
        mock_list.assert_called_once_with(page=2, page_size=5)
        assert result == "mock_history"
