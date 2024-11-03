"""
Unit tests for the command executor module.
"""
import pytest
import tempfile
from unittest.mock import Mock, patch
from autobyteus_server.workspaces.workspace_tools.command_executor import (
    CommandExecutor,
    CommandExecutionResult
)

# General Fixtures
@pytest.fixture
def temp_workspace():
    """
    Fixture providing a temporary workspace directory.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def workspace_path():
    """
    Fixture providing a fixed workspace path for testing.
    """
    return "/test/workspace/path"

# Command Executor Specific Fixtures
@pytest.fixture
def mock_bash_executor():
    """Fixture providing a mock bash executor."""
    with patch('autobyteus_server.workspaces.workspace_tools.command_executor.BashExecutor') as mock:
        executor = Mock()
        mock.return_value = executor
        yield executor

@pytest.fixture
def command_executor(mock_bash_executor):
    """Fixture providing a CommandExecutor instance with mocked bash executor."""
    return CommandExecutor("/test/workspace/path")

# Test cases for CommandExecutionResult
def test_command_execution_result_successful_creation():
    """Test creating a successful execution result."""
    result = CommandExecutionResult(success=True, message="Command executed successfully")
    assert result.success is True
    assert result.message == "Command executed successfully"

def test_command_execution_result_failed_creation():
    """Test creating a failed execution result."""
    result = CommandExecutionResult(success=False, message="Command failed")
    assert result.success is False
    assert result.message == "Command failed"

# Test cases for CommandExecutor
def test_command_executor_initialization():
    """Test proper initialization of CommandExecutor."""
    executor = CommandExecutor("/test/path")
    assert executor.workspace_root_path == "/test/path"
    assert executor.bash_executor is not None

def test_command_executor_successful_command_execution(command_executor, mock_bash_executor):
    """Test successful command execution."""
    # Arrange
    mock_bash_executor.execute.return_value = "command output"
    
    # Act
    result = command_executor.execute_command("test command")
    
    # Assert
    assert result.success is True
    assert result.message == "command output"
    mock_bash_executor.execute.assert_called_once_with(
        command="cd /test/workspace/path && test command"
    )

def test_command_executor_failed_command_execution(command_executor, mock_bash_executor):
    """Test command execution with raised exception."""
    # Arrange
    mock_bash_executor.execute.side_effect = Exception("Command failed")
    
    # Act
    result = command_executor.execute_command("test command")
    
    # Assert
    assert result.success is False
    assert "Command execution failed: Command failed" in result.message

@pytest.mark.parametrize("command,expected_full_command", [
    ("ls", "cd /test/workspace/path && ls"),
    ("pwd", "cd /test/workspace/path && pwd"),
    ("echo 'test'", "cd /test/workspace/path && echo 'test'"),
])
def test_command_executor_workspace_path_prepending(command_executor, mock_bash_executor, command, expected_full_command):
    """Test proper workspace path handling for different commands."""
    # Arrange
    mock_bash_executor.execute.return_value = "success"
    
    # Act
    command_executor.execute_command(command)
    
    # Assert
    mock_bash_executor.execute.assert_called_once_with(command=expected_full_command)

def test_command_executor_empty_command_handling(command_executor, mock_bash_executor):
    """Test handling of empty command."""
    # Arrange
    mock_bash_executor.execute.return_value = ""
    
    # Act
    result = command_executor.execute_command("")
    
    # Assert
    assert result.success is True
    assert result.message == ""
    mock_bash_executor.execute.assert_called_once_with(
        command="cd /test/workspace/path && "
    )

def test_command_executor_real_workspace_path(temp_workspace):
    """Test with a real temporary workspace directory."""
    # Arrange
    executor = CommandExecutor(temp_workspace)
    
    # Act & Assert
    assert executor.workspace_root_path == temp_workspace