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
    llm_model = LLMModel.MISTRAL_LARGE  # Adjust based on your available models

    # Act
    await step.process_requirement(requirement, [], llm_model)

    # Assert
    response = await asyncio.wait_for(step.get_latest_response(), timeout=60.0)
    
    assert response is not None
    # Cleanup
    if step.agent:
        step.agent.stop()

@pytest.mark.asyncio
async def test_subtask_implementation_step_with_context(workflow, context_file):
    # Arrange
    step = SubtaskImplementationStep(workflow)
    requirement = "Modify the greet function to include a time of day greeting (morning/afternoon/evening) based on the current time."
    llm_model = LLMModel.CLAUDE_3_5_SONNET  # Adjust based on your available models

    # Act
    await step.process_requirement(requirement, [context_file], llm_model)

    # Assert
    response = await asyncio.wait_for(step.get_latest_response(), timeout=60.0)
    
    assert response is not None
    # Cleanup
    if step.agent:
        step.agent.stop()
