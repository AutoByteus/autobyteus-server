import pytest
from datetime import datetime
import logging

from autobyteus_server.prompt_engineering.domain.models import Prompt as DomainPrompt
from autobyteus_server.prompt_engineering.repositories.sql.sql_prompt_repository import SQLPromptRepository

logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def sql_prompt_repository():
    """
    Provides a SQLPromptRepository instance for integration tests.
    The test setup runs each test in a transaction, so no manual deletion is necessary.
    """
    repo = SQLPromptRepository()
    return repo

def test_create_prompt_success(sql_prompt_repository):
    """
    Test the creation of a prompt using SQLPromptRepository.
    """
    domain_prompt = DomainPrompt(
        name="Integration Test Prompt",
        category="Integration",
        prompt_text="This is a prompt for integration testing.",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_prompt = sql_prompt_repository.create_prompt(domain_prompt)
    assert created_prompt is not None, "Created prompt should not be None"
    assert created_prompt.name == domain_prompt.name, "Prompt name should match"
    assert created_prompt.category == domain_prompt.category, "Prompt category should match"
    assert created_prompt.prompt_text == domain_prompt.prompt_text, "Prompt text should match"
    # Check that an id was assigned
    assert created_prompt.id is not None, "ID should be assigned"

def test_get_all_prompts_empty(sql_prompt_repository):
    """
    Test that get_all_active_prompts returns an empty list when no prompts exist.
    """
    prompts = sql_prompt_repository.get_all_active_prompts()
    assert isinstance(prompts, list), "get_all_active_prompts should return a list"
    assert len(prompts) == 0, "Prompt list should be empty initially"

def test_get_all_prompts_after_creation(sql_prompt_repository):
    """
    Test that get_all_active_prompts returns all created prompts.
    """
    prompts_to_create = [
        DomainPrompt(name="Prompt A", category="CatA", prompt_text="Text A"),
        DomainPrompt(name="Prompt B", category="CatB", prompt_text="Text B"),
        DomainPrompt(name="Prompt C", category="CatC", prompt_text="Text C")
    ]
    created_prompts = []
    for prompt in prompts_to_create:
        created = sql_prompt_repository.create_prompt(prompt)
        created_prompts.append(created)
    
    retrieved_prompts = sql_prompt_repository.get_all_active_prompts()
    assert len(retrieved_prompts) == len(created_prompts), "Number of retrieved prompts should match created prompts"
    retrieved_names = [prompt.name for prompt in retrieved_prompts]
    for prompt in prompts_to_create:
        assert prompt.name in retrieved_names, f"Prompt '{prompt.name}' should be in the retrieved list"

def test_update_prompt_is_active_flag(sql_prompt_repository):
    """
    Test updating a prompt's is_active flag using SQLPromptRepository.
    """
    # Create a prompt
    domain_prompt = DomainPrompt(
        name="Update Test Prompt",
        category="Update",
        prompt_text="Original text",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_prompt = sql_prompt_repository.create_prompt(domain_prompt)
    # Update the prompt to change is_active flag to False
    created_prompt.is_active = False
    updated_prompt = sql_prompt_repository.update_prompt(created_prompt)
    assert updated_prompt.is_active == False, "Prompt is_active flag should be updated to False"

def test_get_prompt_by_id(sql_prompt_repository):
    """
    Test retrieving a prompt by its ID.
    """
    domain_prompt = DomainPrompt(
        name="GetById Test Prompt",
        category="GetById",
        prompt_text="Test prompt text for get by id",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_prompt = sql_prompt_repository.create_prompt(domain_prompt)
    retrieved_prompt = sql_prompt_repository.get_prompt_by_id(created_prompt.id)
    assert retrieved_prompt is not None, "Should retrieve prompt by id"
    assert retrieved_prompt.name == created_prompt.name, "Prompt name should match"
