import pytest
from autobyteus_server.workflow.persistence.conversation.persistence.provider_registry import PersistenceProviderRegistry
from autobyteus_server.workflow.persistence.conversation.persistence.file_based_persistence_provider import FileBasedPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.persistence.mongo_persistence_provider import MongoPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.persistence.sql_persistence_provider import SqlPersistenceProvider

@pytest.mark.integration
def test_initial_providers_registered():
    registry = PersistenceProviderRegistry()
    available_providers = registry.get_available_providers()
    assert 'file' in available_providers
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
    assert registry.get_provider_class('file') == FileBasedPersistenceProvider
    assert registry.get_provider_class('mongodb') == MongoPersistenceProvider
    assert registry.get_provider_class('postgresql') == SqlPersistenceProvider
    assert registry.get_provider_class('sqlite') == SqlPersistenceProvider
    assert registry.get_provider_class('nonexistent') is None

def test_get_available_providers():
    registry = PersistenceProviderRegistry()
    expected_providers = ['file', 'mongodb', 'postgresql', 'sqlite']
    assert set(registry.get_available_providers()) >= set(expected_providers)