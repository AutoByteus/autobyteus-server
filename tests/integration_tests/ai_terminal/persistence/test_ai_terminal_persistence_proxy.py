
import pytest
import os
from unittest.mock import patch, MagicMock
from autobyteus_server.ai_terminal.persistence.providers.ai_terminal_persistence_proxy import AiTerminalPersistenceProxy
from autobyteus_server.ai_terminal.persistence.providers.mongo_ai_terminal_provider import MongoAiTerminalProvider
from autobyteus_server.ai_terminal.persistence.providers.sql_ai_terminal_provider import SqlAiTerminalProvider
from autobyteus_server.ai_terminal.persistence.domain.models import AiTerminalConversation, ConversationHistory

@pytest.fixture
def persistence_proxy():
    return AiTerminalPersistenceProxy()

def test_default_provider_initialization(persistence_proxy):
    """Test that the default provider is MongoAiTerminalProvider when no env var is set."""
    with patch.dict(os.environ, {}, clear=True):
        provider = persistence_proxy.provider
        assert isinstance(provider, MongoAiTerminalProvider)

def test_mongodb_provider_initialization(persistence_proxy):
    """Test that MongoAiTerminalProvider is initialized when MONGODB is specified."""
    with patch.dict(os.environ, {"AI_TERMINAL_PERSISTENCE_PROVIDER": "mongodb"}, clear=True):
        provider = persistence_proxy.provider
        assert isinstance(provider, MongoAiTerminalProvider)

def test_sql_provider_initialization_postgresql(persistence_proxy):
    """Test that SqlAiTerminalProvider is initialized when POSTGRESQL is specified."""
    with patch.dict(os.environ, {"AI_TERMINAL_PERSISTENCE_PROVIDER": "postgresql"}, clear=True):
        provider = persistence_proxy.provider
        assert isinstance(provider, SqlAiTerminalProvider)

def test_sql_provider_initialization_sqlite(persistence_proxy):
    """Test that SqlAiTerminalProvider is initialized when SQLITE is specified."""
    with patch.dict(os.environ, {"AI_TERMINAL_PERSISTENCE_PROVIDER": "sqlite"}, clear=True):
        provider = persistence_proxy.provider
        assert isinstance(provider, SqlAiTerminalProvider)

def test_unsupported_provider_raises_error(persistence_proxy):
    """Test that unsupported provider raises ValueError."""
    with patch.dict(os.environ, {"AI_TERMINAL_PERSISTENCE_PROVIDER": "unsupported"}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            _ = persistence_proxy.provider
        assert "Unsupported AI Terminal persistence provider" in str(exc_info.value)

def test_create_conversation(persistence_proxy):
    """Test creating a conversation through the proxy."""
    with patch.object(MongoAiTerminalProvider, 'create_conversation', return_value="mock_conversation") as mock_create:
        result = persistence_proxy.create_conversation()
        mock_create.assert_called_once()
        assert result == "mock_conversation"

def test_store_message(persistence_proxy):
    """Test storing a message through the proxy."""
    with patch.object(MongoAiTerminalProvider, 'store_message', return_value="updated_conversation") as mock_store:
        result = persistence_proxy.store_message("test_id", "user", "Hello Proxy!")
        mock_store.assert_called_once_with(
            conversation_id="test_id",
            role="user",
            message="Hello Proxy!",
            token_count=None,
            cost=None
        )
        assert result == "updated_conversation"

def test_get_conversation_history(persistence_proxy):
    """Test retrieving conversation history through the proxy."""
    mock_history = AiTerminalConversation(
        conversation_id="test_id",
        created_at=None,
        messages=[]
    )
    with patch.object(MongoAiTerminalProvider, 'get_conversation_history', return_value=mock_history) as mock_get_history:
        result = persistence_proxy.get_conversation_history("test_id")
        mock_get_history.assert_called_once_with("test_id")
        assert result == mock_history

def test_list_conversations(persistence_proxy):
    """Test listing conversations through the proxy."""
    mock_history = ConversationHistory(conversations=[], total_conversations=0, total_pages=0, current_page=1)
    with patch.object(MongoAiTerminalProvider, 'list_conversations', return_value=mock_history) as mock_list:
        result = persistence_proxy.list_conversations(page=2, page_size=5)
        mock_list.assert_called_once_with(page=2, page_size=5)
        assert result == mock_history
