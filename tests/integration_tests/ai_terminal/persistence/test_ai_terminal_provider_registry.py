
import pytest
from autobyteus_server.ai_terminal.persistence.providers.ai_terminal_provider_registry import AiTerminalProviderRegistry
from autobyteus_server.ai_terminal.persistence.providers.mongo_ai_terminal_provider import MongoAiTerminalProvider
from autobyteus_server.ai_terminal.persistence.providers.sql_ai_terminal_provider import SqlAiTerminalProvider

def test_initial_providers_registered():
    registry = AiTerminalProviderRegistry()
    available = registry.get_available_providers()
    assert 'mongodb' in available
    assert 'postgresql' in available
    assert 'sqlite' in available

def test_register_new_provider():
    class DummyProvider:
        pass

    registry = AiTerminalProviderRegistry()
    registry.register_provider('dummy', DummyProvider)
    available = registry.get_available_providers()
    assert 'dummy' in available
    assert registry.get_provider_class('dummy') == DummyProvider

def test_get_provider_class():
    registry = AiTerminalProviderRegistry()
    assert registry.get_provider_class('mongodb') == MongoAiTerminalProvider
    assert registry.get_provider_class('postgresql') == SqlAiTerminalProvider
    assert registry.get_provider_class('sqlite') == SqlAiTerminalProvider
    assert registry.get_provider_class('nonexistent') is None
