
import pytest
from autobyteus_server.workflow.persistence.conversation.provider.provider_registry import PersistenceProviderRegistry
from autobyteus_server.workflow.persistence.conversation.provider.mongo_persistence_provider import MongoPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.provider.sql_persistence_provider import SqlPersistenceProvider

@pytest.mark.integration
def test_initial_providers_registered():
    registry = PersistenceProviderRegistry()
    available_providers = registry.get_available_providers()
    assert 'mongodb' in available_providers
    assert 'postgresql' in available_providers
    assert 'sqlite' in available_providers  # Ensure SQLite is registered

def test_register_new_provider():
    class DummyPersistenceProvider:
        pass

    registry = PersistenceProviderRegistry()
    registry.register_provider('dummy', DummyPersistenceProvider)
    available_providers = registry.get_available_providers()
    assert 'dummy' in available_providers
    assert registry.get_provider_class('dummy') == DummyPersistenceProvider

def test_get_provider_class():
    registry = PersistenceProviderRegistry()
    assert registry.get_provider_class('mongodb') == MongoPersistenceProvider
    assert registry.get_provider_class('postgresql') == SqlPersistenceProvider
    assert registry.get_provider_class('sqlite') == SqlPersistenceProvider
    assert registry.get_provider_class('nonexistent') is None

def test_get_available_providers():
    registry = PersistenceProviderRegistry()
    expected_providers = ['mongodb', 'postgresql', 'sqlite']
    assert set(registry.get_available_providers()) >= set(expected_providers)
