import pytest
import asyncio
import os
from autobyteus_server.workflow.steps.subtask_implementation.subtask_implementation_step import SubtaskImplementationStep
from autobyteus.llm.models import LLMModel
from autobyteus.workflow.workflow import Workflow

@pytest.fixture
def workflow():
    return Workflow()

@pytest.fixture
def context_file(tmp_path):
    file_content = """
def greet(name):
    return f"Hello, {name}!"

def main():
    print(greet("World"))

if __name__ == "__main__":
    main()
    """
    file_path = tmp_path / "greetings.py"
    file_path.write_text(file_content)
    return str(file_path)

@pytest.mark.asyncio
async def test_subtask_implementation_step_without_context(workflow):
    # Arrange
    step = SubtaskImplementationStep(workflow)
    requirement = "Implement a function to calculate the factorial of a number"
    llm_model = LLMModel.MISTRAL_LARGE_API  # Updated to correct model

    # Act
    conversation_id = await step.process_requirement(requirement, [], llm_model)

    # Assert
    response = await asyncio.wait_for(step.get_latest_response(conversation_id), timeout=60.0)
    
    assert response is not None
    assert "def factorial" in response
    # Cleanup
    if step.agents.get(conversation_id):
        step.stop_agent(conversation_id)

@pytest.mark.asyncio
async def test_subtask_implementation_step_with_context(workflow, context_file):
    # Arrange
    step = SubtaskImplementationStep(workflow)
    requirement = "Modify the greet function to include a time of day greeting (morning/afternoon/evening) based on the current time."
    llm_model = LLMModel.CLAUDE_3_5_SONNET_API  # Updated to correct model

    # Act
    conversation_id = await step.process_requirement(requirement, [{'path': context_file, 'type': 'text'}], llm_model)

    # Assert
    response = await asyncio.wait_for(step.get_latest_response(conversation_id), timeout=60.0)
    
    assert response is not None
    assert "def greet" in response
    # Cleanup
    if step.agents.get(conversation_id):
        step.stop_agent(conversation_id)

@pytest.mark.asyncio
async def test_subtask_implementation_step_continuation(workflow, context_file):
    # Arrange
    step = SubtaskImplementationStep(workflow)
    initial_requirement = "Implement a function to calculate the factorial of a number"
    llm_model = LLMModel.MISTRAL_LARGE_API  # Updated to correct model

    # Act
    conversation_id = await step.process_requirement(initial_requirement, [], llm_model)
    initial_response = await asyncio.wait_for(step.get_latest_response(conversation_id), timeout=60.0)
    assert initial_response is not None
    assert "def factorial" in initial_response

    # Continue the conversation
    continuation_requirement = "Optimize the factorial function using memoization."
    await step.process_requirement(continuation_requirement, [], llm_model, conversation_id=conversation_id)
    continuation_response = await asyncio.wait_for(step.get_latest_response(conversation_id), timeout=60.0)
    
    # Assert
    assert continuation_response is not None
    assert "def factorial" in continuation_response
    assert "memoization" in continuation_response
    # Cleanup
    if step.agents.get(conversation_id):
        step.stop_agent(conversation_id)

@pytest.mark.asyncio
async def test_subtask_implementation_multiple_conversations(workflow, context_file):
    # Arrange
    step = SubtaskImplementationStep(workflow)
    requirement1 = "Implement a function to calculate the factorial of a number"
    requirement2 = "Modify the greet function to include a time of day greeting (morning/afternoon/evening) based on the current time."
    llm_model1 = LLMModel.MISTRAL_LARGE_API  # Updated to correct model
    llm_model2 = LLMModel.CLAUDE_3_5_SONNET_API  # Updated to correct model

    # Act
    conversation_id1 = await step.process_requirement(requirement1, [], llm_model1)
    response1 = await asyncio.wait_for(step.get_latest_response(conversation_id1), timeout=60.0)
    conversation_id2 = await step.process_requirement(requirement2, [{'path': context_file, 'type': 'text'}], llm_model2)
    response2 = await asyncio.wait_for(step.get_latest_response(conversation_id2), timeout=60.0)
    
    # Assert
    assert response1 is not None
    assert "def factorial" in response1
    assert response2 is not None
    assert "def greet" in response2
    # Cleanup
    if step.agents.get(conversation_id1):
        step.stop_agent(conversation_id1)
    if step.agents.get(conversation_id2):
        step.stop_agent(conversation_id2)