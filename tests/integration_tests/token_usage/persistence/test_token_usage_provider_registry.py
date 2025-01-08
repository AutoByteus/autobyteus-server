
import pytest
from autobyteus_server.token_usage.provider.provider_registry import TokenUsageProviderRegistry
from autobyteus_server.token_usage.provider.mongodb_persistence_provider import MongoPersistenceProvider
from autobyteus_server.token_usage.provider.sql_persistence_provider import SqlPersistenceProvider

@pytest.mark.integration
def test_initial_providers_registered():
    """
    Test that the default providers are registered in the token usage provider registry.
    """
    registry = TokenUsageProviderRegistry()
    available_providers = registry.get_available_providers()
    assert 'mongodb' in available_providers
    assert 'postgresql' in available_providers
    assert 'sqlite' in available_providers

def test_register_new_provider():
    """
    Test registering a new token usage provider in the registry.
    """
    class DummyTokenUsageProvider:
        pass

    registry = TokenUsageProviderRegistry()
    registry.register_provider('dummy', DummyTokenUsageProvider)
    available_providers = registry.get_available_providers()
    assert 'dummy' in available_providers
    assert registry.get_provider_class('dummy') == DummyTokenUsageProvider

def test_get_provider_class():
    """
    Test getting a provider class by name from the token usage provider registry.
    """
    registry = TokenUsageProviderRegistry()
    assert registry.get_provider_class('mongodb') == MongoPersistenceProvider
    assert registry.get_provider_class('postgresql') == SqlPersistenceProvider
    assert registry.get_provider_class('sqlite') == SqlPersistenceProvider
    assert registry.get_provider_class('nonexistent') is None

def test_get_available_providers():
    """
    Test retrieving the list of all available token usage providers.
    """
    registry = TokenUsageProviderRegistry()
    expected_providers = ['mongodb', 'postgresql', 'sqlite']
    assert set(registry.get_available_providers()) >= set(expected_providers)
