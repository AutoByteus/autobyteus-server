# tests/unit_tests/automated_coding_workflow/test_automated_coding_workflow.py

import pytest
from unittest.mock import patch, MagicMock
from autobyteus_server.workflow.automated_coding_workflow import AutomatedCodingWorkflow
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus_server.workspaces.workspace import Workspace

@pytest.fixture
def mock_workspace():
    return MagicMock(spec=Workspace)

@pytest.fixture
def mock_step():
    step = MagicMock(spec=BaseStep)
    step.to_dict.return_value = {"some_key": "some_value"}
    return step

def test_automated_coding_workflow_initialization(mock_workspace):
    workflow = AutomatedCodingWorkflow(mock_workspace)
    assert workflow.workspace == mock_workspace
    assert workflow.name == "automated_coding_workflow"

@patch("autobyteus_server.workflow.automated_coding_workflow.create_llm_integration")
def test_automated_coding_workflow_initialize_steps(mock_create_llm_integration, mock_workspace, mock_step):
    mock_create_llm_integration.return_value = MagicMock()
    step_config = {
        'step1': {'step_class': MagicMock(return_value=mock_step)},
        'step2': {'step_class': MagicMock(return_value=mock_step), 'steps': {}}
    }
    
    workflow = AutomatedCodingWorkflow(mock_workspace)
    workflow._initialize_steps(step_config)
    
    assert 'step1' in workflow.steps
    assert 'step2' in workflow.steps

def test_automated_coding_workflow_to_json(mock_workspace, mock_step):
    workflow = AutomatedCodingWorkflow(mock_workspace)
    workflow.steps = {'step1': mock_step}
    result = workflow.to_json()

    expected = '{"name": "automated_coding_workflow", "steps": {"step1": {"some_key": "some_value"}}}'
    assert result == expected

def test_automated_coding_workflow_execute_valid_step(mock_workspace, mock_step):
    workflow = AutomatedCodingWorkflow(mock_workspace)
    workflow.steps = {'step1': mock_step}
    
    result = workflow.execute_step('step1')
    assert result == mock_step.execute.return_value

def test_automated_coding_workflow_execute_invalid_step(mock_workspace):
    workflow = AutomatedCodingWorkflow(mock_workspace)
    with pytest.raises(ValueError, match="Invalid step_id: step99"):
        workflow.execute_step('step99')

def test_automated_coding_workflow_start(mock_workspace):
    workflow = AutomatedCodingWorkflow(mock_workspace)
    workflow.start_workflow()
    assert workflow.status == "Started"